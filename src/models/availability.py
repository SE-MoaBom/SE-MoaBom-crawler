from dataclasses import dataclass
from datetime import date
from .ott_enum import OTTPlatform


@dataclass(slots=True, frozen=False)
class Availability:
    ott_name: OTTPlatform
    url: str
    release_date: date | None = None
    expire_date: date | None = None
