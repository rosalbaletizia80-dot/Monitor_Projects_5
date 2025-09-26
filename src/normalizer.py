import re, pandas as pd
from dateutil import parser as dateparser

SECTOR_RULES = {
    "Hidrógeno": [r"\bhydrogen\b", r"\bH2\b", r"electroly[sz]er", r"electroliz", r"hidrógeno", r"hidrogeno", r"hidrogénio"],
    "Oil & Gas": [r"\brefiner", r"\boil\b", r"\bpetchem\b", r"petroqu", r"cracker", r"\bupgrader\b", r"refiner[ií]a"],
    "Gas": [r"\bLNG\b", r"\bGNL\b", r"regas", r"\bpipeline\b", r"gasoduct"],
    "Químicos": [r"chemical", r"qu[ií]mic", r"ammonia", r"urea", r"methanol", r"metanol", r"ethylene", r"propylene"],
    "Biodiésel": [r"\bbiodiesel\b", r"\bHVO\b", r"\bSAF\b", r"renewable diesel", r"biorefiner"],
    "Tratamiento de Aguas": [r"wastewater", r"water treatment", r"\bWWTP\b", r"EDAR", r"ETAR", r"ETAP", r"depuradora", r"desalin"]
}

LATAM = {"mexico","méxico","brazil","brasil","argentina","chile","peru","perú","colombia","uruguay","ecuador","venezuela"}

def classify_region(text):
    t = (text or "").lower()
    if any(k in t for k in ["netherlands","nederland","países bajos","belgium","belgië","bélgica","germany","deutschland","alemania","denmark","danmark"]):
        return "NL/BE/DE/DK"
    if any(k in t for k in ["spain","españa"]): return "ES"
    if "portugal" in t: return "PT"
    for c in LATAM:
        if c in t: return "LATAM"
    return "OTHER"

def in_region(text, regions):
    t = (text or "").lower()
    for c in regions.get("countries", []):
        if c.lower() in t: return True
    for city in regions.get("cities", []):
        if city.lower() in t: return True
    return False

CITY_REGEX = r"(Rotterdam|Amsterdam|Pernis|Eemshaven|Antwerp|Hamburg|Esbjerg|Madrid|Barcelona|Bilbao|Valencia|Huelva|Cartagena|Lisboa|Lisbon|Porto|Sines|Neuqu[eé]n|Santiago|Lima|Bogot[aá]|Monterrey|S[ãa]o Paulo|Rio de Janeiro)"

def extract_location_hint(item):
    if item.get("location_hint"): return item["location_hint"]
    for field in ["title","summary"]:
        txt = item.get(field, "") or ""
        m = re.search(CITY_REGEX, txt, flags=re.IGNORECASE)
        if m: return m.group(0)
    return ""

def normalize_records(items, keywords):
    rows = []
    for it in items:
        title = (it.get("title") or "").strip()
        summary = (it.get("summary") or "").strip()
        link = (it.get("link") or "").strip()
        src = (it.get("source") or "").strip()
        published_raw = it.get("published") or ""
        try:
            published = dateparser.parse(published_raw).date().isoformat()
        except Exception:
            published = ""

        joined = f"{title} {summary}"
        sector = "Otros"
        for s, pats in SECTOR_RULES.items():
            if any(re.search(p, joined, flags=re.IGNORECASE) for p in pats):
                sector = s; break

        loc_hint = extract_location_hint(it)
        if not in_region(" ".join([title, summary, loc_hint]), keywords.get("regions", {})):
            continue

        rows.append({
            "nombre": title,
            "sector": sector,
            "tipo": "",
            "empresa": "",
            "ubicacion_hint": loc_hint,
            "published": published,
            "fuente": src,
            "link": link,
            "resumen": summary,
            "region": classify_region(" ".join([title, summary, loc_hint]))
        })
    df = pd.DataFrame(rows)
    if not df.empty: df = df.drop_duplicates(subset=["nombre","link"])
    return df
