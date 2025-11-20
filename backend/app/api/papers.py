from fastapi import APIRouter, HTTPException
from ..db.base import get_session
from ..db.crud import get_paper_by_id
import json

router = APIRouter(prefix="/papers")


def paper_to_dict(paper):
    """Convert SQLModel Paper object to a dict for API response."""
    return {
        "paper_id": paper.paper_id,
        "title": paper.title,
        "authors": json.loads(paper.authors or "[]"),
        "year": paper.year,
        "venue": paper.venue,
        "pdf_url": paper.pdf_url,
        "abstract": paper.abstract,
        "citations": paper.citations,
        "verified": paper.verified,
        "verified_by": getattr(paper, "verified_by", None),
        "verification_notes": getattr(paper, "verification_notes", None),
        "approx_ratio": getattr(paper, "approx_ratio", None),
        "algorithm": getattr(paper, "algorithm", None),
        "analysis_method": getattr(paper, "analysis_method", None),
    }


@router.get("/{paper_id}")
def get_paper(paper_id: str):
    with next(get_session()) as session:
        paper = get_paper_by_id(session, paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        return paper_to_dict(paper)
