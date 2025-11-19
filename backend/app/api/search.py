from fastapi import APIRouter, Query, Depends
from ..services.search_service import search_and_enrich


router = APIRouter(prefix="/search")


@router.get("/")
def search(q: str = Query(...), k: int = Query(10)):
    results = search_and_enrich(q, k)
    return results