import re, pandas as pd
from urllib.parse import urlparse
from dateutil import parser as dateparser
import yaml
from .opportunity_radar import detect_opportunity

SECTOR_RULES = {
    "Hidrógeno": [r"\bhydrogen\b", r"\bH2\b", r"electroly[sz]er", r"electroliz", r"hidrógeno", r"hidrogeno", r"hidrogénio"],
    "Oil & Gas": [r"\brefiner", r"\boil\b", r"\bpetchem\b", r"petroqu", r"cracker", r"\bupgrader\b", r"refiner[ií]a"],
    "Químicos": [r"chemical", r"qu[ií]mic", r"ammonia", r"urea", r"methanol", r"metanol", r"ethylene", r"propylene"],
    "Biodiésel": [r"\bbiodiesel\b", r"\bHVO\b", r"\bSAF\b", r"renewable diesel", r"biorefiner"],
    "Tratamiento de Aguas": [r"wastewater", r"water treatment", r"\bWWTP\b", r"EDAR", r"ETAR", r"ETAP", r"depuradora", r"desalin"]
}

STATUS_RULES = {
    "Anunciado": [r"\bannounce", r"\banunci", r"\bplan\b", r"\bMOU\b", r"\bLOI\b", r"\bpre-?FEED\b"],
    "Permisos": [r"\bpermi", r"\bEIA\b", r"environmental impact", r"\blicen[cs]"],
    "Financiación/Contrato": [r"\bfinanc", r"\bfunding", r"\bloan", r"\bFID\b", r"\bcontract\b", r"\bEPC\b", r"\baward"],
    "En construcción": [r"\bconstruction\b", r"\bobra", r"\bgroundbreaking\b", r"\bbuild(?:ing)?\b"],
    "Operativo": [r"\bcommission", r"\bstart-?up\b", r"\boperat", r"\bentra en operación"],
    "Pausado/Cancelado": [r"\bcancel", r"\bsuspend", r"\bhalt", r"\bpospon", r"\bdelay"]
}

CITY_LIST = ["Rotterdam","Amsterdam","Pernis","Eemshaven","Madrid","Barcelona","Bilbao","Valencia","Huelva","Cartagena","Lisbon","Lisboa","Porto","Sines","Neuquén","Santiago","Lima","Bogotá","Monterrey","São Paulo","Rio de Janeiro","Antwerp","Hamburg","Esbjerg","Sevilla","Tarragona","Castellón","Puertollano","A Coruña"]
CITY_REGEX = r"(" + "|".join([re.escape(c) for c in CITY_LIST]) + r")"
LEGAL_SUFFIX = r"(?:S\.?A\.?U?|S\.?L\.?U?|S\.?L\.?|B\.?V\.?|N\.?V\.?|GmbH|AG|SAS|S\.?p\.?A\.?|PLC|Plc|Ltd\.?|Limited|LLC|Oy|Oyj|S\.?A\.?S\.?)"
COMPANY_HINTS = [
    r"(?:by|with|from|of|de|por|con)\s+([A-Z][\w&\-\.’ ]+(?: "+LEGAL_SUFFIX+r")?)",
    r"([A-Z][\w&\-\.’ ]+(?: "+LEGAL_SUFFIX+r"))",
]

def classify_sector(text):
    for s, pats in SECTOR_RULES.items():
        if any(re.search(p, text, flags=re.IGNORECASE) for p in pats):
            return s
    return "Otros"

def extract_city(text):
    m = re.search(CITY_REGEX, text or "", flags=re.IGNORECASE)
    return m.group(1) if m else ""

def extract_company(text):
    t = text or ""
    for rx in COMPANY_HINTS:
        m = re.search(rx, t, flags=re.IGNORECASE)
        if m:
            name = m.group(1).strip(" ,.;:-")
            if len(name.split())>=1 and not name.lower().startswith(("project","proyecto","planta","terminal","port","puerto")):
                return " ".join(w if w.isupper() else w.capitalize() for w in name.split())
    return ""

def extract_status(text):
    for status, pats in STATUS_RULES.items():
        if any(re.search(p, text, flags=re.IGNORECASE) for p in pats):
            return status
    return "Sin clasificar"

def domain_from_url(url):
    try:
        host = urlparse(url).netloc.lower()
        for p in ("www.","m.","amp."):
            if host.startswith(p): host = host[len(p):]
        return host
    except Exception:
        return ""

def normalize_records(items, keywords):
    # carga reglas del radar
    import os
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    opp_cfg_path = os.path.join(base, "config", "opportunity_keywords.yaml")
    with open(opp_cfg_path, "r", encoding="utf-8") as f:
        opp_cfg = yaml.safe_load(f)

    rows = []
    for it in items:
        title = (it.get("title") or "").strip()
        summary = (it.get("summary") or "").strip()
        link = (it.get("link") or "").strip()
        feed_bucket = (it.get("source") or "").strip()
        published_raw = it.get("published") or ""
        try:
            published = dateparser.parse(published_raw).date().isoformat()
        except Exception:
            published = ""

        joined = f"{title}. {summary}"
        sector = classify_sector(joined)
        city = it.get("location_hint") or extract_city(joined)
        company = extract_company(joined)
        status = extract_status(joined)
        source_domain = domain_from_url(link)

        opp = detect_opportunity(title, summary, feed_bucket, opp_cfg)

        rows.append({
            "nombre": title,
            "empresa": company,
            "sector": sector,
            "estado": status,
            "ciudad_hint": city,
            "published": published,
            "fuente": feed_bucket,
            "medio": source_domain,
            "link": link,
            "resumen": summary,
            "oportunidad_categoria": opp["oportunidad_categoria"],
            "oportunidad_tags": opp["oportunidad_tags"],
            "oportunidad_puntaje": opp["oportunidad_puntaje"]
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.drop_duplicates(subset=["nombre","link"])
    return df
