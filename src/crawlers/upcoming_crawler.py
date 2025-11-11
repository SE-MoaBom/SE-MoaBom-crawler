from .kino_crawler import KinoCrawler


# 키노라이츠 공개 예정작 크롤러
class UpcomingCrawler(KinoCrawler):
    BASE_URL = "https://m.kinolights.com/new?tab=upcoming"

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
            name="upcoming",
            headless=headless,
            timeout=timeout,
            logger=logger,
            action_delay=action_delay,
            scroll_limit=scroll_limit,
        )
