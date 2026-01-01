from pydantic import BaseModel
from typing import List, Optional

class BaseItem(BaseModel):
    id: str
    tags: List[str] = []
