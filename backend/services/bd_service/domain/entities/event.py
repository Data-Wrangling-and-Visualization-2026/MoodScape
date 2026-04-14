from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Event:
    id: Optional[int]
    year: int
    event_name: str
    description: Optional[str]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    MIN_YEAR = 1900
    MAX_YEAR = 2030
    
    def validate(self) -> bool:
        if not self.year or not (self.MIN_YEAR <= self.year <= self.MAX_YEAR):
            return False
        if not self.event_name or len(self.event_name.strip()) < 2:
            return False
        if len(self.event_name) > 500:
            return False
        return True
    
    def get_decade(self) -> int:
        return (self.year // 10) * 10
    
    def get_era(self) -> str:
        if self.year < 1960:
            return "post_war"
        elif self.year < 1980:
            return "cold_war"
        elif self.year < 1991:
            return "late_soviet"
        elif self.year < 2000:
            return "nineties"
        elif self.year < 2010:
            return "two_thousands"
        elif self.year < 2020:
            return "twenty_tens"
        else:
            return "twenty_twenties"