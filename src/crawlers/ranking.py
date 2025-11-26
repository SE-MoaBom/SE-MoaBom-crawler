from .kino import KinoCrawler
from models import KinoData
import structlog
import re


class RankingCrawler(KinoCrawler):
    RANKING_URL = "https://m.kinolights.com/ranking"

    def __init__(self, logger: structlog.stdlib.BoundLogger | None = None, **kwargs):
        super().__init__(url=self.RANKING_URL, name="ranking", logger=logger, **kwargs)

    async def crawl(self) -> list[KinoData]:
        results = await super().crawl()

        for rank, data in enumerate(results, start=1):
            if data.program:
                data.program.ranking = rank

        return results

    async def _get_content_ids(self) -> list[str]:
        """랭킹 페이지 전용 ID 수집 로직"""
        await self.page.goto(self.url)
        await self.page.wait_for_load_state("networkidle", timeout=self.timeout)
        await self._scroll_page_until_end(limit=self.scroll_limit)

        selector = ".content-ranking-list .ranking-item a[href*='/title/']"
        items = await self._get_attributes(selector, "href")

        ids = []
        for item in items:
            if m := re.search(r"/title/(\d+)", item):
                ids.append(m.group(1))

        unique_ids = list(dict.fromkeys(ids))
        return unique_ids[:100]
