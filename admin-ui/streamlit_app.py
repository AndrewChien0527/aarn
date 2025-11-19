"""
Streamlit Admin UI for AARN (Approximation Algorithm Research Navigator)

Run:
    pip install -r requirements.txt
    streamlit run streamlit_app.py

Assumes backend base URL is in env var BACKEND_BASE (default: http://localhost:8000)
"""

import os
import streamlit as st
import requests
from typing import Optional
from urllib.parse import urljoin

# ======================
# Config
# ======================
BACKEND = os.getenv("BACKEND_BASE", "http://localhost:8000")
TIMEOUT = 15

st.set_page_config(page_title="AARN — Admin UI", layout="wide")

# ======================
# Helper API client
# ======================
def api_get(path: str, params: dict = None):
    url = urljoin(BACKEND, path)
    try:
        r = requests.get(url, params=params, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"GET {path} failed: {e}")
        return None

def api_post(path: str, json_body: dict = None):
    url = urljoin(BACKEND, path)
    try:
        r = requests.post(url, json=json_body, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"POST {path} failed: {e}")
        return None

# ======================
# UI utilities
# ======================
def format_authors(a):
    if not a:
        return ""
    if isinstance(a, list):
        return ", ".join(a)
    return a

def paper_card(p):
    title = p.get("title") or p.get("paper_id")
    authors = format_authors(p.get("authors"))
    year = p.get("year") or "-"
    ver = "⭐ Verified" if p.get("verified") else "⚠️ Unverified"
    snippet = p.get("important_result") or (p.get("abstract") or "")[:300]
    return title, authors, year, ver, snippet

# ======================
# Page: Search
# ======================
def page_search():
    st.header("Search / Enrich")
    col1, col2 = st.columns([3,1])
    with col1:
        q = st.text_input("Search query", placeholder="e.g. k-center approximation, PTAS, FPTAS")
    with col2:
        k = st.number_input("Top K", min_value=1, max_value=50, value=8)
        run = st.button("Search")

    if 'last_query' not in st.session_state:
        st.session_state['last_query'] = None

    if run and q:
        st.session_state['last_query'] = q
        with st.spinner("Searching and enriching..."):
            results = api_get("/search", params={"q": q, "k": k})
            st.session_state['results'] = results or []
    elif st.session_state.get('last_query') and 'results' not in st.session_state:
        st.session_state['results'] = api_get("/search", params={"q": st.session_state['last_query'], "k": k}) or []

    results = st.session_state.get('results') or []

    st.markdown(f"**Results** — {len(results)}")
    for p in results:
        title, authors, year, ver, snippet = paper_card(p)
        with st.expander(f"{title} — {authors} ({year}) — {ver}"):
            st.write(snippet)
            cols = st.columns([4,1,1])
            if cols[2].button("Open details", key=f"open_{p.get('paper_id')}"):
                st.session_state['selected_paper'] = p.get('paper_id')
            if cols[1].button("Save to DB (ensure exists)", key=f"save_{p.get('paper_id')}"):
                # Try to call /papers/{id} to force upsert (or call backend upsert endpoint if you have)
                r = api_get(f"/papers/{p.get('paper_id')}")
                if r:
                    st.success("Paper exists in DB (fetched).")
                else:
                    st.info("Paper not in DB or fetch failed. Backend should upsert on /search call.")

# ======================
# Page: Paper detail + extraction view
# ======================
def page_paper_detail():
    st.header("Paper Detail")
    paper_id = st.text_input("Paper ID (exact)", value=st.session_state.get('selected_paper', ""))
    if st.button("Load"):
        if paper_id:
            p = api_get(f"/papers/{paper_id}")
            st.session_state['paper_obj'] = p
    p = st.session_state.get('paper_obj')

    if not p:
        st.info("Load a paper (from Search > Open details, or paste a paper_id and press Load).")
        return

    st.subheader(p.get("title"))
    st.write(f"**Authors:** {format_authors(p.get('authors'))}")
    st.write(f"**Venue / Year:** {p.get('venue')} — {p.get('year')}")
    st.write(f"**Citations:** {p.get('citations')}")
    st.markdown("---")
    st.write("**Abstract**")
    st.write(p.get("abstract") or "(no abstract)")

    st.markdown("### Extracted metadata")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Approx Ratio**")
        st.write(p.get("approx_ratio") or "—")
        st.write("**Algorithm**")
        st.write(p.get("algorithm") or "—")
        st.write("**Analysis method**")
        st.write(p.get("analysis_method") or "—")
    with col2:
        st.write("**Summary**")
        st.write(p.get("summary") or "—")
        st.write("**Important result (snippet)**")
        st.write(p.get("important_result") or "—")

    st.markdown("---")
    st.write("**PDF / Links**")
    if p.get("pdf_url"):
        st.write(f"[Open PDF]({p.get('pdf_url')})")

    # Show verification
    st.markdown("---")
    st.subheader("Verification")
    verified = st.checkbox("Verified", value=bool(p.get("verified")))
    by = st.text_input("Verified by (admin id)", value="")
    notes = st.text_area("Verification notes", value=p.get("verification_notes") or "")

    if st.button("Save verification"):
        payload = {
            "verified": bool(verified),
            "by": by or None,
            "notes": notes or None,
            "extras": {
                "approx_ratio": p.get("approx_ratio"),
                "algorithm": p.get("algorithm"),
                "analysis_method": p.get("analysis_method")
            }
        }
        res = api_post(f"/admin/verify/{p.get('paper_id')}", json_body=payload)
        if res:
            st.success("Saved verification.")
            # refresh
            refreshed = api_get(f"/papers/{p.get('paper_id')}")
            st.session_state['paper_obj'] = refreshed

    st.markdown("---")
    st.subheader("Make a suggestion (community)")
    field = st.selectbox("Field", ["approx_ratio", "algorithm", "analysis_method", "summary", "important_result"])
    suggestion_value = st.text_input("Suggested value")
    sugg_user = st.text_input("Your user id (optional)")
    if st.button("Submit suggestion"):
        if not suggestion_value:
            st.warning("Please provide a value for suggestion.")
        else:
            payload = {"user_id": sugg_user or None, "field": field, "value": suggestion_value}
            r = api_post(f"/admin/suggest/{p.get('paper_id')}", json_body=payload)
            if r:
                st.success("Suggestion submitted.")

# ======================
# Page: Admin Dashboard (suggestions queue)
# ======================
def page_admin():
    st.header("Admin — Suggestions Queue")
    st.write("Review pending suggestions and approve/reject them (the backend should provide endpoints for approval).")

    page = st.number_input("Page", min_value=1, value=1)
    per_page = st.number_input("Per page", min_value=5, max_value=100, value=25)
    offset = (page - 1) * per_page

    suggestions = api_get("/admin/suggestions", params={"limit": per_page, "offset": offset}) or []
    if not suggestions:
        st.info("No pending suggestions (or endpoint missing).")
        return

    for s in suggestions:
        with st.expander(f"{s.get('field')} suggestion for {s.get('paper_id')} (by {s.get('user_id')})"):
            st.write(s.get("suggested_value"))
            cols = st.columns(3)
            if cols[0].button("Approve", key=f"approve_{s.get('id')}"):
                # call backend approve endpoint if exists
                res = api_post(f"/admin/suggestions/{s.get('id')}/approve")
                if res:
                    st.success("Approved")
            if cols[1].button("Reject", key=f"reject_{s.get('id')}"):
                res = api_post(f"/admin/suggestions/{s.get('id')}/reject")
                if res:
                    st.success("Rejected")
            if cols[2].button("Open paper", key=f"openpaper_{s.get('id')}"):
                st.session_state['selected_paper'] = s.get('paper_id')
# ======================
# Main page router
# ======================
PAGES = {
    "Search": page_search,
    "Paper Detail": page_paper_detail,
    "Admin Queue": page_admin,
}

st.sidebar.title("AARN Admin UI")
selected_page = st.sidebar.radio("Navigate", list(PAGES.keys()))

# Run the selected page
PAGES[selected_page]()
