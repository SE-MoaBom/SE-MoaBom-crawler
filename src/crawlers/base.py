from abc import ABC, abstractmethod
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
import structlog
from utils import config


class Crawler(ABC):
    def __init__(
        self,
        name: str,
        headless: bool | None = None,
        timeout: int | None = None,
        logger: structlog.stdlib.BoundLogger | None = None,
    ):
        self.name = name
        self.headless = headless if headless is not None else config.HEADLESS_MODE
        self.timeout = timeout if timeout is not None else config.BROWSER_TIMEOUT
        self.logger = logger

        self.playwright = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None  # 메인 페이지 (목록 수집용)

    async def start_browser(self):
        """브라우저 및 기본 컨텍스트 시작"""
        self.logger.info("Starting browser", crawler=self.name)
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)

        # 모바일 뷰포트 설정 (Pixel 5)
        self.context = await self.browser.new_context(
            **self.playwright.devices["Pixel 5"]
        )
        self.page = await self.context.new_page()
        self.page.set_default_timeout(self.timeout)

    async def close_browser(self):
        if self.browser:
            self.logger.info("Closing browser", crawler=self.name)
            await self.context.close()
            await self.browser.close()
            await self.playwright.stop()

    @abstractmethod
    async def crawl(self):
        pass

    async def run(self):
        try:
            self.logger.info("Starting crawl", crawler=self.name)
            await self.start_browser()
            data = await self.crawl()
            self.logger.info("Crawl completed", crawler=self.name, count=len(data))
            return data
        except Exception as e:
            self.logger.error("Crawl failed", crawler=self.name, error=str(e))
            return []
        finally:
            await self.close_browser()

    async def _scroll_page_until_end(self, limit: int = 100) -> None:
        """현재 페이지(self.page)를 끝까지 스크롤"""
        prev_height = await self.page.evaluate("document.body.scrollHeight")

        while limit > 0:
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            try:
                await self.page.wait_for_load_state("networkidle", timeout=5000)
            finally:
                await self.page.wait_for_timeout(1000)

            new_height = await self.page.evaluate("document.body.scrollHeight")
            if new_height == prev_height:
                break
            prev_height = new_height
            limit -= 1

    async def _get_text(self, selector: str, page: Page | None = None) -> str:
        target = page or self.page
        el = await target.query_selector(selector)
        return (await el.text_content()).strip() if el else ""

    async def _get_attribute(
        self, selector: str, attr: str, page: Page | None = None
    ) -> str | None:
        target = page or self.page
        el = await target.query_selector(selector)
        return await el.get_attribute(attr) if el else None

    async def _get_attributes(
        self, selector: str, attr: str, page: Page | None = None
    ) -> list[str]:
        target = page or self.page
        elements = await target.query_selector_all(selector)
        results = []
        for el in elements:
            val = await el.get_attribute(attr)
            if val:
                results.append(val)
        return results

    async def _click_element(self, selector: str, page: Page | None = None):
        target = page or self.page
        el = await target.query_selector(selector)
        if el:
            await el.click()
