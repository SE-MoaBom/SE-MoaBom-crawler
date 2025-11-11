from dataclasses import asdict
import json
from utils import get_logger, Config
from crawlers import UpcomingCrawler, ExpiredCrawler, ExploreCrawler, Crawler
import asyncio


async def main():
    config = Config()
    logger = get_logger(log_file_path=config.LOG_FILE_PATH, log_level=config.LOG_LEVEL)
    logger.info("Application started.")

    crawler_settings = {
        "logger": logger,
        "headless": config.HEADLESS_MODE,
        "timeout": config.BROWSER_TIMEOUT,
        "action_delay": config.ACTION_DELAY,
        "scroll_limit": config.SCROLL_LIMIT,
    }

    crawlers: list[Crawler] = [
        # UpcomingCrawler(**crawler_settings),
        # ExpiredCrawler(**crawler_settings),
        ExploreCrawler(
            **crawler_settings
        ),  # 주의! scroll_limit 없으면 10만개 이상 크롤링
    ]

    results = await asyncio.gather(*(crawler.run() for crawler in crawlers))

    # 임시 코드: json 파일로 저장
    results_dict = [
        [asdict(item) for item in crawler_result] for crawler_result in results
    ]
    with open("results.json", "w") as f:
        json.dump(results_dict, f, ensure_ascii=False, indent=4, default=str)


if __name__ == "__main__":
    asyncio.run(main())
