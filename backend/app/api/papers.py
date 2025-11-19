from fastapi import APIRouter, HTTPException
from ..db.base import get_session
from ..db.crud import get_paper_by_id


router = APIRouter(prefix="/papers")


@router.get("/{paper_id}")
def get_paper(paper_id: str):
    with next(get_session()) as session:
        p = get_paper_by_id(session, paper_id)
        if not p:
            raise HTTPException(status_code=404, detail="paper not found")
    return p