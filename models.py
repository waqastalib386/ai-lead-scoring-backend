
from pydantic import BaseModel
from typing import Optional

class LeadCreate(BaseModel):
    age: int
    income: int
    source: str
    pages_visited: int

class LeadResponse(LeadCreate):
    id: int
