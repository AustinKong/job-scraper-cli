import hashlib
import math
import re
import sqlite3
from langchain_core.runnables import RunnableLambda

STOPWORDS = {"the","a","an","and","or","to","of","in","for","on","at","by","with","from","is","are","be","as","that","this"}

def _tokenize(text: str):
  text = text.lower()
  text = re.sub(r"[^a-z0-9\s]+", " ", text)
  return [t for t in text.split() if len(t) > 2 and t not in STOPWORDS]

def _hamming128(a: int, b: int) -> int:
  return (a ^ b).bit_count()

def _simhash128(text: str) -> int:
  tokens = _tokenize(text)
  vec = [0] * 128
  for tok in tokens:
    h = int.from_bytes(hashlib.blake2b(tok.encode(), digest_size=16).digest(), "big")
    for i in range(128):
      vec[i] += 1 if (h >> i) & 1 else -1
    
  out = 0
  for i, s in enumerate(vec):
    if s > 0:
      out |= (1 << i)
  return out

def _char_set(text, n = 4):
  text = re.sub(r"\s+", " ", text.lower()).strip()
  return { text[i:i+n] for i in range(len(text) - n + 1) }

def _jaccard(a, b):
  A, B = set(a), set(b)
  return len(A & B) / len(A | B)

def _confidence_from_metrics(hamming, jaccard):
  s_sim = 1.0 - (hamming / 128.0)
  j = 0.0 if jaccard is None else jaccard

  # Sigmoid
  z = -2.5 + 6.0 * s_sim + 8.0 * j
  conf = 1.0 / (1.0 + math.exp(-z))
  return conf

def _sim_confidence(a, b):
  title_sim = _jaccard(_tokenize(a["title"]), _tokenize(b["title"]))
  keyword_sim = _jaccard( # keywords need to be list
    [k.lower() for k in a["keywords"]],
    [k.lower() for k in b["keywords"]]
  )
  description_sim = _jaccard(_tokenize(a["description"]), _tokenize(b["description"]))
  is_same_company = a["company"].strip().lower() == b["company"].strip().lower()

  # Sigmoid
  z = -3.76 + (5.0 * title_sim) + (4.0 * keyword_sim) + (2.5 * description_sim)
  conf = 1.0 / (1.0 + math.exp(-z))

  conf *= (title_sim ** 2) if title_sim > 0 else 0.0
  conf *= (0.5 + 0.5 * keyword_sim)

  if is_same_company and title_sim < 0.6:
    conf *= 0.05

  if is_same_company and title_sim >= 0.6:
    conf = min(1.0, conf + 0.08)

  return max(0.0, min(1.0, conf))

def _fuzzy_dedup_new(input):
  content, title, description, keywords = input["content"].strip(), input["title"].strip(), input["description"].strip(), ",".join(input.get("keywords", []))
  simhash = _simhash128(content)

  HAMMING_THRESHOLD = 8
  DEDUP_THRESHOLD = 0.95

  A = _char_set(description)














def _fuzzy_dedup(input):
  content, title, description, keywords = input["content"].strip(), input["title"].strip(), input["description"].strip(), ",".join(input.get("keywords", []))
  sim = _simhash128(content)

  HAMMING_THRESHOLD = 8 # Only do Jaccard for reasonably close simhash
  DEDUP_THRESHOLD = 0.95

  A = _char_set(title + "\n" + description + "\n" + keywords)
  best = (0, -1) 
  with sqlite3.connect("store.db") as db:
    db.row_factory = sqlite3.Row

    for (id, blob, listing_title, listing_description, listing_keywords) in db.execute("SELECT id, simhash128, title, description, keywords FROM listings"):
      # Lightweight simhash check first
      listing_sim = int.from_bytes(blob, "big")

      h = _hamming128(sim, listing_sim)
      j = None
      # Do (expensive) Jaccard check if simhash close enough
      if h <= HAMMING_THRESHOLD:
        B = _char_set(listing_title + "\n" + listing_description + "\n" + listing_keywords)
        j = _jaccard(A, B)

      conf = _confidence_from_metrics(h, j)
      if conf > best[0]:
        best = (conf, id)

    conf, id = best
    if conf >= DEDUP_THRESHOLD:
      row = db.execute("""
        SELECT url, content, simhash128, title, company, posted_date, description
        FROM listings
        WHERE id = ?
      """, (id,)).fetchone()

      row = dict(row)
      row["simhash128"] = int.from_bytes(row["simhash128"], "big")

      return row | { "dedup_conf": conf }
    else:
      return input | { "simhash128": sim, "dedup_conf": 0.0 }

fuzzy_dedup = RunnableLambda(_fuzzy_dedup)
