from pydantic import BaseModel, Field
from typing import List, Optional


class JobPost(BaseModel):
    id: str
    source_group: str = Field(default="")
    source_url: str = Field(default="")
    title: str
    description: str = Field(default="")
    location: str = Field(default="")
    salary: Optional[str] = None
    posted_at: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
