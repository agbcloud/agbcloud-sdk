# -*- coding: utf-8 -*-
"""
Version utilities for AGB SDK.

This module provides functions to get SDK version information and determine
if the current version is a release version.
"""

import os
import re
from typing import Optional


def get_sdk_version() -> str:
    """
    Get SDK version from installed package or pyproject.toml.

    Returns:
        str: SDK version string (e.g., "0.4.0")
    """
    # Try to get version from installed package
    try:
        from importlib.metadata import version, PackageNotFoundError
        try:
            return version("agbcloud-sdk")
        except PackageNotFoundError:
            pass
    except ImportError:
        # Python < 3.8, fallback to reading pyproject.toml
        pass

    # Fallback: read from pyproject.toml
    try:
        import tomllib
        pyproject_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pyproject.toml")
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
            return data.get("project", {}).get("version", "0.0.0")
    except Exception:
        # Final fallback
        return "invalid-version"


try:
    from agb._release import IS_RELEASE_VERSION
except ImportError:
    # If file doesn't exist (e.g. old versions), assume it's not a release
    IS_RELEASE_VERSION = False


def is_release_version() -> bool:
    """
    Check if the current SDK build is a release version.

    This determines if the version is a release version by checking the
    IS_RELEASE_VERSION flag, which is set to True during the CI/CD build process
    for official releases.

    Returns:
        bool: True if this is a release version, False otherwise
    """
    return IS_RELEASE_VERSION

