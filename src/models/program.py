from dataclasses import dataclass
from datetime import date


@dataclass(slots=True, frozen=False)
class Program:
    kino_id: int
    title: str
    description: str
    meta: str

    thumbnail_url: str
    backdrop_url: str
