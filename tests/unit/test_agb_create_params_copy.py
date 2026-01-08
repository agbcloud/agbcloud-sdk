from __future__ import annotations

from typing import Any

import pytest

from agb.agb import AGB
from agb.context_sync import ContextSync, SyncPolicy
from agb.session_params import BrowserContext, CreateSessionParams


def test_agb_create_does_not_mutate_caller_params(monkeypatch: pytest.MonkeyPatch) -> None:
    def _fake_create_mcp_session(_request: Any) -> Any:
        raise RuntimeError("boom")

    agb = AGB(api_key="dummy")
    monkeypatch.setattr(agb.client, "create_mcp_session", _fake_create_mcp_session)

    user_context_sync = ContextSync(
        context_id="ctx-1",
        path="/tmp/data",
        policy=SyncPolicy(),
    )
    browser_context = BrowserContext(context_id="browser-ctx", auto_upload=True)

    params = CreateSessionParams(
        image_id="agb-code-space-2",
        context_syncs=[user_context_sync],
        browser_context=browser_context,
        labels={"env": "test"},
    )

    # Snapshot before calling create()
    assert params.browser_context is not None
    before_labels = dict(params.labels)
    before_image_id = params.image_id
    before_browser_context_id = params.browser_context.context_id
    before_browser_context_auto_upload = params.browser_context.auto_upload
    before_browser_context_obj_id = id(params.browser_context)
    before_context_syncs_list_id = id(params.context_syncs)
    before_context_syncs_item_ids = [id(cs) for cs in params.context_syncs]
    before_context_syncs_values = [
        (cs.context_id, cs.path, cs.policy.to_dict() if cs.policy else None)
        for cs in params.context_syncs
    ]

    # Call create() twice using the same params object
    result_1 = agb.create(params)
    result_2 = agb.create(params)
    assert result_1.success is False
    assert result_2.success is False

    # Verify caller params were not mutated
    assert params.labels == before_labels
    assert params.image_id == before_image_id

    assert params.browser_context is not None
    assert id(params.browser_context) == before_browser_context_obj_id
    assert params.browser_context.context_id == before_browser_context_id
    assert params.browser_context.auto_upload == before_browser_context_auto_upload

    assert id(params.context_syncs) == before_context_syncs_list_id
    assert [id(cs) for cs in params.context_syncs] == before_context_syncs_item_ids
    assert [
        (cs.context_id, cs.path, cs.policy.to_dict() if cs.policy else None)
        for cs in params.context_syncs
    ] == before_context_syncs_values


