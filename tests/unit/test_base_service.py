import importlib.util
import sys
import types
import unittest
from unittest.mock import MagicMock

# Some local dev environments may not have runtime dependencies installed.
# BaseService imports `requests` but doesn't require it for this unit test.
sys.modules.setdefault("requests", types.ModuleType("requests"))

def _install_agb_stubs():
    """
    Provide minimal stubs for `agb.*` imports so this unit test can run in a local
    environment without installing all runtime deps.
    """
    if "agb" not in sys.modules:
        sys.modules["agb"] = types.ModuleType("agb")

    # agb.logger
    if "agb.logger" not in sys.modules:
        logger_mod = types.ModuleType("agb.logger")

        class _DummyLogger:
            def __getattr__(self, _name):
                return lambda *args, **kwargs: None

        def get_logger(_name: str):
            return _DummyLogger()

        logger_mod.get_logger = get_logger
        sys.modules["agb.logger"] = logger_mod

    # agb.exceptions
    if "agb.exceptions" not in sys.modules:
        exc_mod = types.ModuleType("agb.exceptions")

        class AGBError(Exception):
            pass

        exc_mod.AGBError = AGBError
        sys.modules["agb.exceptions"] = exc_mod

    # agb.model
    if "agb.model" not in sys.modules:
        model_mod = types.ModuleType("agb.model")

        class OperationResult:
            def __init__(self, request_id: str = "", success: bool = False, data=None, error_message: str = ""):
                self.request_id = request_id
                self.success = success
                self.data = data
                self.error_message = error_message

        model_mod.OperationResult = OperationResult
        sys.modules["agb.model"] = model_mod

    # agb.api.models
    if "agb.api" not in sys.modules:
        sys.modules["agb.api"] = types.ModuleType("agb.api")

    if "agb.api.models" not in sys.modules:
        models_mod = types.ModuleType("agb.api.models")

        class CallMcpToolRequest:
            def __init__(self, authorization: str, session_id: str, name: str, args: str):
                self.authorization = authorization
                self.session_id = session_id
                self.name = name
                self.args = args

            def get_params(self):
                return {}

            def get_body(self):
                return {}

        models_mod.CallMcpToolRequest = CallMcpToolRequest
        sys.modules["agb.api.models"] = models_mod


# Import these modules by file path (and with stubs) to avoid importing `agb` package
# which may pull optional runtime deps (aiohttp, loguru, etc.) in some local envs.
_BASE_DIR = __file__.rsplit("/tests/unit/", 1)[0]

def _import_by_path(module_name: str, path: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Failed to load module spec: {module_name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_install_agb_stubs()

base_service_mod = _import_by_path(
    "_agb_api_base_service",
    f"{_BASE_DIR}/agb/api/base_service.py",
)
call_resp_mod = _import_by_path(
    "_agb_api_models_call_mcp_tool_response",
    f"{_BASE_DIR}/agb/api/models/call_mcp_tool_response.py",
)

BaseService = base_service_mod.BaseService
CallMcpToolResponse = call_resp_mod.CallMcpToolResponse


class DummySession:
    def __init__(self):
        self._client = MagicMock()

    def get_api_key(self) -> str:
        return "test_api_key"

    def get_session_id(self) -> str:
        return "released_session_id"

    def get_client(self):
        return self._client


class DummyService(BaseService):
    pass


class TestBaseServiceCallMcpTool(unittest.TestCase):
    def test_call_mcp_tool_api_failure_should_return_success_false(self):
        """
        Regression: if API wrapper reports failure (success=false) but tool payload has isError=false,
        _call_mcp_tool must still return success=False.
        """
        session = DummySession()
        service = DummyService(session)

        # API layer failed (success=false), tool layer looks OK (isError=false) -> must be treated as failure.
        response = CallMcpToolResponse.from_http_response(
            {
                "status_code": 200,
                "url": "http://example/mcp",
                "headers": {},
                "success": True,
                "request_id": "req-1",
                "json": {
                    "success": False,
                    "code": "InvalidSession.NotFound",
                    "message": "Resource [Session] is not found",
                    "data": {},
                    "requestId": "req-1",
                },
            }
        )

        session.get_client().call_mcp_tool.return_value = response

        result = service._call_mcp_tool("write_file", {"path": "/tmp/a.txt", "content": "x", "mode": "overwrite"})  # MCP tool name unchanged
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "req-1")
        self.assertIn("not found", (result.error_message or "").lower())

    def test_call_mcp_tool_none_response_should_fail(self):
        session = DummySession()
        service = DummyService(session)

        session.get_client().call_mcp_tool.return_value = None
        result = service._call_mcp_tool("noop", {"x": 1})
        self.assertFalse(result.success)
        self.assertIn("returned None", result.error_message)

    def test_call_mcp_tool_unsupported_response_type_should_fail(self):
        session = DummySession()
        service = DummyService(session)

        # A plain object without is_successful should hit the unsupported response type branch
        session.get_client().call_mcp_tool.return_value = types.SimpleNamespace(request_id="rid")
        result = service._call_mcp_tool("noop", {"x": 1})
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "rid")
        self.assertIn("unsupported", (result.error_message or "").lower())

    def test_call_mcp_tool_handles_agb_error(self):
        session = DummySession()
        service = DummyService(session)

        # Raise the stubbed AGBError from agb.exceptions (installed in _install_agb_stubs)
        AGBError = sys.modules["agb.exceptions"].AGBError

        session.get_client().call_mcp_tool.side_effect = AGBError("boom")
        result = service._call_mcp_tool("noop", {"x": 1})
        self.assertFalse(result.success)
        self.assertIn("boom", result.error_message)

    def test_call_mcp_tool_handles_generic_exception(self):
        session = DummySession()
        service = DummyService(session)

        session.get_client().call_mcp_tool.side_effect = RuntimeError("oops")
        result = service._call_mcp_tool("noop", {"x": 1})
        self.assertFalse(result.success)
        self.assertIn("Failed to call MCP tool", result.error_message)


    def test_call_mcp_tool_success_should_return_success_true(self):
        session = DummySession()
        service = DummyService(session)

        response = CallMcpToolResponse.from_http_response(
            {
                "status_code": 200,
                "url": "http://example/mcp",
                "headers": {},
                "success": True,
                "request_id": "req-ok",
                "json": {
                    "success": True,
                    "code": "OK",
                    "message": "",
                    "data": {
                        "isError": False,
                        "content": [{"type": "text", "text": "ok"}],
                    },
                    "requestId": "req-ok",
                },
            }
        )

        session.get_client().call_mcp_tool.return_value = response
        result = service._call_mcp_tool("ping", {"x": 1})
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "req-ok")
        self.assertEqual(result.data, "ok")


    def test_call_mcp_tool_logging_json_dump_failure(self):
        session = DummySession()
        service = DummyService(session)

        class _BadResp:
            request_id = "rid-bad"
            # not JSON serializable (set)
            json_data = {"x": {1}}

            def is_successful(self):
                return False

            def get_error_message(self):
                return "bad"

        session.get_client().call_mcp_tool.return_value = _BadResp()
        result = service._call_mcp_tool("noop", {"x": 1})
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "rid-bad")
        self.assertIn("bad", result.error_message)
