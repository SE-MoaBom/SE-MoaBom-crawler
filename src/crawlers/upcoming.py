from .kino import KinoCrawler
import structlog


# 키노라이츠 공개 예정작 크롤러
class UpcomingCrawler(KinoCrawler):
    BASE_URL = "https://m.kinolights.com/new?tab=upcoming"

    def __init__(self, logger: structlog.stdlib.BoundLogger | None = None, **kwargs):
        super().__init__(url=self.BASE_URL, name="upcoming", logger=logger, **kwargs)
