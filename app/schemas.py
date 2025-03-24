from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class URLCreate(BaseModel):
    original_url: str
    custom_alias: str
    created_at: Optional[datetime] = None


class URLResponse(BaseModel):
    original_url: str
    short_code: str
    created_at: datetime

class URLStats(BaseModel):
    original_url: str
    short_code: str
    visit_count: int
    expires_at: Optional[datetime]
