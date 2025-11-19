from ..core.scholar import search_semantic_scholar
from ..services.extract_service import extract_metadata
from ..db.crud import upsert_papers
from ..db.base import get_session
import json




def search_and_enrich(query: str, k: int = 10):
    papers = search_semantic_scholar(query, limit=k)
    # enrich each
    for p in papers:
        meta = extract_metadata(p.get('abstract', ''), openai_ok=False)
        p.update(meta)
    # persist
    with next(get_session()) as session:
        upsert_papers(session, papers)
    return papers