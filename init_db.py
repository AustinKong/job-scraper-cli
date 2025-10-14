import sqlite3

def init_db(db_path: str = "store.db"):
  with sqlite3.connect(db_path) as db:
    db.execute("""
    DROP TABLE IF EXISTS listings;
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS listings (
      id INTEGER PRIMARY KEY,

      url TEXT NOT NULL UNIQUE,
      content TEXT NOT NULL,
      simhash128 BLOB NOT NULL,

      title TEXT,
      company TEXT,
      posted_date DATE,
      description TEXT,
      keywords TEXT
    );
    """)
    db.commit()

if __name__ == "__main__":
  init_db()
  print("✅ Database initialized.")