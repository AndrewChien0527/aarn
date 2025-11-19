from fastapi import APIRouter, Body
from ..db.base import get_session
from ..db.crud import mark_verified, create_suggestion
from ..schemas import VerifyPayload, SuggestPayload


router = APIRouter(prefix="/admin")


@router.post("/verify/{paper_id}")
def admin_verify(paper_id: str, payload: VerifyPayload = Body(...)):
    with next(get_session()) as session:
        p = mark_verified(session, paper_id, payload.verified, by=payload.by, notes=payload.notes, extras=payload.extras)
        if not p:
            return {"ok": False}
        return {"ok": True}


@router.post("/suggest/{paper_id}")
def suggest(paper_id: str, payload: SuggestPayload = Body(...)):
    with next(get_session()) as session:
        s = create_suggestion(session, paper_id, payload.field, payload.value, user_id=payload.user_id)
    return s