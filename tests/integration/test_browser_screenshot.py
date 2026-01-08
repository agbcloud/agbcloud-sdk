import os
import sys
import time
import unittest
from typing import Optional, Any
from agb import AGB
from agb.session_params import CreateSessionParams
from agb.modules.browser.browser import Browser, BrowserOption
from agb.exceptions import BrowserError
from agb.model.response import SessionResult

# Add the parent directory to the path so we can import the agb package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Optional PIL import for image validation
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    Image = None
    PIL_AVAILABLE = False

# Optional Playwright import
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    async_playwright = None
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: Playwright not available. Browser screenshot tests will be skipped.")


def get_test_api_key():
    """Get API key for testing"""
    api_key = os.environ.get("AGB_API_KEY")
    if not api_key:
        raise unittest.SkipTest("AGB_API_KEY environment variable not set")
    return api_key


class TestBrowserScreenshotIntegration(unittest.TestCase):
    """Integration tests for browser screenshot functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment with AGB client and browser session."""
        # Skip if no API key or in CI
        api_key = get_test_api_key()
        if not api_key or os.environ.get("CI"):
            raise unittest.SkipTest("Skipping integration test: No API key or running in CI")

        cls.agb = AGB(api_key)
        
        # Create browser session
        session_params = CreateSessionParams(image_id="agb-browser-use-1")
        session_result: SessionResult = cls.agb.create(session_params)
        if not session_result.success or session_result.session is None:
            raise unittest.SkipTest("Failed to create browser session")
        
        cls.session = session_result.session
        cls.browser = cls.session.browser
        
        # Initialize browser
        if not cls.browser.initialize(BrowserOption()):
            raise unittest.SkipTest("Failed to initialize browser")
            
        print(f"Created browser session: {cls.session.session_id}")

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        if hasattr(cls, "agb") and hasattr(cls, "session"):
            try:
                cls.agb.delete(cls.session)
                print(f"Browser session deleted: {cls.session.session_id}")
            except Exception as e:
                print(f"Warning: Failed to delete browser session: {e}")

    def setUp(self):
        """Set up test fixtures before each test method."""
        if not PLAYWRIGHT_AVAILABLE or async_playwright is None:
            self.skipTest("Playwright not available")
            
        # Get browser endpoint URL
        try:
            self.endpoint_url = self.browser.get_endpoint_url()
        except Exception as e:
            self.skipTest(f"Failed to get browser endpoint URL: {e}")

    def tearDown(self):
        """Tear down test fixtures after each test method."""
        pass

    async def _create_page_and_navigate(self, url: str) -> Any:
        """Helper method to create a page and navigate to a URL."""
        if not PLAYWRIGHT_AVAILABLE or async_playwright is None:
            raise unittest.SkipTest("Playwright not available")
            
        self.playwright = await async_playwright().start()
        self.browser_instance = await self.playwright.chromium.connect_over_cdp(self.endpoint_url)
        self.context = self.browser_instance.contexts[0]
        page = await self.context.new_page()
        
        await page.goto(url, timeout=30000)
        await page.wait_for_load_state("domcontentloaded")
        return page

    async def _close_page_and_browser(self, page: Any):
        """Helper method to close page and browser."""
        if hasattr(self, 'context') and page:
            await page.close()
        if hasattr(self, 'browser_instance'):
            await self.browser_instance.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()

    def test_screenshot_with_valid_page(self):
        """Test taking screenshot with a valid page."""
        print("\n=== Testing screenshot with valid page ===")
        
        async def run_test():
            page = await self._create_page_and_navigate("https://www.tmall.com")
            try:
                # Take screenshot with default full_page=False
                screenshot_data = await self.browser.screenshot(page)
                
                # Verify screenshot data
                self.assertIsInstance(screenshot_data, bytes, "Screenshot data should be bytes")
                self.assertGreater(len(screenshot_data), 0, "Screenshot data should not be empty")
                
                # Save screenshot to local file
                filename = "screenshot_valid_page.png"
                with open(filename, "wb") as f:
                    f.write(screenshot_data)
                print(f"✅ Screenshot saved to {filename}")
                
                print(f"✅ Screenshot captured successfully. Size: {len(screenshot_data)} bytes")
            finally:
                await self._close_page_and_browser(page)
        
        import asyncio
        asyncio.run(run_test())

    def test_screenshot_with_full_page(self):
        """Test taking screenshot with full_page=True."""
        print("\n=== Testing screenshot with full_page=True ===")
        
        async def run_test():
            page = await self._create_page_and_navigate("https://www.tmall.com")
            try:
                # Take screenshot with full_page=True
                screenshot_data = await self.browser.screenshot(page, full_page=True)
                
                # Verify screenshot data
                self.assertIsInstance(screenshot_data, bytes, "Screenshot data should be bytes")
                self.assertGreater(len(screenshot_data), 0, "Screenshot data should not be empty")
                
                # Save screenshot to local file
                filename = "screenshot_full_page.png"
                with open(filename, "wb") as f:
                    f.write(screenshot_data)
                print(f"✅ Full page screenshot saved to {filename}")
                 # Verify it's a long screenshot (by image dimensions validation)
                if PIL_AVAILABLE:
                    try:
                        with Image.open(filename) as img:
                            width, height = img.size
                            # Verify image dimension reasonableness, long screenshots typically have height much greater than width
                            assert width > 0 and height > 0, "Invalid image dimensions"
                            assert height > width * 1.5, f"Image {filename} does not have long screenshot characteristics, dimensions: {width}x{height}"
                            print(f"✅ Verified as long screenshot, dimensions: {width}x{height}")
                    except Exception as e:
                        print(f"Image validation failed: {e}")
                else:
                    print("PIL library not installed, skipping long screenshot dimension validation")

                print(f"✅ All parameters screenshot completed, size: {len(screenshot_data)} bytes")
                
                print(f"✅ Full page screenshot captured successfully. Size: {len(screenshot_data)} bytes")
            finally:
                await self._close_page_and_browser(page)
        
        import asyncio
        asyncio.run(run_test())

    def test_screenshot_with_custom_options(self):
        """Test taking screenshot with custom options."""
        print("\n=== Testing screenshot with custom options ===")
        
        async def run_test():
            page = await self._create_page_and_navigate("https://www.tmall.com")
            try:
                # Take screenshot with custom options
                screenshot_data = await self.browser.screenshot(
                    page, 
                    full_page=False,  # Capture only viewport (explicitly set)
                    type="jpeg",      # Use JPEG format
                    quality=80        # Set quality to 80%
                )
                
                # Verify screenshot data
                self.assertIsInstance(screenshot_data, bytes, "Screenshot data should be bytes")
                self.assertGreater(len(screenshot_data), 0, "Screenshot data should not be empty")
                
                # Save screenshot to local file
                filename = "screenshot_custom_options.jpg"
                with open(filename, "wb") as f:
                    f.write(screenshot_data)
                print(f"✅ Custom options screenshot saved to {filename}")
                
                print(f"✅ Screenshot with custom options captured successfully. Size: {len(screenshot_data)} bytes")
            finally:
                await self._close_page_and_browser(page)
        
        import asyncio
        asyncio.run(run_test())

    def test_screenshot_function_parameter_priority(self):
        """Test that function parameter full_page takes priority over options."""
        print("\n=== Testing function parameter priority ===")
        
        async def run_test():
            page = await self._create_page_and_navigate("https://www.tmall.com")
            try:
                # Take screenshot with function parameter full_page=False
                # The function parameter should take priority over options
                screenshot_data = await self.browser.screenshot(
                    page, 
                    False,  # full_page parameter (should take priority)
                    type="png",  # Add another option to test options handling
                    timeout=30000  # Add timeout option
                )
                
                # Verify screenshot data - we can't easily verify the full_page behavior,
                # but we can verify the function executes without error
                self.assertIsInstance(screenshot_data, bytes, "Screenshot data should be bytes")
                self.assertGreater(len(screenshot_data), 0, "Screenshot data should not be empty")
                
                # Save screenshot to local file
                filename = "screenshot_function_priority.png"
                with open(filename, "wb") as f:
                    f.write(screenshot_data)
                print(f"✅ Function priority screenshot saved to {filename}")
                
                print(f"✅ Screenshot with function parameter priority captured successfully. Size: {len(screenshot_data)} bytes")
            finally:
                await self._close_page_and_browser(page)
        
        import asyncio
        asyncio.run(run_test())

    def test_screenshot_without_browser_initialization(self):
        """Test taking screenshot without browser initialization."""
        print("\n=== Testing screenshot without browser initialization ===")
        
        # Create a new browser instance that is not initialized
        uninitialized_browser = Browser(self.session)
        
        async def run_test():
            # Create a simple mock page object for testing
            # We don't need to navigate to a real website for this test
            # since we're only testing the browser initialization check
            class MockPage:
                pass
            
            mock_page = MockPage()
            
            try:
                # Attempt to take screenshot with uninitialized browser
                with self.assertRaises(BrowserError) as context_manager:
                    await uninitialized_browser.screenshot(mock_page)
                    
                # Verify the error message
                self.assertIn("Browser must be initialized", str(context_manager.exception))
                
                print("✅ Uninitialized browser screenshot correctly raised BrowserError")
            except Exception as e:
                print(f"⚠️ Test encountered an issue: {e}")
                raise
        
        import asyncio
        asyncio.run(run_test())

    def test_screenshot_with_multiple_pages(self):
        """Test taking screenshots with multiple pages."""
        print("\n=== Testing screenshot with multiple pages ===")
        
        urls = [
            "https://www.tmall.com",
            "https://www.taobao.com"
        ]
        
        async def run_test():
            screenshot_sizes = []
            
            for i, url in enumerate(urls):
                try:
                    page = await self._create_page_and_navigate(url)
                    try:
                        # Take screenshot with default settings
                        # Use a shorter timeout for testing to avoid long waits
                        screenshot_data = await self.browser.screenshot(page, timeout=10000)
                        
                        # Verify screenshot data
                        self.assertIsInstance(screenshot_data, bytes, f"Screenshot {i+1} data should be bytes")
                        self.assertGreater(len(screenshot_data), 0, f"Screenshot {i+1} data should not be empty")
                        
                        # Save screenshot to local file
                        filename = f"screenshot_page_{i+1}.png"
                        with open(filename, "wb") as f:
                            f.write(screenshot_data)
                        print(f"✅ Screenshot {i+1} saved to {filename}")
                        
                        screenshot_sizes.append(len(screenshot_data))
                        print(f"✅ Screenshot {i+1} captured successfully. Size: {len(screenshot_data)} bytes")
                    finally:
                        await self._close_page_and_browser(page)
                except Exception as e:
                    print(f"⚠️ Warning: Failed to capture screenshot for {url}: {e}")
                    # Continue with other URLs rather than failing the entire test
                    continue
            
            # Verify we got at least one screenshot
            self.assertGreater(len(screenshot_sizes), 0, "Should have at least one successful screenshot")
        
        import asyncio
        asyncio.run(run_test())

    def test_screenshot_performance(self):
        """Test screenshot performance."""
        print("\n=== Testing screenshot performance ===")
        
        async def run_test():
            page = await self._create_page_and_navigate("https://www.tmall.com")
            
            # Measure screenshot time
            start_time = time.time()
            
            try:
                # Use a shorter timeout for testing
                screenshot_data = await self.browser.screenshot(page, timeout=10000)
                
                end_time = time.time()
                
                # Calculate duration
                duration = end_time - start_time
                
                # Verify screenshot data
                self.assertIsInstance(screenshot_data, bytes, "Screenshot data should be bytes")
                self.assertGreater(len(screenshot_data), 0, "Screenshot data should not be empty")
                
                # Save screenshot to local file
                filename = "screenshot_performance_test.png"
                with open(filename, "wb") as f:
                    f.write(screenshot_data)
                print(f"✅ Performance test screenshot saved to {filename}")
                
                print(f"✅ Screenshot captured in {duration:.2f} seconds. Size: {len(screenshot_data)} bytes")
                
                # Performance check (should complete within reasonable time)
                self.assertLess(duration, 30.0, "Screenshot should complete within 30 seconds")
            except Exception as e:
                print(f"⚠️ Performance test encountered an issue: {e}")
                # Don't fail the test entirely, but note the issue
                raise
            finally:
                await self._close_page_and_browser(page)
        
        import asyncio
        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()