from .kino import KinoCrawler
import structlog


# 키노라이츠 종료 예정작 크롤러
class ExpiredCrawler(KinoCrawler):
    BASE_URL = "https://m.kinolights.com/new?tab=expired"

    def __init__(
        self,
        headless: bool = True,
        timeout: int = 30000,
        logger: structlog.stdlib.BoundLogger | None = None,
        action_delay: int = 300,
        scroll_limit: int = 100,
    ):
        super().__init__(
            url=self.BASE_URL,
            name="expired",
            headless=headless,
            timeout=timeout,
            logger=logger,
            action_delay=action_delay,
            scroll_limit=scroll_limit,
        )
