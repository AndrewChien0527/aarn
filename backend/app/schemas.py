from pydantic import BaseModel
from typing import Optional, Dict


class VerifyPayload(BaseModel):
    verified: bool
    by: Optional[str] = None
    notes: Optional[str] = None
    extras: Optional[Dict[str,str]] = None


class SuggestPayload(BaseModel):
    user_id: Optional[str] = None
    field: str
    value: str