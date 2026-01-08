#!/usr/bin/env python3
"""
Data Extraction Example

This example demonstrates structured data extraction from web pages:
- Defining data schemas with Pydantic
- Extracting product information
- Handling lists and nested data
- Text-based vs DOM-based extraction
"""

import os
import asyncio
from typing import List, Optional
from pydantic import BaseModel, Field
from agb import AGB
from agb.session_params import CreateSessionParams
from agb.modules.browser import BrowserOption, BrowserViewport, ExtractOptions
from agb.exceptions import BrowserError
from playwright.async_api import async_playwright


# Define data schemas using Pydantic
class Quote(BaseModel):
    """Schema for a single quote."""

    text: str = Field(description="The quote text")
    author: str = Field(description="The author of the quote")
    tags: List[str] = Field(description="Tags associated with the quote")


class QuotesList(BaseModel):
    """Schema for a list of quotes."""

    quotes: List[Quote] = Field(description="List of quotes on the page")


class Product(BaseModel):
    """Schema for product information."""

    name: str = Field(description="Product name")
    price: str = Field(description="Product price")
    rating: Optional[float] = Field(description="Product rating", default=None)
    availability: Optional[str] = Field(
        description="Product availability status", default=None
    )
    description: Optional[str] = Field(description="Product description", default=None)


class ProductList(BaseModel):
    """Schema for a list of products."""

    products: List[Product] = Field(description="List of products")


class NewsArticle(BaseModel):
    """Schema for news article."""

    title: str = Field(description="Article title")
    summary: str = Field(description="Article summary or excerpt")
    author: Optional[str] = Field(description="Article author", default=None)
    date: Optional[str] = Field(description="Publication date", default=None)
    url: Optional[str] = Field(description="Article URL", default=None)


class NewsList(BaseModel):
    """Schema for a list of news articles."""

    articles: List[NewsArticle] = Field(description="List of news articles")


async def main():
    """Main function demonstrating data extraction capabilities."""

    # Get API key from environment
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        raise ValueError("AGB_API_KEY environment variable not set")

    print("📊 Starting data extraction example...")

    # Initialize AGB client
    agb = AGB(api_key=api_key)
    session = None
    browser = None

    try:
        # Create a session with browser support
        print("📦 Creating browser session...")
        params = CreateSessionParams(image_id="agb-browser-use-1")
        result = agb.create(params)

        if not result.success:
            raise RuntimeError(f"Failed to create session: {result.error_message}")

        session = result.session
        print(f"✅ Session created: {session.session_id}")

        # Configure browser
        option = BrowserOption(
            use_stealth=True, viewport=BrowserViewport(width=1366, height=768)
        )

        # Initialize browser
        print("🌐 Initializing browser...")
        success = await session.browser.initialize_async(option)
        if not success:
            raise RuntimeError("Browser initialization failed")

        print("✅ Browser initialized successfully")

        # Get CDP endpoint and connect Playwright
        endpoint_url = session.browser.get_endpoint_url()

        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(endpoint_url)
            page = await browser.new_page()

            # Example 1: Extract quotes from quotes.toscrape.com
            print("\n📝 Example 1: Extracting Quotes")
            await page.goto("https://quotes.toscrape.com")

            # Extract all quotes on the page
            success, quotes_data = await session.browser.agent.extract_async(
                ExtractOptions(
                    instruction="Extract all quotes from this page including the quote text, author, and tags",
                    schema=QuotesList,
                    use_text_extract=True,
                ),
                page,
            )

            if success and quotes_data:
                print(f"  ✅ Successfully extracted {len(quotes_data.quotes)} quotes")
                for i, quote in enumerate(quotes_data.quotes[:3], 1):  # Show first 3
                    print(f"    Quote {i}:")
                    print(f"      Text: {quote.text[:100]}...")
                    print(f"      Author: {quote.author}")
                    print(f"      Tags: {', '.join(quote.tags)}")
            else:
                print("  ❌ Failed to extract quotes")

            # Example 2: Extract with CSS selector focus
            print("\n🎯 Example 2: Focused Extraction with CSS Selector")

            # Extract only the first quote using CSS selector
            success, focused_quotes = await session.browser.agent.extract_async(
                ExtractOptions(
                    instruction="Extract the quote information from the selected quote container",
                    schema=Quote,
                    selector=".quote:first-child",  # Focus on first quote only
                    use_text_extract=False,
                ),
                page,
            )

            if success and focused_quotes:
                print(f"  ✅ Successfully extracted focused quote:")
                print(f"    Text: {focused_quotes.text}")
                print(f"    Author: {focused_quotes.author}")
                print(f"    Tags: {', '.join(focused_quotes.tags)}")
            else:
                print("  ❌ Failed to extract focused quote")

            # Example 3: Extract from a different page structure
            print("\n📰 Example 3: Extracting from Different Page Structure")
            await page.goto("https://httpbin.org/html")

            # Define a simple schema for this page
            class SimplePageInfo(BaseModel):
                title: str = Field(description="Page title")
                headings: List[str] = Field(description="All headings on the page")
                links: List[str] = Field(description="All link texts on the page")

            success, page_info = await session.browser.agent.extract_async(
                ExtractOptions(
                    instruction="Extract the page title, all headings, and all link texts from this HTML page",
                    schema=SimplePageInfo,
                    use_text_extract=True,
                ),
                page,
            )

            if success and page_info:
                print(f"  ✅ Successfully extracted page information:")
                print(f"    Title: {page_info.title}")
                print(f"    Headings: {page_info.headings}")
                print(f"    Links: {page_info.links}")
            else:
                print("  ❌ Failed to extract page information")

            # Example 4: Complex nested data extraction
            print("\n🏗️ Example 4: Complex Nested Data")
            await page.goto("https://quotes.toscrape.com")

            # Define a more complex schema
            class AuthorInfo(BaseModel):
                name: str = Field(description="Author name")
                quote_count: int = Field(
                    description="Number of quotes by this author on the page"
                )

            class PageAnalysis(BaseModel):
                total_quotes: int = Field(
                    description="Total number of quotes on the page"
                )
                authors: List[AuthorInfo] = Field(
                    description="Information about authors"
                )
                unique_tags: List[str] = Field(
                    description="All unique tags used on the page"
                )
                page_title: str = Field(description="Page title")

            success, analysis = await session.browser.agent.extract_async(
                ExtractOptions(
                    instruction="Analyze this quotes page and extract comprehensive information about quotes, authors, tags, and page structure",
                    schema=PageAnalysis,
                    use_text_extract=True,
                    dom_settle_timeout_ms=2000,
                ),
                page,
            )

            if success and analysis:
                print(f"  ✅ Successfully extracted complex analysis:")
                print(f"    Page title: {analysis.page_title}")
                print(f"    Total quotes: {analysis.total_quotes}")
                print(f"    Number of authors: {len(analysis.authors)}")
                print(f"    Unique tags: {len(analysis.unique_tags)}")
                print(f"    Sample authors:")
                for author in analysis.authors[:3]:
                    print(f"      - {author.name}: {author.quote_count} quotes")
            else:
                print("  ❌ Failed to extract complex analysis")

            # Example 5: Error handling and retry with different approaches
            print("\n🔄 Example 5: Error Handling and Retry Strategies")

            # Try to extract from a page that might not have the expected structure
            await page.goto("https://example.com")

            # First attempt with strict schema
            class StrictPageInfo(BaseModel):
                title: str = Field(description="Page title")
                main_content: str = Field(description="Main content text")
                links: List[str] = Field(description="All links on the page")

            success, strict_info = await session.browser.agent.extract_async(
                ExtractOptions(
                    instruction="Extract title, main content, and all links from this page",
                    schema=StrictPageInfo,
                    use_text_extract=True,
                ),
                page,
            )

            if success and strict_info:
                print(f"  ✅ Strict extraction successful:")
                print(f"    Title: {strict_info.title}")
                print(f"    Content length: {len(strict_info.main_content)} characters")
                print(f"    Links found: {len(strict_info.links)}")
            else:
                print("  ⚠️ Strict extraction failed, trying flexible approach...")

                # Fallback with more flexible schema
                class FlexiblePageInfo(BaseModel):
                    title: Optional[str] = Field(
                        description="Page title if available", default=None
                    )
                    content: Optional[str] = Field(
                        description="Any text content found", default=None
                    )
                    has_links: bool = Field(
                        description="Whether the page has any links", default=False
                    )

                success, flexible_info = await session.browser.agent.extract_async(
                    ExtractOptions(
                        instruction="Extract any available information from this page, being flexible about what's available",
                        schema=FlexiblePageInfo,
                        use_text_extract=True,
                    ),
                    page,
                )

                if success and flexible_info:
                    print(f"  ✅ Flexible extraction successful:")
                    print(f"    Title: {flexible_info.title}")
                    print(f"    Has content: {flexible_info.content is not None}")
                    print(f"    Has links: {flexible_info.has_links}")
                else:
                    print("  ❌ Both extraction attempts failed")

            # Example 6: Batch extraction from multiple elements
            print("\n📦 Example 6: Batch Extraction")
            await page.goto("https://quotes.toscrape.com")

            # Extract each quote individually to demonstrate batch processing
            quote_containers = await page.query_selector_all(".quote")
            print(f"  Found {len(quote_containers)} quote containers")

            extracted_quotes = []
            for i, container in enumerate(quote_containers[:3]):  # Process first 3
                print(f"    Processing quote {i+1}...")

                # Focus extraction on this specific container
                container_id = f"quote-{i}"
                await container.evaluate(f"(element) => element.id = '{container_id}'")

                success, quote = await session.browser.agent.extract_async(
                    ExtractOptions(
                        instruction=f"Extract the quote information from the element with id '{container_id}'",
                        schema=Quote,
                        selector=f"#{container_id}",
                        use_text_extract=False,
                    ),
                    page,
                )

                if success and quote:
                    extracted_quotes.append(quote)
                    print(f"      ✅ Extracted: {quote.author}")
                else:
                    print(f"      ❌ Failed to extract quote {i+1}")

            print(
                f"  📊 Batch extraction completed: {len(extracted_quotes)} quotes extracted"
            )

            await browser.close()
            print("✅ Browser closed successfully")

    except BrowserError as e:
        print(f"❌ Browser error occurred: {e}")
        if browser:
            await browser.close()
    except Exception as e:
        print(f"❌ Unexpected error occurred: {e}")
        if browser:
            await browser.close()
        raise

    finally:
        # Clean up session
        if session:
            agb.delete(session)
            print("🧹 Session cleaned up")

    print("🎉 Data extraction example completed!")


async def demonstrate_advanced_extraction_patterns():
    """Demonstrate advanced extraction patterns and best practices."""

    print("\n🔬 Advanced Extraction Patterns:")
    print("  1. Use specific CSS selectors for focused extraction")
    print("  2. Define flexible schemas with Optional fields for robust extraction")
    print("  3. Implement retry logic with different extraction strategies")
    print(
        "  4. Use text-based extraction for better performance on content-heavy pages"
    )
    print("  5. Use DOM-based extraction for precise element targeting")
    print("  6. Handle nested data structures with proper Pydantic models")
    print("  7. Implement batch processing for multiple similar elements")
    print("  8. Use appropriate timeouts based on page complexity")


if __name__ == "__main__":
    asyncio.run(main())
