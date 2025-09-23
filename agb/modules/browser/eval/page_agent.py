import asyncio
import logging
import os
from types import ModuleType
from typing import List, Optional, Type, Union, Literal, Dict, Any, TypeVar
import concurrent.futures

from pydantic import BaseModel
from playwright.async_api import Page, async_playwright
from agb import AGB
from agb.session_params import CreateSessionParams
from agb.modules.browser.browser import BrowserOption
from agb.model.response import SessionResult
from agb.modules.browser.browser_agent import ActOptions, ExtractOptions, ObserveOptions, ActResult, ObserveResult
from agb.modules.browser.eval.local_page_agent import LocalSession,LocalMCPClient
from agb.session import BaseSession
from agb.api.base_service import BaseService

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class PageAgent:
    def __init__(
        self, cdp_url: Optional[str] = None, enable_metrics: Optional[bool] = False
    ):
        self._metrics_enabled = enable_metrics
        self._metrics: Dict[str, int] = {}
        self.reset_metrics()
        self.session: Optional[BaseSession] = None
        self.agb: Optional[AGB] = None
        self.browser: Optional[Any] = None
        self.current_page: Optional[Page] = None
        self._worker_thread: Optional[concurrent.futures.Future] = None
        self._task_queue: Optional[asyncio.Queue] = None
        self._tool_call_queue: Optional[asyncio.Queue] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def get_test_api_key(self) -> str:
        """Get API key for testing"""
        api_key = os.environ.get("AGB_API_KEY")
        if not api_key:
            api_key = "akm-xxx"  # Replace with your test API key
            print(
                "Warning: Using default API key. Set AGB_API_KEY environment variable for testing."
            )
        return api_key

    async def initialize(self) -> None:
        try:
            run_local = os.environ.get("RUN_PAGE_TASK_LOCAL", "false") == "true"
            result = SessionResult(success=False)
            if not run_local:
                api_key = self.get_test_api_key()
                logger.info(f"api_key = {api_key}")
                from agb.config import Config
                config = Config(
                    endpoint=os.getenv("AGB_ENDPOINT", "sdk-api.agb.cloud"),
                    timeout_ms=60000
                )

                # Create AGB instance
                self.agb = AGB(api_key=api_key, cfg=config)

                # Create a session
                logger.info("Creating a new session for browser agent testing...")
                params = CreateSessionParams(
                    image_id="agb-browser-use-1",  # Specify the image ID
                )

                result = self.agb.create(params)
            else:
                result.session = LocalSession()
                result.success = True

            if result.success and result.session is not None:
                self.session = result.session
                logger.info(f"Session created with ID: {self.session.session_id}")
                if await self.session.browser.initialize_async(BrowserOption()):
                    logger.info("Browser initialized successfully")
                    endpoint_url = self.session.browser.get_endpoint_url()
                    logger.info(f"endpoint_url = {endpoint_url}")
                    if (self._worker_thread is None):
                        promise: concurrent.futures.Future[bool] = concurrent.futures.Future()
                        def thread_target():
                            async def _connect_browser():
                                success = False
                                logger.info("Start connect to browser")
                                try:
                                    async with async_playwright() as p:
                                        self._task_queue = asyncio.Queue()
                                        self._loop = asyncio.get_running_loop()
                                        self.browser = await p.chromium.connect_over_cdp(endpoint_url)
                                        logger.info("Browser connected successfully")
                                        success = True
                                        promise.set_result(success)
                                        await self._playwright_interactive_loop()
                                except Exception as e:
                                    logger.error(f"Failed to connect to browser: {e}")
                                    success = False
                                    promise.set_result(success)
                            asyncio.run(_connect_browser())
                        self._worker_thread = concurrent.futures.ThreadPoolExecutor().submit(thread_target)
                        promise.result()

                    # Get pwd
                    # Find and modify all py files under page_tasks, replace mcp_server.page_agent with agb.browser.eval.page_agent in py files
                    pwd = os.getcwd()
                    for file in os.listdir(f"{pwd}/page_tasks"):
                        if file.endswith(".py") and file != "__init__.py":
                            with open(f"{pwd}/page_tasks/{file}", "r") as f:
                                content = f.read()
                            content = content.replace("mcp_server.page_agent", "agb.browser.eval.page_agent")
                            with open(f"{pwd}/page_tasks/{file}", "w") as f:
                                f.write(content)

                    logger.info("Import page_tasks successfully")
                else:
                    logger.error("Failed to initialize browser")
                    raise RuntimeError("Failed to initialize browser")
            else:
                logger.error("Failed to create session")
                raise RuntimeError("Failed to create session")
        except Exception as e:
            logger.error(f"Error in initialize: {e}", exc_info=True)
            raise
        logger.info("Initialize browser agent successfully")

    async def _playwright_interactive_loop(self) -> None:
            """Run interactive loop."""
            while True:
                if self._task_queue is not None:
                    try:
                        task_name, arguments, future = await asyncio.wait_for(self._task_queue.get(), timeout=1.0)
                        try:
                            print(f"Execute task {task_name} with arguments {arguments}")
                            if task_name == "run_task":
                                task_module = arguments["task"]
                                logger = arguments["logger"]
                                config = arguments["config"]
                                ret = await task_module.run(self, logger, config)
                            else:
                                raise RuntimeError(f"Unknown task: {task_name}")
                            future.set_result(ret)
                        except Exception as e:
                            future.set_exception(e)
                    except asyncio.TimeoutError:
                        pass
                else:
                    await asyncio.sleep(1)

    async def _call_mcp_tool(self, tool_name: str, arguments: dict) -> Any:
        if not self.session or not self._tool_call_queue or not self._loop:
            raise RuntimeError("MCP client is not connected. Call connect() and ensure it returns True before calling callTool.")
        # Use a Future to get the result back from the interactive loop
        future: concurrent.futures.Future = concurrent.futures.Future()
        await self._tool_call_queue.put((tool_name, arguments, future))
        return future.result()

    async def _interactive_loop(self) -> None:
        """Run interactive loop."""
        while True:
            if self._tool_call_queue is not None:
                try:
                    tool_name, arguments, future = await asyncio.wait_for(self._tool_call_queue.get(), timeout=1.0)
                    try:
                        print(f"Call tool {tool_name} with arguments {arguments}")
                        if self.session is not None:
                            service = BaseService(self.session)
                            response = service._call_mcp_tool(tool_name, arguments)
                            print("MCP tool response:", response)

                            # Extract text content from response
                            if hasattr(response, 'content') and response.content:
                                for content_item in response.content:
                                    if hasattr(content_item, 'text') and content_item.text:
                                        future.set_result(content_item.text)
                                        break
                                else:
                                    # If no text content found, use the original response
                                    future.set_result(response)
                            else:
                                # Fallback to original response if no content structure
                                future.set_result(response)
                        else:
                            future.set_exception(RuntimeError("MCP client session is not initialized."))
                    except Exception as e:
                        future.set_exception(e)
                except asyncio.TimeoutError:
                    pass
            else:
                await asyncio.sleep(1)

    async def _post_task_to_pr_loop(self, task: str, arguments: dict) -> Any:
        if not self.session or not self._task_queue or not self._loop:
            raise RuntimeError("Session is not ready. Call initialize() and ensure it returns True before calling _post_task_to_pr_loop.")
        # Use a Future to get the result back from the interactive loop
        future: concurrent.futures.Future = concurrent.futures.Future()
        await self._task_queue.put((task, arguments, future))
        return future.result()

    async def get_current_page(self) -> Page:
        if self.current_page is None:
            raise RuntimeError("Current page is not available. Make sure to navigate to a page first.")
        
        cdp_session = None
        try:
            cdp_session = await self.current_page.context.new_cdp_session(self.current_page)
            #logger.info(f"get_current_page: {self.current_page}")
        finally:
            if cdp_session:
                await cdp_session.detach()
        return self.current_page

    async def run_task(self, task: ModuleType, logger: logging.Logger, config: Dict[str, Any]) -> Any:
        arguments = {
            "task": task,
            "logger": logger,
            "config": config,
        }
        return await self._post_task_to_pr_loop("run_task", arguments)

    def reset_metrics(self) -> None:
        """
        initialize metrics
        """
        self._metrics = {
            "llm_duration_s": 0,
            "llm_call_count": 0,
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
        }

    def get_metrics(self) -> Dict[str, int]:
        """
        get metrics
        """
        return self._metrics

    async def goto(
        self,
        url: str,
        context_id: Optional[int] = None,
        page_id: Optional[str] = None,
        wait_until: Optional[
            Literal["load", "domcontentloaded", "networkidle", "commit"]
        ] = "load",
        timeout_ms: Optional[int] = 180000) -> str:
        """Navigates the browser to the specified URL."""
        logger.info(f"goto {url}")
        try:
            if self.browser is None:
                raise RuntimeError("Browser is not initialized. Call initialize() first.")
            
            self.current_page = await self.browser.new_page()
            await self.current_page.goto(url, wait_until=wait_until, timeout=timeout_ms)
            return f"Successfully navigated to {url}"
        except Exception as e:
            logger.error(f"Error in goto: {e}", exc_info=True)
            return f"goto {url} failed: {str(e)}"

    async def navigate(
        self,
        url: str) -> str:
        """Navigates the browser to the specified URL."""
        logger.info(f"goto {url}")
        try:
            if self.session is None:
                raise RuntimeError("Session is not initialized. Call initialize() first.")
            
            await self.session.browser.agent.navigate_async(url)
            return f"Successfully navigated to {url}"
        except Exception as e:
            logger.error(f"Error in goto: {e}", exc_info=True)
            return f"goto {url} failed: {str(e)}"

    async def screenshot(
        self
    ) -> str:
        try:
            if self.session is None:
                raise RuntimeError("Session is not initialized. Call initialize() first.")
            
            data_url_or_error = await self.session.browser.agent.screenshot_async()
            if data_url_or_error.startswith("screenshot failed:"):
                logger.error(data_url_or_error)
                return data_url_or_error
            if not data_url_or_error.startswith("data:image/png;base64,"):
                error_msg = f"screenshot failed: Unexpected format from SDK: {data_url_or_error[:100]}"
                logger.error(error_msg)
                return error_msg
                
            base64_data = data_url_or_error.split(',', 1)[1]
            return base64_data

        except Exception as e:
            logger.error(f"Error in screenshot: {e}", exc_info=True)
            return f"screenshot failed: {str(e)}"

    async def extract(self, instruction: str, schema: Type[T], context_id: Optional[int] = None, page_id: Optional[str] = None, use_text_extract: Optional[bool] = False, dom_settle_timeout_ms: Optional[int] = 5000, use_vision: Optional[bool] = False, selector: Optional[str] = None) -> T:
        """
        Extracts structured data from the current webpage based on an instruction.

        Args:
            instruction (str): The natural language instruction for extraction.
            schema (Type[T]): The Pydantic schema for the expected output data structure.
            use_text_extract (Optional[bool]): If True, uses text-based extraction; otherwise, uses DOM-based.
            dom_settle_timeout_ms (Optional[int]): Max time to wait for DOM stability.
            use_vision (Optional[bool]): If True, uses visual (screenshot) information for extraction.
            selector (Optional[str]): Optional CSS selector to narrow down extraction area.

        Returns:
            T: An instance of the provided Pydantic schema with extracted data.
        """
        try:
            if self.session is None:
                raise RuntimeError("Session is not initialized. Call initialize() first.")
            
            options = ExtractOptions(
                instruction=instruction,
                schema=schema,
                use_text_extract=use_text_extract,
            )

            success, extracted_data = await self.session.browser.agent.extract_async(page=self.current_page, options=options)
            if not success or extracted_data is None:
                raise RuntimeError("Failed to extract data from the page")
            return extracted_data
        except Exception as e:
            logger.error(f"Error in extract: {e}", exc_info=True)
            raise

    async def observe(self, instruction: str, return_actions: bool = True, only_visible: bool = False, dom_settle_timeout_ms: Optional[int] = None, use_vision: bool = False) -> List[ObserveResult]:
        """
        Observes the current webpage to identify and describe elements.

        Args:
            instruction (Optional[str]): Natural language goal for observation.
            return_actions (bool): If True, action suggestions for observed elements are returned.
            only_visible (bool): If True, only visible elements are considered.
            dom_settle_timeout_ms (Optional[int]): Max time to wait for DOM stability.
            use_vision (bool): If True, uses visual (screenshot) information for observation.

        Returns:
            List[ObservedElement]: A list of identified and described elements.
        """
        try:
            if self.session is None:
                raise RuntimeError("Session is not initialized. Call initialize() first.")
            
            logger.info("Starting observation...")
            options = ObserveOptions(
                instruction=instruction,
                dom_settle_timeout_ms=dom_settle_timeout_ms,
            )
            success, observed_elements = await self.session.browser.agent.observe_async(page=self.current_page, options=options)
            return observed_elements
        except Exception as e:
            logger.error(f"Error in observe: {e}", exc_info=True)
            raise

    async def act(self, action_input: Union[str, ActOptions, ObserveResult], context_id: Optional[int] = None, page_id: Optional[str] = None, use_vision: bool = False) -> ActResult:
        """
        Performs an action on the current webpage, either inferred from an instruction
        or directly on an ObservedElement.

        Args:
            action_input (Union[str, ActOptions, ObservedElement]):
                - str: A natural language instruction for the action.
                - ActOptions: Action config with timeouts, DOM settle wait, and variable placeholders.
                - ObservedElement: A pre-identified element to act on directly.
            use_vision (bool): If True, uses visual (screenshot) information for action inference.

        Returns:
            ActionResult: The result of the action, indicating success or failure.
        """
        try:
            if self.session is None:
                raise RuntimeError("Session is not initialized. Call initialize() first.")
            
            logger.info(f"Attempting to execute action: {action_input}")
            if isinstance(action_input, str):
                options = ActOptions(
                    action=action_input,    
                )
                return await self.session.browser.agent.act_async(page=self.current_page, action_input=options)
            else:
                return await self.session.browser.agent.act_async(page=self.current_page, action_input=action_input)
        except Exception as e:
            logger.error(f"Error in act: {e}", exc_info=True)
            raise

    async def close(self) -> None:
        """Closes the browser session if it exists."""
        logger.info("PageAgent session closed and instance state reset.")