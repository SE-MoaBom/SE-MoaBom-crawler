from datetime import datetime
import urllib.parse
import re
import structlog
import asyncio
from playwright.async_api import Page
from .base import Crawler
from models import KinoData, Program, Availability, OTTPlatform
from utils import config


class KinoCrawler(Crawler):
    TITLE_URL = "https://m.kinolights.com/title/"

    def __init__(
        self,
        url: str,
        name: str,
        headless: bool | None = None,
        timeout: int | None = None,
        logger: structlog.stdlib.BoundLogger | None = None,
        action_delay: int | None = None,
        scroll_limit: int | None = None,
    ):
        # 이름에 접두사 처리
        full_name = f"kinolights-{name}" if not name.startswith("kinolights-") else name
        super().__init__(
            name=full_name, headless=headless, timeout=timeout, logger=logger
        )

        self.url = url
        self.action_delay = action_delay or config.ACTION_DELAY
        self.scroll_limit = scroll_limit or config.SCROLL_LIMIT

    async def crawl(self) -> list[KinoData]:
        ids = await self._get_content_ids()
        if not ids:
            return []
        return await self._crawl_details(ids)

    async def _get_content_ids(self) -> list[str]:
        """목록 페이지에서 ID 수집 (메인 페이지 사용)"""
        await self.page.goto(self.url)
        await self.page.wait_for_load_state("domcontentloaded")

        await self._scroll_page_until_end(limit=self.scroll_limit)

        # 두 가지 선택자 모두 시도
        items = await self._get_attributes("div.contents-wrap a", "href")
        if not items:
            items = await self._get_attributes("div.container__contents a", "href")

        ids = [m.group() for item in items if (m := re.search(r"\d+", item))]
        return list(set(ids))

    async def _crawl_details(self, ids: list[str]) -> list[KinoData]:
        """병렬로 상세 페이지 크롤링"""
        sem = asyncio.Semaphore(config.MAX_TABS)  # 동시 실행 제한 (5개)
        total = len(ids)

        async def fetch(index, content_id):
            async with sem:
                # 각 작업마다 독립된 페이지 생성
                page = await self.context.new_page()
                try:
                    self.logger.info(
                        f"Processing {index + 1}/{total}: {content_id}",
                        crawler=self.name,
                    )
                    result = await self._parse_single_content(content_id, page)
                    return result
                except Exception as e:
                    self.logger.error(f"Error parsing {content_id}: {e}")
                    return None
                finally:
                    await page.close()

        tasks = [fetch(i, cid) for i, cid in enumerate(ids)]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]

    async def _parse_single_content(self, id: str, page: Page) -> KinoData | None:
        """단일 페이지 파싱 (전달받은 page 객체 사용)"""
        await page.goto(f"{self.TITLE_URL}{id}")
        try:
            await page.wait_for_selector(".title-kr", timeout=self.timeout)
        except:
            self.logger.warning(f"Timeout: {id}")
            return None

        title = await self._get_text(".title-kr", page=page)

        # 정액제 탭
        await self._click_element(".price-tab", page=page)
        await page.wait_for_timeout(self.action_delay)

        ott_items = await page.query_selector_all(".movie-price-item")
        if not ott_items:
            return None

        availabilities = await self._parse_availabilities(title, ott_items)

        # 더보기 & 배경 이미지
        await self._click_element("button.more", page=page)

        style = await self._get_attribute("div.backdrop div", "style", page=page)
        backdrop_url = (
            m.group(1)
            if style and (m := re.search(r"url\(['\"]?(.*?)['\"]?\)", style))
            else None
        )

        # 메타데이터 추출 (JS 실행)
        metadata = await page.eval_on_selector_all(
            ".metadata__item",
            """items => {
                const data = {};
                items.forEach(item => {
                    const t = item.querySelector('.item__title')?.textContent.trim();
                    const b = item.querySelector('.item__body')?.textContent.trim();
                    if (t && b) data[t] = b;
                });
                return data;
            }""",
        )

        genre = metadata.get("장르", "Unknown")
        rt_str = metadata.get("러닝타임")
        running_time = int(re.search(r"(\d+)", rt_str).group(1)) if rt_str else None

        program = Program(
            kino_id=int(id),
            title=title,
            genre=genre,
            description=(await self._get_text("div.synopsis", page=page)).strip(),
            thumbnail_url=await self._get_attribute("div.poster img", "src", page=page),
            backdrop_url=backdrop_url,
            running_time=running_time,
            ranking=None,  # 랭킹은 RankingCrawler에서 후처리
        )

        return KinoData(program=program, availabilities=availabilities)

    async def _parse_availabilities(self, title, ott_items) -> list[Availability]:
        availabilities = []
        for item in ott_items:
            name_el = await item.query_selector(".name")
            if not name_el:
                continue

            ott_name = OTTPlatform.from_korean(await name_el.text_content())

            url_el = await item.query_selector("a")
            raw_url = (
                await url_el.get_attribute("href")
                if url_el
                else f"https://search.naver.com/search.naver?query={urllib.parse.quote(title)}"
            )

            date_el = await item.query_selector(".date")
            date_text = await date_el.text_content() if date_el else ""

            release_date, expire_date = None, None
            if m := re.search(r"종료예정일\s*:\s*(\d{4}\.\d{2}\.\d{2})", date_text):
                expire_date = datetime.strptime(m.group(1), "%Y.%m.%d").date()
            elif m := re.search(r"공개예정일\s*:\s*(\d{4}\.\d{2}\.\d{2})", date_text):
                release_date = datetime.strptime(m.group(1), "%Y.%m.%d").date()

            availabilities.append(
                Availability(
                    ott_name=ott_name,
                    url=self._extract_original_url(raw_url),
                    release_date=release_date,
                    expire_date=expire_date,
                )
            )
        return availabilities

    def _extract_original_url(self, url: str | None) -> str | None:
        if not url:
            return None
        try:
            parsed = urllib.parse.urlparse(url)
            qs = urllib.parse.parse_qs(parsed.query)
            if "url" in qs:
                return urllib.parse.unquote(qs["url"][0])
        except:
            pass
        return url
