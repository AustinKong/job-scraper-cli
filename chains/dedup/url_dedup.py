from langchain_core.runnables import RunnableLambda
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode, quote, unquote
import sqlite3

# Normalize percent encoding, collapse double slashes
def _clean_path(path: str) -> str:
  if not path:
    return "/"
  
  path = quote(unquote(path), safe="/-._~:@!$&'()*+,;=")

  while "//" in path:
    path = path.replace("//", "/")
  
  return path or "/"

TRACKING_PARAMS = {
  "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
  "gclid", "fbclid", "sessionid", "phpsessid", "ref", "tracking_id"
}

# Removes noisy tracking query params, lower cases params and sorts
def _clean_query(query: str) -> str:
  kv_pairs = []

  for k, v in parse_qsl(query, keep_blank_values=False):
    k_low = k.lower()
    if k_low in TRACKING_PARAMS:
      continue
    kv_pairs.append((k_low, v))
  
  kv_pairs.sort()
  return urlencode(kv_pairs, doseq=True)

def _normalize_url(url: str) -> str:
  url = url.strip()

  if not url.startswith(("http://", "https://")):
    url = "https://" + url

  parsed = urlparse(url)

  hostname = parsed.hostname
  if not hostname:
    raise ValueError(f"URL has no hostname: {url}")

  # Normalize weird ASCII chars
  try:
    host_norm = hostname.encode("idna").decode("ascii").lower()
  except Exception:
    host_norm = hostname.lower()

  scheme = parsed.scheme.lower()

  netloc = host_norm
  # Drop default ports (:80 for http and :443 for https), keep remaining
  if parsed.port and scheme in ("http", "https"):
    if (scheme == "http" and parsed.port != 80) or (scheme == "https" and parsed.port != 443):
      netloc += f":{parsed.port}"
  
  path = _clean_path(parsed.path)
  query = _clean_query(parsed.query)
  fragment = ""

  return urlunparse((scheme, netloc, path, "", query, fragment)) 

def _url_dedup(url):
  url = _normalize_url(url)

  with sqlite3.connect("store.db") as db:
    db.row_factory = sqlite3.Row
    row = db.execute("""
      SELECT url, content, simhash128, title, company, posted_date, description
      FROM listings
      WHERE url = ?
    """, (url,)).fetchone()

    if row is not None:
      row = dict(row)
      row["simhash128"] = int.from_bytes(row["simhash128"], "big")

      return row | { "dedup_conf": 1.0 }

  return { "url": url, "dedup_conf": 0.0 }

url_dedup = RunnableLambda(_url_dedup)
