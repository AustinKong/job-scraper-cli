import json
import os
from pydantic import BaseModel, Field
from typing import Optional, List, Self
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
