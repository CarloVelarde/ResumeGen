from pydantic import BaseModel
from typing import List, Optional

class Project(BaseModel):
    id: str
    name: str
    summary: Optional[str] = None
    highlights: List[str]
    tags: List[str] = []