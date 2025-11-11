import re
from .crawler import Crawler
from models import KinoData, Program, Availability
from datetime import datetime


# 키노라이츠 크롤러
class KinoCrawler(Crawler):
    TITLE_URL = "https://m.kinolights.com/title/"

    def __init__(
        self,
        url: str,
        name: str,
        headless: bool = True,
        timeout: int = 30000,
        logger=None,
        action_delay: int = 300,
        scroll_limit: int = 100,
    ):
        super().__init__(
            name=f"kinolights-{name}",
            headless=headless,
            timeout=timeout,
            logger=logger,
        )
        self.url = url
        self.action_delay = action_delay
        self.scroll_limit = scroll_limit

    async def crawl(self) -> list[KinoData]:
        result: list[KinoData] = []

        try:
            await self._before_crawl()

            # 1단계. 스크롤 페이지 끝까지 내려 모두 로딩
            await self.page.goto(self.url)
            await self._scroll_page_until_end(limit=self.scroll_limit)

            # 2단계. 각 작품 id 수집
            items = await self._get_attributes("div.contents-wrap a", "href")
            ids = [m.group() for item in items if (m := re.search(r"\d+", item))]

            # 3단계. 각 작품 정보 수집
            for id in ids:
                await self.page.goto(f"{self.TITLE_URL}{id}")
                await self.page.wait_for_selector(".title-kr")

                # 정액제 버튼 클릭
                await self._click_element(".price-tab")
                await self.page.wait_for_timeout(self.action_delay)

                # OTT 정보 수집
                ott_items = await self.page.query_selector_all(".movie-price-item")
                if not ott_items:
                    continue

                availabilities: list[Availability] = []
                for item in ott_items:
                    ott_name = await item.eval_on_selector(
                        ".name", "el => el.textContent"
                    )
                    web_url = await item.eval_on_selector(
                        "a", "el => el.getAttribute('href')"
                    )
                    date_info = (
                        await item.eval_on_selector(".date", "el => el.textContent")
                        if await item.query_selector(".date")
                        else None
                    )

                    ott_release_date = None
                    ott_close_date = None
                    if date_info:
                        m = re.search(
                            r"종료예정일\s*:\s*(\d{4}\.\d{2}\.\d{2})", date_info
                        )
                        if m:
                            ott_close_date = datetime.strptime(
                                m.group(1), "%Y.%m.%d"
                            ).date()
                        else:
                            m = re.search(
                                r"공개예정일\s*:\s*(\d{4}\.\d{2}\.\d{2})", date_info
                            )
                            if m:
                                ott_release_date = datetime.strptime(
                                    m.group(1), "%Y.%m.%d"
                                ).date()

                    availabilities.append(
                        Availability(
                            ott_name=ott_name,
                            web_url=web_url,
                            ott_release_date=ott_release_date,
                            ott_close_date=ott_close_date,
                        )
                    )
                    await self.page.wait_for_timeout(self.action_delay)

                # 더보기 버튼 클릭
                await self._click_element("button.more")
                await self.page.wait_for_timeout(self.action_delay)

                # 배경 이미지 추출
                style = await self._get_attribute("div.backdrop div", "style")
                backdrop_url = (
                    m.group(1)
                    if style and (m := re.search(r"url\(['\"]?(.*?)['\"]?\)", style))
                    else None
                )

                program: Program = Program(
                    kino_id=int(id),
                    title=await self._get_text(".title-kr"),
                    description=await self._get_text("div.synopsis"),
                    meta=await self._get_text(".metadata-item"),
                    thumbnail_url=await self._get_attribute("div.poster img", "src"),
                    backdrop_url=backdrop_url,
                )

                kino_data: KinoData = KinoData(
                    program=program,
                    availabilities=availabilities,
                )

                result.append(kino_data)
        except Exception as e:
            self.logger.error("Error occurred while crawling", error=str(e))
        return result

    async def _before_crawl(self) -> None:
        pass
