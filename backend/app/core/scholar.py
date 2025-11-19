from typing import List
import requests
from ..config import S2_API_BASE


SEARCH_FIELDS = "title,authors,year,venue,externalIds,abstract,citationCount,url"




def search_semantic_scholar(query: str, limit: int = 10) -> List[dict]:
    url = f"{S2_API_BASE}/paper/search"
    params = {"query": query, "limit": limit, "fields": SEARCH_FIELDS}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    out = []
    for item in data.get("data", []):
        paper_id = item.get("paperId") or item.get("externalIds", {}).get("CorpusId")
        authors = [a.get("name") for a in item.get("authors", [])]
        out.append({
"paper_id": paper_id or f"s2-{item.get('paperId')}",
"title": item.get("title"),
"authors": authors,
"year": item.get("year"),
"venue": item.get("venue"),
"pdf_url": item.get("url"),
"abstract": item.get("abstract"),
"citations": item.get("citationCount", 0),
})
    return out