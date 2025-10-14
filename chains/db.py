from langchain_core.runnables import RunnableLambda
import sqlite3

def _save_listing(listing):
  with sqlite3.connect("store.db") as db:
    db.execute("""
    INSERT OR IGNORE INTO listings (url, content, simhash128, title, company, posted_date, description, keywords)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, (
      listing["url"],
      listing["content"],
      listing["simhash128"].to_bytes(16, "big"),
      listing["title"],
      listing["company"],
      listing["posted_date"],
      listing["description"],
      ",".join(listing["keywords"]) if listing["keywords"] else None
    ))
    db.commit()
  
  return listing

def _read_listing_by_url(input):
  print(input)
  with sqlite3.connect("store.db") as db:
    db.row_factory = sqlite3.Row
    listing = db.execute("""
    SELECT url, content, simhash128, title, company, posted_date, description
    FROM listings
    WHERE url = ?
    """, (input["url"],)).fetchone()

    listing = dict(listing)
    listing["simhash128"] = int.from_bytes(listing["simhash128"], "big")
  
  return listing

save_listing = RunnableLambda(_save_listing)
read_listing_by_url = RunnableLambda(_read_listing_by_url)
