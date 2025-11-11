from dataclasses import dataclass
from datetime import date


@dataclass(slots=True, frozen=False)
class Availability:
    ott_name: str  # 넷플릭스, 티빙, 쿠팡플레이, 웨이브, 디즈니+, 왓챠, 라프텔, U+모바일tv, 아마존 프라임 비디오, 씨네폭스

    ott_release_date: date | None = None
    ott_close_date: date | None = None

    web_url: str | None = None
