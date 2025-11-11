from dataclasses import dataclass
from datetime import date


@dataclass(slots=True, frozen=False)
class Availability:
    ott_name: str

    ott_release_date: date | None = None
    ott_close_date: date | None = None

    web_url: str | None = None
