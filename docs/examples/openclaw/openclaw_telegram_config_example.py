"""
Moltbot on AGB — Telegram Plugin Configuration Example

This script demonstrates an end-to-end workflow for provisioning a cloud session
with Moltbot preinstalled, configuring the Telegram channel and optional model
overrides, then opening the web console and cleaning up on exit.

Workflow
--------
1. Create an AGB session.
2. Optionally replace the Moltbot "models" section from a local JSON file.
3. Enable and configure Telegram when TELEGRAM_BOT_TOKEN is set.
4. Restart the Moltbot gateway and launch the in-session browser to the console URL.
5. Wait for user confirmation (Ctrl+C), then delete the session.

Prerequisites
-------------
- Python 3.10+
- AGB SDK installed: pip install agb
- Valid AGB API key

Long-running sessions
---------------------
If you need the sandbox to run for a long time, set ``policy_id`` to
``"longDuration-policy"`` when creating the session. Otherwise the session
may be released after a few minutes.

Telegram setup
--------------
If you use the Telegram channel, follow the official Telegram Bot API guide first:
create a bot, then set TELEGRAM_BOT_TOKEN. See: https://docs.openclaw.ai/channels/telegram

Environment Variables
--------------------
Required:
  AGB_API_KEY         API key for AGB.

Optional (channels and models):
  BAILIAN_API_KEY         Bailian provider API key; included in config when set.
  TELEGRAM_BOT_TOKEN      Enables and configures the Telegram plugin when set.
  MOLTBOT_MODELS_JSON     Path to a local JSON file with a "models" key; the
                          session's Moltbot config "models" section is replaced
                          with this content.
  MOLTBOT_CONFIG_PATH     Path to Moltbot config inside the session (default:
                          /home/wuying/.moltbot/moltbot.json).
  MOLTBOT_BAILIAN_BASE_URL  Bailian/DashScope API base URL in session config when
                            not using MOLTBOT_MODELS_JSON (default: overseas endpoint).

Usage
-----
  export AGB_API_KEY=your-api-key
  export BAILIAN_API_KEY=your-bailian-api-key
  export TELEGRAM_BOT_TOKEN=your-telegram-bot-token
  python openclaw_telegram_config_example.py
"""

import json
import os
import sys
from typing import Any, Dict, Optional

from agb import AGB
from agb.session import Session
from agb.session_params import CreateSessionParams


# -----------------------------------------------------------------------------
# Configuration constants
# -----------------------------------------------------------------------------

# Session image and in-session console.
IMAGE_ID = "moltbot-linux-ubuntu-2204"
CONSOLE_URL = "http://127.0.0.1:18789"

# Moltbot config path inside the session sandbox. Override via MOLTBOT_CONFIG_PATH.
DEFAULT_MOLTBOT_CONFIG_PATH = "/home/wuying/.moltbot/moltbot.json"
MOLTBOT_CONFIG_PATH = os.environ.get("MOLTBOT_CONFIG_PATH", DEFAULT_MOLTBOT_CONFIG_PATH)

# Default Bailian/DashScope base URL for overseas (international) region. Override via
# MOLTBOT_BAILIAN_BASE_URL if you use a different endpoint. No secrets here—only the
# public API base URL.
DEFAULT_BAILIAN_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

# Request timeout for command execution (milliseconds).
COMMAND_TIMEOUT_MS = 30000


# -----------------------------------------------------------------------------
# Environment helpers
# -----------------------------------------------------------------------------


def _require_env(name: str) -> str:
    """Read a required environment variable; exit with code 1 if missing or empty."""
    value = os.environ.get(name)
    if not value or not value.strip():
        print(f"Error: Required environment variable {name!r} is not set or empty.", file=sys.stderr)
        sys.exit(1)
    return value.strip()


def _get_optional_env(name: str) -> Optional[str]:
    """Read an optional environment variable; return None if unset or empty."""
    value = os.environ.get(name)
    if not value or not value.strip():
        return None
    return value.strip()


# -----------------------------------------------------------------------------
# Session command execution
# -----------------------------------------------------------------------------


def execute_command(
    session: Session,
    command: str,
    timeout_ms: int = COMMAND_TIMEOUT_MS,
) -> None:
    """
    Execute a shell command in the session and print the result.

    Args:
        session: The AGB session.
        command: The shell command to run.
        timeout_ms: Timeout in milliseconds.

    Exits:
        Prints command output on success; prints error to stderr on failure.
    """
    print(f"\nExecuting: {command}")
    result = session.command.execute(command, timeout_ms=timeout_ms)
    if result.success:
        if result.output and result.output.strip():
            print(result.output)
    else:
        print(
            f"Command failed: {result.error_message or 'Unknown error'}",
            file=sys.stderr,
        )


# -----------------------------------------------------------------------------
# Moltbot config: read/write "models" section in session sandbox
# -----------------------------------------------------------------------------


def read_moltbot_config(session: Session, path: str) -> Optional[Dict[str, Any]]:
    """
    Read and parse the Moltbot config JSON from the session filesystem.

    Args:
        session: The AGB session.
        path: Path to the config file inside the session (e.g. MOLTBOT_CONFIG_PATH).

    Returns:
        Parsed config as a dict, or None on read or parse error.
    """
    result = session.file.read(path)
    if not result.success:
        print(
            f"Failed to read Moltbot config at {path}: {result.error_message}",
            file=sys.stderr,
        )
        return None
    try:
        return json.loads(result.content)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in Moltbot config: {e}", file=sys.stderr)
        return None


def write_moltbot_config(
    session: Session,
    path: str,
    data: Dict[str, Any],
) -> bool:
    """
    Write the Moltbot config JSON back to the session filesystem.

    Args:
        session: The AGB session.
        path: Path to the config file inside the session.
        data: Full config dict to write (typically after modifying "models").

    Returns:
        True if write succeeded, False otherwise.
    """
    content = json.dumps(data, indent=4, ensure_ascii=False)
    result = session.file.write(path, content, mode="overwrite")
    if not result.success:
        print(
            f"Failed to write Moltbot config to {path}: {result.error_message}",
            file=sys.stderr,
        )
        return False
    return True


def replace_models_section(
    config: Dict[str, Any],
    new_models: Dict[str, Any],
) -> None:
    """Replace the top-level \"models\" key in config; other keys are unchanged."""
    config["models"] = new_models


# -----------------------------------------------------------------------------
# User interaction: wait for Ctrl+Q before releasing session
# -----------------------------------------------------------------------------


def wait_for_ctrl_c() -> None:
    """
    Block until the user presses Ctrl+C (or Enter as fallback).

    Prompts the user to press Ctrl+C in the terminal to continue; then the
    script will release the session. On non-TTY or errors, falls back to
    waiting for Enter.
    """
    print("")
    print("Cloud desktop is ready. Open the Cloud Desktop URL above in your browser.")
    print("When finished, press Ctrl+C in this terminal to release the session.")
    try:
        if not sys.stdin.isatty():
            while True:
                ch = sys.stdin.read(1)
                if not ch:
                    raise EOFError("stdin closed before hotkey was received")
                if ch == "\x03":
                    break
            return

        if os.name == "nt":
            import msvcrt

            while True:
                ch = msvcrt.getwch()
                if ch == "\x03":
                    break
            return

        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch == "\x03":
                    break
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except Exception:
        print("Hotkey detection unavailable; press Enter to continue and release the session.")
        try:
            input("Press Enter to continue...")
        except EOFError:
            return


# -----------------------------------------------------------------------------
# Main workflow
# -----------------------------------------------------------------------------


def main() -> None:
    api_key = _require_env("AGB_API_KEY")
    bailian_api_key = _get_optional_env("BAILIAN_API_KEY")
    telegram_bot_token = _get_optional_env("TELEGRAM_BOT_TOKEN")
    moltbot_models_json = _get_optional_env("MOLTBOT_MODELS_JSON")

    agb_client = AGB(api_key=api_key)
    session: Optional[Session] = None

    try:
        # --- Step 1: Create session ---
        # Use policy_id="longDuration-policy" for long-running sandbox; otherwise
        # the session may be released after a few minutes.
        print(f"Creating session (image: {IMAGE_ID})...")
        params = CreateSessionParams(
            image_id=IMAGE_ID,
            policy_id="longDuration-policy",
        )
        session_result = agb_client.create(params)

        if not session_result.success or not session_result.session:
            print(
                f"Failed to create session: {session_result.error_message or 'Unknown error'}",
                file=sys.stderr,
            )
            wait_for_ctrl_c()
            return

        session = session_result.session
        assert session is not None
        print(f"Session created. Session ID: {session.session_id}")

        # --- Step 2: Optional — replace "models" section from local JSON ---
        if moltbot_models_json and os.path.isfile(moltbot_models_json):
            print(f"\nApplying models section from local file: {moltbot_models_json}")
            config = read_moltbot_config(session, MOLTBOT_CONFIG_PATH)
            if config is not None:
                with open(moltbot_models_json, encoding="utf-8") as f:
                    local_data = json.load(f)
                if "models" in local_data:
                    replace_models_section(config, local_data["models"])
                    if write_moltbot_config(session, MOLTBOT_CONFIG_PATH, config):
                        print("Models section updated successfully.")
                else:
                    print(
                        f"Local file has no 'models' key: {moltbot_models_json}",
                        file=sys.stderr,
                    )
        else:
            # No local models JSON: set bailian baseUrl in sandbox config (from env or default).
            config = read_moltbot_config(session, MOLTBOT_CONFIG_PATH)
            if config is not None:
                bailian_base_url = _get_optional_env("MOLTBOT_BAILIAN_BASE_URL") or DEFAULT_BAILIAN_BASE_URL
                providers = config.setdefault("models", {}).setdefault("providers", {})
                bailian = providers.setdefault("bailian", {})
                bailian["baseUrl"] = bailian_base_url
                if write_moltbot_config(session, MOLTBOT_CONFIG_PATH, config):
                    print(f"\nModels section: bailian.baseUrl set to {bailian_base_url}")

        # --- Step 3: Enable plugins and set channel config (when env vars are set) ---
        enable_parts: list[str] = []
        config_set_parts: list[str] = []

        if bailian_api_key is not None:
            config_set_parts.append(
                f"moltbot config set models.providers.bailian.apiKey {bailian_api_key}"
            )
        if telegram_bot_token is not None:
            enable_parts.append("moltbot plugins enable telegram")
            config_set_parts.append(
                f'moltbot config set channels.telegram.botToken "{telegram_bot_token}"'
            )
            config_set_parts.append(
                f'moltbot config set channels.telegram.groupPolicy "open"'
            )

        enable_plugins = " && ".join(enable_parts) if enable_parts else ""
        config_parts_list: list[str] = []
        if enable_plugins:
            config_parts_list.append(enable_plugins)
        config_parts_list.extend(config_set_parts)

        if config_parts_list:
            print("\nConfiguring Moltbot (plugins and config)...")
            execute_command(
                session,
                " && ".join(config_parts_list),
                timeout_ms=COMMAND_TIMEOUT_MS,
            )
            print("\nRestarting Moltbot gateway...")
            execute_command(session, "moltbot gateway restart", timeout_ms=COMMAND_TIMEOUT_MS)
        else:
            print(
                "\nNo channel credentials set (TELEGRAM_BOT_TOKEN). "
                "Skipping Moltbot plugin configuration.",
            )

        # --- Step 4: Launch in-session browser to console URL ---
        execute_command(
            session,
            f"sleep 5 && nohup firefox {CONSOLE_URL} > /dev/null 2>&1 &",
            timeout_ms=COMMAND_TIMEOUT_MS,
        )

        # --- Step 5: Output cloud desktop URL and wait for user ---
        print("\n--- Cloud Desktop ---")
        resource_url = (getattr(session, "resource_url", "") or "").strip()
        if resource_url:
            print(f"URL: {resource_url}")
        else:
            print("Resource URL is not available for this session.")

        wait_for_ctrl_c()

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        raise
    finally:
        if session is not None:
            print("\nReleasing session...")
            agb_client.delete(session)
            print("Session released.")


if __name__ == "__main__":
    main()
