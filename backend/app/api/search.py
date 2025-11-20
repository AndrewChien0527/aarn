from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from ..services.search_service import search_and_enrich
from ..db.base import get_session

router = APIRouter(prefix="/search")

@router.get("/")
def search(q: str = Query(...), k: int = Query(10), session: Session = Depends(get_session)):
    """
    Search papers and enrich DB if needed.
    """
    results = search_and_enrich(q, k, session=session)
    return results
