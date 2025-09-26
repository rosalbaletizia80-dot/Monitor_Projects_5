import re
from collections import defaultdict

def _score_text(text, cfg):
    text_l = (text or "").lower()
    hits = defaultdict(int)
    total = 0
    for cat, spec in cfg.get("categories", {}).items():
        w = int(spec.get("weight", 1))
        for kw in spec.get("keywords", []):
            if kw.lower() in text_l:
                hits[cat] += 1
                total += w
    if not hits:
        return None, [], 0
    # categoría principal = la de mayor hits*weight
    best_cat, best_val = None, -1
    tags = []
    for cat, spec in cfg.get("categories", {}).items():
        c_hits = hits.get(cat, 0)
        if c_hits:
            tags.extend([kw for kw in spec.get("keywords", []) if kw.lower() in text_l][:3])
            val = c_hits * int(spec.get("weight", 1))
            if val > best_val:
                best_val = val
                best_cat = cat
    return best_cat, list(dict.fromkeys(tags))[:5], best_val

def detect_opportunity(title, summary, extra, cfg):
    blob = " ".join([title or "", summary or "", extra or ""])
    cat, tags, score = _score_text(blob, cfg)
    return {
        "oportunidad_categoria": cat or "General",
        "oportunidad_tags": "; ".join(tags),
        "oportunidad_puntaje": int(score)
    }
