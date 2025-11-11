from .kino_crawler import KinoCrawler


# 키노라이츠 탐색탭 크롤러
class ExploreCrawler(KinoCrawler):
    BASE_URL = "https://m.kinolights.com/discover/explore?hideBack=true"

    def __init__(
        self,
        headless: bool = True,
        timeout: int = 30000,
        logger=None,
        action_delay: int = 300,
        scroll_limit: int = 100,
    ):
        super().__init__(
            url=self.BASE_URL,
            name="explore",
            headless=headless,
            timeout=timeout,
            logger=logger,
            action_delay=action_delay,
            scroll_limit=scroll_limit,
        )

    async def _before_crawl(self):
        await self._click_element("button.slide__chip")  # 구매/대여 제외
