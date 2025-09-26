def fetch_rss(feeds):
    import requests, feedparser, logging, time, random
    headers = {
        # UA “real” para que Google News no devuelva 403/429
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    items = []
    for f in feeds.get("feeds", []):
        url = f.get("url", "").strip()
        name = f.get("name", "")
        if not url:
            continue
        ok = False
        for attempt in range(3):  # hasta 3 intentos con backoff
            try:
                logging.info(f"[RSS] {name}: intento {attempt+1} -> {url}")
                resp = requests.get(url, headers=headers, timeout=15)
                if resp.status_code == 200 and resp.text:
                    d = feedparser.parse(resp.text)
                    if getattr(d, "entries", None):
                        for e in d.entries:
                            items.append({
                                "title": e.get("title", ""),
                                "link": e.get("link", ""),
                                "published": e.get("published", e.get("updated", "")),
                                "summary": e.get("summary", ""),
                                "source": name,
                            })
                        ok = True
                        break
                    else:
                        logging.warning(f"[RSS] {name}: 200 pero 0 entradas")
                else:
                    logging.warning(f"[RSS] {name}: HTTP {resp.status_code}")
            except Exception as ex:
                logging.warning(f"[RSS] {name}: error {type(ex).__name__}: {ex}")
            # pequeño backoff aleatorio
            time.sleep(0.8 + random.random()*0.8)
        if not ok:
            logging.error(f"[RSS] {name}: FALLÓ tras reintentos")
    logging.info(f"[RSS] total entradas: {len(items)}")
    return items
