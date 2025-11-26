import asyncio
from utils import get_logger, config
from crawlers import UpcomingCrawler, ExpiredCrawler, RankingCrawler, Crawler
from datetime import datetime
from db import init_db, AsyncSessionLocal, Repository, seed_otts, close_db


async def main():
    logger = get_logger(log_file_path=config.LOG_FILE_PATH, log_level=config.LOG_LEVEL)
    logger.info("Application started.")

    batch_start_time = datetime.now()

    try:
        await init_db()
        await seed_otts()
        logger.info("Database initialized and OTT platforms seeded.")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        return

    crawlers: list[Crawler] = [
        UpcomingCrawler(logger=logger),
        ExpiredCrawler(logger=logger),
        RankingCrawler(logger=logger),
    ]

    cleanup_upcoming = any(isinstance(c, UpcomingCrawler) for c in crawlers)
    cleanup_expiring = any(isinstance(c, ExpiredCrawler) for c in crawlers)

    async with AsyncSessionLocal() as session:
        repo = Repository(session, logger=logger)
        for crawler in crawlers:
            crawler_name = type(crawler).__name__
            try:
                logger.info(f"🚀 Starting crawler sequence: {crawler_name}")
                result = await crawler.run()

                if result:
                    await repo.save_crawl_results(result)
                    logger.info(f"✅ Saved {len(result)} items from {crawler_name}.")

                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"❌ Crawler {crawler_name} failed", error=str(e))

        # 모든 크롤링 완료 후 정리 작업
        await repo.cleanup_outdated_data(
            batch_start_time=batch_start_time,
            cleanup_upcoming=cleanup_upcoming,
            cleanup_expiring=cleanup_expiring,
        )

        await repo.log_statistics()

    logger.info("Application finished.")
    await close_db()


if __name__ == "__main__":
    asyncio.run(main())
