from abc import ABC, abstractmethod
from playwright.async_api import async_playwright, Browser, Page
from models import KinoData
import structlog


class Crawler(ABC):
    def __init__(
        self,
        name: str,
        headless: bool = True,
        timeout: int = 30000,
        logger: structlog.stdlib.BoundLogger | None = None,
    ):
        """
        Initialize the crawler.

        Args:
            platform: Platform enum
            headless: Run browser in headless mode
            timeout: Browser timeout in milliseconds
            logger: Structlog logger instance
        """
        self.platform_name = name
        self.headless = headless
        self.timeout = timeout
        self.logger = logger or structlog.get_logger()
        self.browser: Browser | None = None
        self.page: Page | None = None
        self.playwright = None

    async def start_browser(self):
        """Start the browser instance."""
        self.logger.info("Starting browser", crawler=self.platform_name)
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)

        context = await self.browser.new_context(**self.playwright.devices["Pixel 5"])
        self.page = await context.new_page()
        self.page.set_default_timeout(self.timeout)

    async def close_browser(self):
        """Close the browser instance."""
        if self.browser:
            self.logger.info("Closing browser", crawler=self.platform_name)
            await self.browser.close()
            await self.playwright.stop()

    @abstractmethod
    async def crawl(self) -> list[KinoData]:
        """
        Crawl the platform and return content information.

        Returns:
            list of KinoData instances containing content information
        """
        pass

    async def run(self) -> list[KinoData]:
        """
        Run the crawler with error handling.

        Returns:
            list of crawled content data
        """
        try:
            self.logger.info("Starting crawl", crawler=self.platform_name)
            await self.start_browser()

            data = await self.crawl()
            self.logger.info(
                "Crawl completed successfully",
                crawler=self.platform_name,
                items_count=len(data),
            )
            return data
        except Exception as e:
            self.logger.error(
                "Crawl failed", crawler=self.platform_name, error=str(e), exc_info=True
            )
            return []
        finally:
            await self.close_browser()

    async def _scroll_page_until_end(self, limit: int = 100) -> None:
        previous_height = await self.page.evaluate("document.body.scrollHeight")

        while limit > 0:
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self.page.wait_for_timeout(1000)

            new_height = await self.page.evaluate("document.body.scrollHeight")
            if new_height == previous_height:
                break
            previous_height = new_height
            limit -= 1

    async def _get_text(self, selector: str) -> str:
        element = await self.page.query_selector(selector)
        if element:
            text = await element.text_content()
            return text.strip() if text else ""
        return ""

    async def _get_attribute(self, selector: str, attribute: str) -> str | None:
        element = await self.page.query_selector(selector)
        if element:
            attr_value = await element.get_attribute(attribute)
            return attr_value
        return None

    async def _get_texts(self, selector: str) -> list[str]:
        elements = await self.page.query_selector_all(selector)
        texts = []
        for element in elements:
            text = await element.text_content()
            if text:
                texts.append(text.strip())
        return texts

    async def _get_attributes(self, selector: str, attribute: str) -> list[str]:
        elements = await self.page.query_selector_all(selector)
        attrs = []
        for element in elements:
            attr_value = await element.get_attribute(attribute)
            if attr_value:
                attrs.append(attr_value)
        return attrs

    async def _click_element(self, selector: str):
        element = await self.page.query_selector(selector)
        if element:
            await element.click()
