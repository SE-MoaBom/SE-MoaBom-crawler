from dataclasses import dataclass, field
from .program import Program
from .availability import Availability


@dataclass(slots=True, frozen=False)
class KinoData:
    program: Program
    availabilities: list[Availability] = field(default_factory=list)
