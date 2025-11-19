import re
from ..core.llm import call_openai_chat


# Simple rule+LLM extraction pipeline


RATIO_PATTERNS = [r"(\d+(?:\.\d+)?(?:\+|\-|–)?\d*\s*-?approx)", r"(\d+(?:\.\d+)?\s*\-?approx)", r"(1\+\\eps)" ]




def extract_with_regex(abstract: str):
    if not abstract:
        return {}
    txt = abstract
    # naive ratio extraction heuristic
    ratios = []
    for p in RATIO_PATTERNS:
        m = re.search(p, txt, flags=re.I)
        if m:
            ratios.append(m.group(0))
    return {"approx_ratio": ratios[0] if ratios else None}




def extract_metadata(abstract: str, openai_ok: bool = True):
    # run regex first
    out = extract_with_regex(abstract)
    # if OpenAI is configured, use LLM to extract structured values
    try:
        if openai_ok:
            prompt = f"Extract the following fields from this abstract in JSON: approx_ratio, algorithm, analysis_method, one_sentence_summary.\nAbstract:\n{abstract}\nOutput JSON only."
            resp = call_openai_chat(prompt, max_tokens=200)
            # naive parse: attempt to find a JSON blob
            import json
            try:
                jstart = resp.find('{')
                j = json.loads(resp[jstart:])
                out.update(j)
            except Exception:
            # fallback: do nothing
                pass
    except Exception:
        pass
    return out