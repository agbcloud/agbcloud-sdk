import asyncio
import os
import sys
import time

# Add project root directory to Python path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from agb.agb import AGB
from agb.session_params import CreateSessionParams
from agb.modules.browser.browser import BrowserOption, BrowserViewport
from agb.logger import get_logger

logger = get_logger(__name__)


def test_create_session():
    """创建测试会话"""
    print("=" * 60)
    print("Creating Session for Async Browser Initialization Test")
    print("=" * 60)

    api_key = os.environ.get("AGB_API_KEY")
    if not api_key:
        print("❌ Error: AGB_API_KEY environment variable not set")
        sys.exit(1)

    agb = AGB(api_key=api_key)
    print("✅ AGB client initialized")

    # Create session
    print("\nCreating session...")
    create_start_time = time.time()

    params = CreateSessionParams(image_id="agb-browser-use-1")
    result = agb.create(params)

    create_end_time = time.time()
    create_duration = create_end_time - create_start_time

    print(f"⏱️  Session creation took: {create_duration:.3f} seconds")

    if result.success and result.session:
        print("✅ Session created successfully!")
        print(f"   Session ID: {result.session.session_id}")
        return result, agb, create_duration
    else:
        print("❌ Session creation failed!")
        print(f"   Error: {result.error_message if result else 'Unknown error'}")
        sys.exit(1)


async def test_browser_async_initialization(session):
    """测试异步浏览器初始化功能"""
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
        import traceback
        traceback.print_exc()
        return False, None, 0


async def main():
    """主测试函数"""
    print("🚀 Starting Async Browser Initialization Test Only")
    print("=" * 80)

    try:
        # Step 1: Create session
        result, agb, create_duration = test_create_session()
        session = result.session

        # Step 2: Run async browser initialization test
        async_init_success, async_browser, async_init_duration = (
            await test_browser_async_initialization(session)
        )

        # Step 3: Cleanup
        print("\n" + "=" * 60)
        print("Cleanup")
        print("=" * 60)

        print("Deleting session...")
        delete_result = agb.delete(session)
        if delete_result.success:
            print("✅ Session deleted successfully!")
        else:
            print(f"❌ Session deletion failed: {delete_result.error_message}")

        # Summary
        print("\n" + "=" * 80)
        print("🎯 TEST SUMMARY")
        print("=" * 80)

        if async_init_success:
            print("✅ Async browser initialization test PASSED!")
            print(f"   Session Creation: {create_duration:.3f}s")
            print(f"   Async Browser Init: {async_init_duration:.3f}s")
            return 0
        else:
            print("❌ Async browser initialization test FAILED!")
            return 1

    except Exception as e:
        print(f"❌ Critical error in test: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    # Run the async main function
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
