from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class Bullet(BaseModel):
  text: str

class Experience(BaseModel):
  title: str
  company: str
  start_date: date
  end_date: Optional[date]
  location: Optional[str]
  type: Optional[str] = None
  bullets: List[Bullet] = Field(default_factory=list)

class Profile(BaseModel):
  full_name: str
  email: str
  phone: str
  location: Optional[str]
  website: Optional[str]
