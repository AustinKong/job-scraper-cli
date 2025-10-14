import hashlib
import re
import sqlite3
from langchain_core.runnables import RunnableLambda

STOPWORDS = {"the","a","an","and","or","to","of","in","for","on","at","by","with","from","is","are","be","as","that","this"}

def _tokenize(text: str):
  text = text.lower()
  text = re.sub(r"[^a-z0-9\s]+", " ", text)
  tokens = text.split()
  return [t for t in tokens if len(t) > 2 and t not in STOPWORDS]

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

def _jaccard(A, B):
  return len(A & B) / len(A | B)

def _fuzzy_dedup(input):
  content = input["content"].strip()
  sim = _simhash128(content)

  HAMMING_THRESHOLD = 8
  JACCARD_THRESHOLD = 0.35

  A = _char_set(content)
  with sqlite3.connect("store.db") as db:
    for (blob, listing_content) in db.execute("SELECT simhash128, content FROM listings"):
      # Lightweight simhash check first
      listing_sim = int.from_bytes(blob, "big")

      if _hamming128(sim, listing_sim) <= HAMMING_THRESHOLD:
        # Expensive Jaccard check to eliminate false positives
        B = _char_set(listing_content)

        if _jaccard(A, B) >= JACCARD_THRESHOLD:
          return None
    
  return input | { "simhash128": sim }

fuzzy_dedup = RunnableLambda(_fuzzy_dedup)
