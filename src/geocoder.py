import re, pandas as pd

def _norm(s: str) -> str:
    s = (s or "").lower()
    s = s.replace(",", " ").replace(";", " ").replace("|"," ").replace("/", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s

LOCAL_DB = {
    "rotterdam netherlands": (51.9244, 4.4777, "Rotterdam, NL"),
    "huelva spain": (37.2614, -6.9447, "Huelva, ES"),
    "sines portugal": (37.9562, -8.8698, "Sines, PT"),
    "neuquén argentina": (-38.9516, -68.0591, "Neuquén, AR"),
    "neuquen argentina": (-38.9516, -68.0591, "Neuquén, AR"),
    "madrid spain": (40.4168, -3.7038, "Madrid, ES"),
    "amsterdam netherlands": (52.3676, 4.9041, "Amsterdam, NL"),
    "antwerp belgium": (51.2194, 4.4025, "Antwerp, BE")
}

def geocode_records(df):
    lats, lons, labels = [], [], []
    for _, r in df.iterrows():
        key = _norm(r.get("ubicacion_hint",""))
        best = None
        if key:
            # intenta con sufijos de país
            for suffix in ["", " netherlands", " spain", " portugal", " argentina", " belgium"]:
                cand = (key + suffix).strip()
                if cand in LOCAL_DB: best = LOCAL_DB[cand]; break
        if best:
            lat, lon, label = best
        else:
            lat = lon = None; label = r.get("ubicacion_hint","")
        lats.append(lat); lons.append(lon); labels.append(label)
    out = df.copy()
    out["lat"]=lats; out["lon"]=lons; out["ubicacion"]=labels
    out = out.dropna(subset=["lat","lon"])
    return out
