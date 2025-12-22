#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGB browser module test code
Tests browser initialization, configuration, and management functionality
"""

import asyncio
import os
import sys
import time

# Add project root directory to Python path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# Direct import, completely bypass __init__.py
import importlib.util
import traceback

from agb.agb import AGB
from agb.config import Config
from agb.logger import get_logger
from agb.modules.browser.browser import (
    BrowserFingerprint,
    BrowserOption,
    BrowserProxy,
    BrowserScreen,
    BrowserViewport,
)

logger = get_logger(__name__)
from agb.session_params import CreateSessionParams


def get_api_key():
    """Get API Key from environment variables"""
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        raise ValueError(
            "AGB_API_KEY environment variable not set. Please set the environment variable:\n"
            "export AGB_API_KEY=your_api_key_here"
        )
    return api_key


def test_create_session():
    """Test creating AGB session for browser testing"""

    # API key
    api_key = get_api_key()
    print(f"Using API Key: {api_key}")

    try:
        print("Initializing AGB client...")

        config = Config(
            endpoint=os.getenv("AGB_ENDPOINT", "sdk-api.agb.cloud"), timeout_ms=60000
        )

        # Create AGB instance
        agb = AGB(api_key=api_key, cfg=config)
        print(f"✅ AGB client initialized successfully")
        print(f"   Endpoint: {agb.endpoint}")
        print(f"   Timeout: {agb.timeout_ms}ms")

        print("\nCreating session...")

        params = CreateSessionParams(image_id="agb-browser-use-1")

        # Record session creation start time
        create_start_time = time.time()

        result = agb.create(params)

        # Record session creation end time
        create_end_time = time.time()
        create_duration = create_end_time - create_start_time

        print(f"⏱️  Session creation took: {create_duration:.3f} seconds")

        # Check result
        if result.success:
            print("✅ Session created successfully!")
            print(f"   Request ID: {result.request_id}")
            print(f"   Session ID: {result.session.session_id}")
            if hasattr(result.session, "resource_url") and result.session.resource_url:
                print(f"   Resource URL: {result.session.resource_url}")
            if hasattr(result.session, "image_id") and result.session.image_id:
                print(f"   Image ID: {result.session.image_id}")
        else:
            print("❌ Session creation failed!")
            print(f"   Error message: {result.error_message}")
            if result.request_id:
                print(f"   Request ID: {result.request_id}")

        return result, agb, create_duration

    except Exception as e:
        print(f"❌ Error occurred during test: {e}")
        traceback.print_exc()
        return None, None, 0


def test_browser_proxy_configuration():
    """Test BrowserProxy configuration and validation"""
    print("\n" + "=" * 60)
    print("Testing BrowserProxy Configuration")
    print("=" * 60)

    try:
        # Test custom proxy configuration
        print("1. Testing custom proxy configuration...")
        custom_proxy = BrowserProxy(
            proxy_type="custom",
            server="127.0.0.1:8080",
            username="user",
            password="pass",
        )

        proxy_map = custom_proxy.to_map()
        print(f"✅ Custom proxy created successfully!")
        print(f"   Type: {custom_proxy.type}")
        print(f"   Server: {custom_proxy.server}")
        print(f"   Username: {custom_proxy.username}")
        print(f"   Password: {custom_proxy.password}")
        print(f"   Map: {proxy_map}")

        # Test built-in proxy with polling strategy
        print("\n2. Testing built-in proxy with polling strategy...")
        builtin_polling_proxy = BrowserProxy(
            proxy_type="built-in", strategy="polling", pollsize=15
        )

        builtin_map = builtin_polling_proxy.to_map()
        print(f"✅ Built-in polling proxy created successfully!")
        print(f"   Type: {builtin_polling_proxy.type}")
        print(f"   Strategy: {builtin_polling_proxy.strategy}")
        print(f"   Pollsize: {builtin_polling_proxy.pollsize}")
        print(f"   Map: {builtin_map}")

        # Test built-in proxy with restricted strategy
        print("\n3. Testing built-in proxy with restricted strategy...")
        builtin_restricted_proxy = BrowserProxy(
            proxy_type="built-in", strategy="restricted"
        )

        restricted_map = builtin_restricted_proxy.to_map()
        print(f"✅ Built-in restricted proxy created successfully!")
        print(f"   Type: {builtin_restricted_proxy.type}")
        print(f"   Strategy: {builtin_restricted_proxy.strategy}")
        print(f"   Map: {restricted_map}")

        # Test from_map method
        print("\n4. Testing from_map method...")
        restored_proxy = BrowserProxy.from_map(proxy_map)
        print(f"✅ Proxy restored from map successfully!")
        print(f"   Restored type: {restored_proxy.type}")
        print(f"   Restored server: {restored_proxy.server}")

        # Test validation errors
        print("\n5. Testing validation errors...")
        try:
            invalid_proxy = BrowserProxy(proxy_type="invalid")
            print("❌ Should have raised ValueError for invalid proxy type")
        except ValueError as e:
            print(f"✅ Correctly caught validation error: {e}")

        try:
            custom_without_server = BrowserProxy(proxy_type="custom")
            print("❌ Should have raised ValueError for custom proxy without server")
        except ValueError as e:
            print(f"✅ Correctly caught validation error: {e}")

        try:
            builtin_without_strategy = BrowserProxy(proxy_type="built-in")
            print(
                "❌ Should have raised ValueError for built-in proxy without strategy"
            )
        except ValueError as e:
            print(f"✅ Correctly caught validation error: {e}")

        return True

    except Exception as e:
        print(f"❌ Error occurred during proxy configuration test: {e}")
        traceback.print_exc()
        return False


def test_browser_viewport_and_screen():
    """Test BrowserViewport and BrowserScreen configuration"""
    print("\n" + "=" * 60)
    print("Testing BrowserViewport and BrowserScreen")
    print("=" * 60)

    try:
        # Test BrowserViewport
        print("1. Testing BrowserViewport...")
        viewport = BrowserViewport(width=1366, height=768)
        viewport_map = viewport.to_map()

        print(f"✅ Viewport created successfully!")
        print(f"   Width: {viewport.width}")
        print(f"   Height: {viewport.height}")
        print(f"   Map: {viewport_map}")

        # Test from_map method
        restored_viewport = BrowserViewport()
        restored_viewport.from_map(viewport_map)
        print(f"✅ Viewport restored from map successfully!")
        print(f"   Restored width: {restored_viewport.width}")
        print(f"   Restored height: {restored_viewport.height}")

        # Test BrowserScreen
        print("\n2. Testing BrowserScreen...")
        screen = BrowserScreen(width=1920, height=1080)
        screen_map = screen.to_map()

        print(f"✅ Screen created successfully!")
        print(f"   Width: {screen.width}")
        print(f"   Height: {screen.height}")
        print(f"   Map: {screen_map}")

        # Test from_map method
        restored_screen = BrowserScreen()
        restored_screen.from_map(screen_map)
        print(f"✅ Screen restored from map successfully!")
        print(f"   Restored width: {restored_screen.width}")
        print(f"   Restored height: {restored_screen.height}")

        return True

    except Exception as e:
        print(f"❌ Error occurred during viewport/screen test: {e}")
        traceback.print_exc()
        return False


def test_browser_fingerprint():
    """Test BrowserFingerprint configuration"""
    print("\n" + "=" * 60)
    print("Testing BrowserFingerprint")
    print("=" * 60)

    try:
        # Test fingerprint with all options
        print("1. Testing fingerprint with all options...")
        fingerprint = BrowserFingerprint(
            devices=["desktop", "mobile"],
            operating_systems=["windows", "macos", "linux"],
            locales=["en-US", "zh-CN", "ja-JP"],
        )

        fingerprint_map = fingerprint.to_map()
        print(f"✅ Fingerprint created successfully!")
        print(f"   Devices: {fingerprint.devices}")
        print(f"   Operating Systems: {fingerprint.operating_systems}")
        print(f"   Locales: {fingerprint.locales}")
        print(f"   Map: {fingerprint_map}")

        # Test from_map method
        restored_fingerprint = BrowserFingerprint()
        restored_fingerprint.from_map(fingerprint_map)
        print(f"✅ Fingerprint restored from map successfully!")
        print(f"   Restored devices: {restored_fingerprint.devices}")
        print(f"   Restored OS: {restored_fingerprint.operating_systems}")
        print(f"   Restored locales: {restored_fingerprint.locales}")

        # Test validation errors
        print("\n2. Testing validation errors...")
        try:
            invalid_device = BrowserFingerprint(devices=["invalid_device"])
            print("❌ Should have raised ValueError for invalid device")
        except ValueError as e:
            print(f"✅ Correctly caught validation error: {e}")

        try:
            invalid_os = BrowserFingerprint(operating_systems=["invalid_os"])
            print("❌ Should have raised ValueError for invalid OS")
        except ValueError as e:
            print(f"✅ Correctly caught validation error: {e}")

        return True

    except Exception as e:
        print(f"❌ Error occurred during fingerprint test: {e}")
        traceback.print_exc()
        return False


def test_browser_option():
    """Test BrowserOption configuration"""
    print("\n" + "=" * 60)
    print("Testing BrowserOption")
    print("=" * 60)

    try:

        # Test basic browser option
        print("1. Testing basic browser option...")
        basic_option = BrowserOption(
            use_stealth=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        )

        basic_map = basic_option.to_map()
        print(f"✅ Basic option created successfully!")
        print(f"   Use Stealth: {basic_option.use_stealth}")
        print(f"   User Agent: {basic_option.user_agent}")
        print(f"   Map: {basic_map}")

        # Test complex browser option with all components
        print("\n2. Testing complex browser option...")
        proxy = BrowserProxy(proxy_type="custom", server="127.0.0.1:8080")
        viewport = BrowserViewport(width=1366, height=768)
        fingerprint = BrowserFingerprint(devices=["desktop"])

        complex_option = BrowserOption(
            use_stealth=False,
            user_agent="Custom User Agent",
            viewport=viewport,
            screen=BrowserScreen(width=1920, height=1080),
            fingerprint=fingerprint,
            proxies=[proxy],
        )

        complex_map = complex_option.to_map()
        print(f"✅ Complex option created successfully!")
        print(f"   Use Stealth: {complex_option.use_stealth}")
        print(f"   User Agent: {complex_option.user_agent}")
        print(
            f"   Viewport: {complex_option.viewport.to_map() if complex_option.viewport else None}"
        )
        print(
            f"   Screen: {complex_option.screen.to_map() if complex_option.screen else None}"
        )
        print(
            f"   Fingerprint: {complex_option.fingerprint.to_map() if complex_option.fingerprint else None}"
        )
        print(
            f"   Proxies: {[p.to_map() for p in complex_option.proxies] if complex_option.proxies else None}"
        )
        print(f"   Map: {complex_map}")

        # Test from_map method
        restored_option = BrowserOption()
        restored_option.from_map(complex_map)
        print(f"✅ Option restored from map successfully!")
        print(f"   Restored use_stealth: {restored_option.use_stealth}")
        print(f"   Restored user_agent: {restored_option.user_agent}")

        # Test validation errors
        print("\n3. Testing validation errors...")
        try:
            too_many_proxies = BrowserOption(proxies=[proxy, proxy])
            print("❌ Should have raised ValueError for too many proxies")
        except ValueError as e:
            print(f"✅ Correctly caught validation error: {e}")

        return True

    except Exception as e:
        print(f"❌ Error occurred during browser option test: {e}")
        traceback.print_exc()
        return False


def test_browser_initialization(session):
    """Test browser initialization functionality"""
    print("\n" + "=" * 60)
    print("Testing Browser Initialization")
    print("=" * 60)

    try:
        # Create browser option
        print("1. Creating browser option...")
        browser_option = BrowserOption(
            use_stealth=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            viewport=BrowserViewport(width=1366, height=768),
        )

        print(f"✅ Browser option created successfully!")
        print(f"   Use Stealth: {browser_option.use_stealth}")
        print(f"   User Agent: {browser_option.user_agent}")
        print(f"   Viewport: {browser_option.viewport.to_map()}")

        # Initialize browser
        print("\n2. Initializing browser...")
        browser = session.browser

        # Record browser initialization start time
        init_start_time = time.time()

        success = browser.initialize(browser_option)

        # Record browser initialization end time
        init_end_time = time.time()
        init_duration = init_end_time - init_start_time

        print(f"⏱️  Browser initialization took: {init_duration:.3f} seconds")

        if success:
            print("✅ Browser initialized successfully!")
            print(f"   Endpoint Router Port: {browser.endpoint_router_port}")
            print(f"   Is Initialized: {browser.is_initialized()}")
            print(
                f"   Option: {browser.get_option().to_map() if browser.get_option() else None}"
            )

            # Test endpoint URL generation
            try:
                endpoint_url = browser.get_endpoint_url()
                print(f"   Endpoint URL: {endpoint_url}")
            except Exception as e:
                print(f"❌   Endpoint URL Error: {e}")
        else:
            print("❌ Browser initialization failed!")
            print(f"   Is Initialized: {browser.is_initialized()}")

        return success, browser, init_duration

    except Exception as e:
        print(f"❌ Error occurred during browser initialization test: {e}")
        traceback.print_exc()
        return False, None, 0


async def test_browser_async_initialization(session):
    """Test async browser initialization functionality"""
    print("\n" + "=" * 60)
    print("Testing Async Browser Initialization")
    print("=" * 60)

    try:
        # Create browser option
        print("1. Creating browser option for async test...")
        browser_option = BrowserOption(
            use_stealth=False,
            user_agent="Async Test User Agent",
            viewport=BrowserViewport(width=1920, height=1080),
        )

        print(f"✅ Browser option created successfully!")
        print(f"   Use Stealth: {browser_option.use_stealth}")
        print(f"   User Agent: {browser_option.user_agent}")
        print(f"   Viewport: {browser_option.viewport.to_map()}")

        # Initialize browser asynchronously
        print("\n2. Initializing browser asynchronously...")
        browser = session.browser

        # If browser is already initialized, destroy it first to test full initialization
        if browser.is_initialized():
            logger.info("Browser is already initialized, destroying it first to test full async initialization...")
            try:
                browser.destroy()
                # Reset initialization state manually since destroy() doesn't reset it
                browser._initialized = False
                browser._option = None
                browser.endpoint_router_port = None
                logger.info("Browser destroyed, ready for async initialization")
            except Exception as e:
                logger.warning(f"Failed to destroy browser: {e}")

        # Record browser initialization start time
        init_start_time = time.time()

        success = await browser.initialize_async(browser_option)

        # Record browser initialization end time
        init_end_time = time.time()
        init_duration = init_end_time - init_start_time

        print(f"⏱️  Async browser initialization took: {init_duration:.3f} seconds")

        if success:
            print("✅ Async browser initialization successful!")
            print(f"   Endpoint Router Port: {browser.endpoint_router_port}")
            print(f"   Is Initialized: {browser.is_initialized()}")
            print(
                f"   Option: {browser.get_option().to_map() if browser.get_option() else None}"
            )

            # Test endpoint URL generation
            try:
                endpoint_url = browser.get_endpoint_url()
                print(f"   Endpoint URL: {endpoint_url}")
            except Exception as e:
                print(f"❌   Endpoint URL Error: {e}")
        else:
            print("❌ Async browser initialization failed!")
            print(f"   Is Initialized: {browser.is_initialized()}")

        return success, browser, init_duration

    except Exception as e:
        print(f"❌ Error occurred during async browser initialization test: {e}")
        traceback.print_exc()
        return False, None, 0


def test_browser_agent(session):
    """Test BrowserAgent functionality"""
    print("\n" + "=" * 60)
    print("Testing BrowserAgent")
    print("=" * 60)

    try:
        # Check if browser agent exists
        browser = session.browser
        agent = browser.agent

        print(f"✅ BrowserAgent created successfully!")
        print(f"   Agent type: {type(agent).__name__}")
        print(f"   Agent session: {agent.session is not None}")
        print(f"   Agent browser: {agent.browser is not None}")

        return True

    except Exception as e:
        print(f"❌ Error occurred during browser agent test: {e}")
        traceback.print_exc()
        return False


def test_browser_cleanup(session, agb):
    """Test browser cleanup and session deletion"""
    print("\n" + "=" * 60)
    print("Testing Browser Cleanup")
    print("=" * 60)

    try:
        # Get session info
        session_id = session.get_session_id()
        print(f"Session ID for cleanup: {session_id}")

        # Delete session
        print("\nDeleting session...")

        # Record session deletion start time
        delete_start_time = time.time()

        delete_result = agb.delete(session)

        # Record session deletion end time
        delete_end_time = time.time()
        delete_duration = delete_end_time - delete_start_time

        print(f"⏱️  Session deletion took: {delete_duration:.3f} seconds")

        if delete_result.success:
            print("✅ Session deleted successfully!")
            print(f"   Request ID: {delete_result.request_id}")
        else:
            print("❌ Session deletion failed!")
            print(f"   Error message: {delete_result.error_message}")
            if delete_result.request_id:
                print(f"   Request ID: {delete_result.request_id}")

        return delete_result.success, delete_duration

    except Exception as e:
        print(f"❌ Error occurred during cleanup test: {e}")
        traceback.print_exc()
        return False, 0


async def main():
    """Main test function"""
    print("🚀 Starting AGB Browser Module Tests")
    print("=" * 80)

    # Test results tracking
    test_results = {}

    try:
        # Test 1: Create session
        print("\n" + "=" * 60)
        print("TEST 1: Session Creation")
        print("=" * 60)

        result, agb, create_duration = test_create_session()
        if result and result.success:
            test_results["session_creation"] = True
            test_results["create_duration"] = create_duration
            session = result.session
            print("✅ Session creation test passed!")
        else:
            test_results["session_creation"] = False
            print("❌ Session creation test failed!")
            return 1

        # Test 2: Browser proxy configuration
        print("\n" + "=" * 60)
        print("TEST 2: Browser Proxy Configuration")
        print("=" * 60)

        proxy_success = test_browser_proxy_configuration()
        test_results["proxy_configuration"] = proxy_success
        if proxy_success:
            print("✅ Browser proxy configuration test passed!")
        else:
            print("❌ Browser proxy configuration test failed!")

        # Test 3: Browser viewport and screen
        print("\n" + "=" * 60)
        print("TEST 3: Browser Viewport and Screen")
        print("=" * 60)

        viewport_success = test_browser_viewport_and_screen()
        test_results["viewport_screen"] = viewport_success
        if viewport_success:
            print("✅ Browser viewport and screen test passed!")
        else:
            print("❌ Browser viewport and screen test failed!")

        # Test 4: Browser fingerprint
        print("\n" + "=" * 60)
        print("TEST 4: Browser Fingerprint")
        print("=" * 60)

        fingerprint_success = test_browser_fingerprint()
        test_results["fingerprint"] = fingerprint_success
        if fingerprint_success:
            print("✅ Browser fingerprint test passed!")
        else:
            print("❌ Browser fingerprint test failed!")

        # Test 5: Browser option
        print("\n" + "=" * 60)
        print("TEST 5: Browser Option")
        print("=" * 60)

        option_success = test_browser_option()
        test_results["browser_option"] = option_success
        if option_success:
            print("✅ Browser option test passed!")
        else:
            print("❌ Browser option test failed!")

        # Test 6: Browser initialization
        print("\n" + "=" * 60)
        print("TEST 6: Browser Initialization")
        print("=" * 60)

        init_success, browser, init_duration = test_browser_initialization(session)
        test_results["browser_initialization"] = init_success
        test_results["init_duration"] = init_duration
        if init_success:
            print("✅ Browser initialization test passed!")
        else:
            print("❌ Browser initialization test failed!")

        # Test 7: Async browser initialization
        print("\n" + "=" * 60)
        print("TEST 7: Async Browser Initialization")
        print("=" * 60)

        async_init_success, async_browser, async_init_duration = (
            await test_browser_async_initialization(session)
        )
        test_results["async_browser_initialization"] = async_init_success
        test_results["async_init_duration"] = async_init_duration
        if async_init_success:
            print("✅ Async browser initialization test passed!")
        else:
            print("❌ Async browser initialization test failed!")

        # Test 8: Browser agent
        print("\n" + "=" * 60)
        print("TEST 8: Browser Agent")
        print("=" * 60)

        agent_success = test_browser_agent(session)
        test_results["browser_agent"] = agent_success
        if agent_success:
            print("✅ Browser agent test passed!")
        else:
            print("❌ Browser agent test failed!")

        # Test 9: Cleanup
        print("\n" + "=" * 60)
        print("TEST 9: Cleanup")
        print("=" * 60)

        cleanup_success, delete_duration = test_browser_cleanup(session, agb)
        test_results["cleanup"] = cleanup_success
        test_results["delete_duration"] = delete_duration
        if cleanup_success:
            print("✅ Cleanup test passed!")
        else:
            print("❌ Cleanup test failed!")

        # Summary
        print("\n" + "=" * 80)
        print("🎯 TEST SUMMARY")
        print("=" * 80)

        # Separate test results from performance data
        test_keys = [
            k
            for k in test_results.keys()
            if k
            not in [
                "create_duration",
                "init_duration",
                "async_init_duration",
                "delete_duration",
            ]
        ]
        performance_keys = [
            "create_duration",
            "init_duration",
            "async_init_duration",
            "delete_duration",
        ]

        total_tests = len(test_keys)
        passed_tests = sum(1 for k in test_keys if test_results[k] is True)
        failed_tests = total_tests - passed_tests

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")

        # Performance summary
        print("\nPerformance Summary:")
        if "create_duration" in test_results:
            print(f"  Session Creation: {test_results['create_duration']:.3f}s")
        if "init_duration" in test_results:
            print(f"  Browser Init: {test_results['init_duration']:.3f}s")
        if "async_init_duration" in test_results:
            print(f"  Async Browser Init: {test_results['async_init_duration']:.3f}s")
        if "delete_duration" in test_results:
            print(f"  Session Deletion: {test_results['delete_duration']:.3f}s")

        # Individual test results
        print("\nIndividual Test Results:")
        for test_name in test_keys:
            result = test_results[test_name]
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name}: {status}")

        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED! Browser module is working correctly!")
            return 0
        else:
            print(
                f"\n⚠️  {failed_tests} test(s) failed. Please check the implementation."
            )
            return 1

    except Exception as e:
        print(f"❌ Critical error in main test function: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    # Run the async main function
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
