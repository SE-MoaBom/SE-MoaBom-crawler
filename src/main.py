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

    results = await asyncio.gather(*(crawler.run() for crawler in crawlers))

    async with AsyncSessionLocal() as session:
        repo = Repository(session, logger=logger)
        for crawler_result in results:
            if crawler_result:
                await repo.save_crawl_results(crawler_result)
                logger.info(f"Saved {len(crawler_result)} items to database.")

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
