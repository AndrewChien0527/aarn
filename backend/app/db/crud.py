from sqlalchemy import select
from sqlmodel import Session
from .models import Paper, Suggestion, PaperHistory
import json
from datetime import datetime


def upsert_papers(session: Session, papers: list[dict]):
    out = []
    for p in papers:
        stmt = select(Paper).where(Paper.paper_id == p["paper_id"])
        existing = session.exec(stmt).first()
        
        authors_json = json.dumps(p.get("authors", []))

        if existing:
            # update fields if missing
            existing.title = p.get("title") or existing.title
            existing.abstract = p.get("abstract") or existing.abstract
            existing.citations = p.get("citations", existing.citations)
            existing.authors = authors_json
            existing.venue = p.get("venue") or existing.venue
            existing.pdf_url = p.get("pdf_url") or existing.pdf_url
            # optional fields
            existing.approx_ratio = p.get("approx_ratio", getattr(existing, "approx_ratio", None))
            existing.algorithm = p.get("algorithm", getattr(existing, "algorithm", None))
            existing.analysis_method = p.get("analysis_method", getattr(existing, "analysis_method", None))
            existing.verified = p.get("verified", getattr(existing, "verified", False))
            existing.verification_notes = p.get("verification_notes", getattr(existing, "verification_notes", None))
            session.add(existing)
            out.append(existing)
        else:
            paper = Paper(
                paper_id=p["paper_id"],
                title=p.get("title", ""),
                authors=authors_json,
                year=p.get("year"),
                venue=p.get("venue"),
                pdf_url=p.get("pdf_url"),
                abstract=p.get("abstract"),
                citations=p.get("citations", 0),
                verified=p.get("verified", False),
                verification_notes=p.get("verification_notes"),
                approx_ratio=p.get("approx_ratio"),
                algorithm=p.get("algorithm"),
                analysis_method=p.get("analysis_method"),
            )
            session.add(paper)
            session.commit()
            session.refresh(paper)
            out.append(paper)
    session.commit()
    return out




def get_paper_by_id(session: Session, paper_id: str):
    stmt = select(Paper).where(Paper.paper_id == paper_id)
    return session.exec(stmt).first()




def search_papers_db(session: Session, q: str):
    stmt = select(Paper).where(Paper.title.ilike(f"%{q}%") | Paper.abstract.ilike(f"%{q}%")).order_by(Paper.verified.desc())
    return session.exec(stmt).all()




def mark_verified(session: Session, paper_id: str, verified: bool, by: str = None, notes: str = None, extras: dict = None):
    p = get_paper_by_id(session, paper_id)
    if not p:
        return None
    # save history
    hist = PaperHistory(paper_id=paper_id, change=f"verified={verified}; notes={notes}", changed_by=by)
    session.add(hist)
    p.verified = verified
    p.verified_by = by
    from datetime import datetime
    p.verified_at = datetime.utcnow()
    if notes:
        p.verification_notes = notes
    if extras:
        if 'approx_ratio' in extras:
            p.approx_ratio = extras['approx_ratio']
        if 'algorithm' in extras:
            p.algorithm = extras['algorithm']
        if 'analysis_method' in extras:
            p.analysis_method = extras['analysis_method']
    session.add(p)
    session.commit()
    return p




def create_suggestion(session: Session, paper_id: str, field: str, value: str, user_id: str = None):
    s = Suggestion(paper_id=paper_id, field=field, suggested_value=value, user_id=user_id)
    session.add(s)
    session.commit()
    session.refresh(s)
    return s