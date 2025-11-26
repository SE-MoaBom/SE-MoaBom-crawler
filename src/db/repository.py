from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy import select, exists, func
from .models import ProgramModel, AvailabilityModel, OTTModel
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
import structlog


class Repository:
    def __init__(
        self, session: AsyncSession, logger: structlog.stdlib.BoundLogger | None = None
    ):
        self.session = session
        self.logger = logger

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,)),
        reraise=True,
    )
    async def save_crawl_results(self, results):
        """
        크롤링 결과를 DB에 저장합니다. (Bulk Upsert)
        """
        if not results:
            return

        try:
            # 1. Program 데이터 준비
            program_values = []
            for data in results:
                p = data.program
                program_values.append(
                    {
                        "crawling_id": p.kino_id,
                        "title": p.title,
                        "genre": p.genre,
                        "description": p.description,
                        "thumbnail_url": p.thumbnail_url,
                        "backdrop_url": p.backdrop_url,
                        "running_time": p.running_time,
                        "ranking": p.ranking,
                        "status": p.status,
                    }
                )

            # 2. Program Bulk Upsert
            if program_values:
                stmt = mysql_insert(ProgramModel).values(program_values)
                update_dict = {
                    col.name: col
                    for col in stmt.inserted
                    if col.name not in ["program_id", "crawling_id", "created_at"]
                }
                await self.session.execute(stmt.on_duplicate_key_update(update_dict))
                await self.session.commit()

            # 3. ID 매핑 (crawling_id -> program_id)
            kino_ids = [data.program.kino_id for data in results]
            stmt_prog = select(ProgramModel.crawling_id, ProgramModel.program_id).where(
                ProgramModel.crawling_id.in_(kino_ids)
            )
            result_prog = await self.session.execute(stmt_prog)
            kino_id_map = {row.crawling_id: row.program_id for row in result_prog.all()}

            # 4. OTT ID 매핑 (name -> ott_id)
            all_ott_names = set(
                avail.ott_name.value
                for data in results
                for avail in data.availabilities
                if avail.ott_name
            )
            ott_map = {}
            if all_ott_names:
                stmt_ott = select(OTTModel.name, OTTModel.ott_id).where(
                    OTTModel.name.in_(all_ott_names)
                )
                result_ott = await self.session.execute(stmt_ott)
                ott_map = {row.name: row.ott_id for row in result_ott.all()}

            # 5. Availability 데이터 준비
            avail_values = []
            for data in results:
                program_id = kino_id_map.get(data.program.kino_id)
                if not program_id:
                    continue

                for avail in data.availabilities:
                    if not avail.ott_name:
                        continue

                    ott_id = ott_map.get(avail.ott_name.value)
                    if not ott_id:
                        continue

                    avail_values.append(
                        {
                            "program_id": program_id,
                            "ott_id": ott_id,
                            "url": avail.url,
                            "release_date": avail.release_date,
                            "expire_date": avail.expire_date,
                        }
                    )

            # 6. Availability Bulk Upsert
            if avail_values:
                stmt = mysql_insert(AvailabilityModel).values(avail_values)
                update_dict = {
                    "url": stmt.inserted.url,
                    "release_date": stmt.inserted.release_date,
                    "expire_date": stmt.inserted.expire_date,
                }
                await self.session.execute(stmt.on_duplicate_key_update(update_dict))
                await self.session.commit()

            if self.logger:
                self.logger.info(f"Saved {len(results)} items to database.")

        except Exception as e:
            if self.logger:
                self.logger.error("Failed to save crawl results", error=str(e))
            await self.session.rollback()

    async def cleanup_outdated_data(
        self,
        batch_start_time,
        cleanup_upcoming: bool = False,
        cleanup_expiring: bool = False,
    ):
        if self.logger:
            self.logger.info("Starting cleanup of outdated data...")

        try:
            # 1. 공개 예정작 정리 (status -> NULL)
            if cleanup_upcoming:
                stmt_upcoming = (
                    ProgramModel.__table__.update()
                    .where(ProgramModel.status == "UPCOMING")
                    .where(ProgramModel.updated_at < batch_start_time)
                    .values(status=None)
                )
                await self.session.execute(stmt_upcoming)

            # 2. 종료 예정작 정보 삭제
            if cleanup_expiring:
                stmt_expiring = (
                    AvailabilityModel.__table__.delete()
                    .where(AvailabilityModel.expire_date.is_not(None))
                    .where(AvailabilityModel.updated_at < batch_start_time)
                )
                await self.session.execute(stmt_expiring)

            # 3. 고아 데이터 삭제 (Availability가 없는 Program)
            subq = select(AvailabilityModel.availability_id).where(
                AvailabilityModel.program_id == ProgramModel.program_id
            )
            stmt_orphaned = (
                ProgramModel.__table__.delete()
                .where(ProgramModel.status.is_(None))
                .where(~exists(subq))
            )
            await self.session.execute(stmt_orphaned)

            await self.session.commit()

        except Exception as e:
            if self.logger:
                self.logger.error("Failed to cleanup outdated data", error=str(e))
            await self.session.rollback()

    async def log_statistics(self):
        try:
            total = await self.session.scalar(
                select(func.count()).select_from(ProgramModel)
            )
            upcoming = await self.session.scalar(
                select(func.count())
                .select_from(ProgramModel)
                .where(ProgramModel.status == "UPCOMING")
            )
            expiring = await self.session.scalar(
                select(func.count())
                .select_from(ProgramModel)
                .where(ProgramModel.status == "EXPIRING")
            )

            self.logger.info(
                "📊 DB Statistics",
                total_programs=total,
                upcoming=upcoming,
                expiring=expiring,
            )
        except Exception as e:
            self.logger.error("Failed to fetch DB statistics", error=str(e))
