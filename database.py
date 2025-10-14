from sqlalchemy import create_engine, Column, Integer, String, Date, Text
from sqlalchemy.orm import declarative_base, Session
from langchain_core.runnables import RunnableLambda

Base = declarative_base()

class ListingTable(Base):
  __tablename__ = "listings"
  id = Column(Integer, primary_key=True)
  title = Column(String)
  company = Column(String)
  posted_date = Column(Date, nullable=True)
  url = Column(String)
  description = Column(Text)
  keywords = Column(Text)

engine = create_engine("sqlite:///listings.db")
Base.metadata.create_all(engine)

def save_listings(listings):
  with Session(engine) as session:
    for l in listings:
      record = ListingTable(
        title=l.title,
        company=l.company,
        posted_date=l.posted_date,
        url=l.url,
        description=l.description,
        keywords=",".join(l.keywords),
      )
      session.add(record)
    session.commit()

save_to_db = RunnableLambda(lambda listings: save_listings(listings))
