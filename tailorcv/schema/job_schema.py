# Schema representing the job description

from pydantic import BaseModel
class Job(BaseModel):
    title: str
    keywords: list[str]
    raw_text: str