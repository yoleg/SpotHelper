from dataclasses import dataclass
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent.parent / "data"
CANOPY_CSV = DATA_DIR / "canopies.csv"
CREDIT_URL = "https://www.skydivemag.com/new/2017-03-10-dying-for-airspeed/"
CREDIT_TITLE = "Dying for Airspeed"


@dataclass(frozen=True)
class Canopy:
    name: str
    description: str
    horizontal_mph: float
    vertical_mph: float

    @property
    def display_name(self) -> str:
        return f"{self.name} ({self.description}, {self.horizontal_mph} mph x {self.vertical_mph} mph)"

    def __str__(self):
        return self.display_name

    @classmethod
    def format_field_name(cls, name: str) -> str:
        return name.replace('_', ' ').title().replace(' Mph', ' Speed (mph)')


def get_canopies() -> list[Canopy]:
    df = pd.read_csv(CANOPY_CSV)
    return [Canopy(**row) for row in df.to_dict(orient='records')]


