from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class Paper(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    paper_id: str
    title: str
    authors: Optional[str] = None # JSON-encoded list
    year: Optional[int] = None
    venue: Optional[str] = None
    pdf_url: Optional[str] = None
    abstract: Optional[str] = None
    important_result: Optional[str] = None
    citations: Optional[int] = 0


# extracted/enriched fields
    approx_ratio: Optional[str] = None
    algorithm: Optional[str] = None
    analysis_method: Optional[str] = None
    summary: Optional[str] = None


# verification
    verified: bool = False
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    verification_notes: Optional[str] = None


    created_at: datetime = Field(default_factory=datetime.utcnow)




class Suggestion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    paper_id: str
    user_id: Optional[str] = None
    field: str
    suggested_value: str
    upvotes: int = 0
    downvotes: int = 0
    status: str = "pending" # pending/approved/rejected
    created_at: datetime = Field(default_factory=datetime.utcnow)




class PaperHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    paper_id: str
    change: str # json diff or textual note
    changed_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)