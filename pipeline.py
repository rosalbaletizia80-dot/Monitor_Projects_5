import os, yaml, feedparser, pandas as pd, logging, time, random
from src.normalizer import normalize_records
from src.geocoder import geocode_records
from src.map_builder import build_map

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
BASE = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.join(BASE, "config")
OUT = os.path.join(BASE, "output")

def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def fetch_rss(feeds):
    items = []
    for f in feeds.get("feeds", []):
        url = f.get("url", "").strip()
        name = f.get("name", "")
        if not url:
            continue
        logging.info(f"[RSS] {name}: {url}")
        time.sleep(0.6 + random.random()*0.5)
        d = feedparser.parse(url)
        for e in getattr(d, "entries", []):
            items.append({
                "title": e.get("title", ""),
                "summary": e.get("summary", ""),
                "link": e.get("link", ""),
                "published": e.get("published", e.get("updated","")),
                "source": name
            })
    logging.info(f"[RSS] total entries: {len(items)}")
    return items

def main():
    os.makedirs(OUT, exist_ok=True)
    feeds = load_yaml(os.path.join(CFG, "feeds_rss.yaml"))
    keywords = load_yaml(os.path.join(CFG, "keywords.yaml"))
    rss_items = fetch_rss(feeds)
    if not rss_items:
        logging.warning("[INFO] No RSS items. Using seed_data.csv")
        rss_items = pd.read_csv(os.path.join(CFG, "seed_data.csv")).to_dict(orient="records")

    df_norm = normalize_records(rss_items, keywords)
    logging.info(f"[NORM] rows after filter: {len(df_norm)}")
    df_geo = geocode_records(df_norm)
    logging.info(f"[GEO] rows with coords: {len(df_geo)}")

    csv_path = os.path.join(OUT, "proyectos.csv")
    df_geo.to_csv(csv_path, index=False)
    map_path = os.path.join(OUT, "mapa_proyectos.html")
    build_map(df_geo, map_path)
    logging.info(f"[OK] CSV -> {csv_path}")
    logging.info(f"[OK] MAP -> {map_path}")

if __name__ == "__main__":
    main()
