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

save_listing = RunnableLambda(_save_listing)
