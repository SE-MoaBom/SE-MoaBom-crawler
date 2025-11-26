from dataclasses import dataclass


@dataclass(slots=True, frozen=False)
class Program:
    kino_id: int
    title: str
    genre: str
    description: str
    thumbnail_url: str
    backdrop_url: str | None = None
    running_time: int | None = None
    ranking: int | None = None
    status: str | None = None
