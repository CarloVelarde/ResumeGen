from pydantic import BaseModel
from typing import List

class Education(BaseModel):
    id: str
    institution: str
    area: str
    degree: str
    location: str
    start_date: str
    end_date: str
    highlights: List[str] = []
    tags: List[str] = []
