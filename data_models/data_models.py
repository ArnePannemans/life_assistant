from dataclasses import dataclass

@dataclass
class CalendarEvent:
    summary: str
    location: str
    description: str
    start_datetime: str
    end_datetime: str
