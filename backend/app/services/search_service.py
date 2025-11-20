from ..core.scholar import search_semantic_scholar
from ..services.extract_service import extract_metadata
from ..db.crud import upsert_papers
from ..db.base import get_session
from sqlmodel import Session
def search_and_enrich(query: str, k: int = 10 , session: Session=None):
    papers = search_semantic_scholar(query, limit=k)
    enriched = []
    for p in papers:
        meta = extract_metadata(p.get("abstract", ""), openai_ok=False)
        # Merge extracted metadata safely
        p.update({
            "approx_ratio": meta.get("approx_ratio"),
            "algorithm": meta.get("algorithm"),
            "analysis_method": meta.get("analysis_method"),
            **p  # keep original fields
        })
        enriched.append(p)

    with next(get_session()) as session:
        upsert_papers(session, enriched)

    return enriched
