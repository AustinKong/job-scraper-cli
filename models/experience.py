from pydantic import BaseModel, Field
from typing import Optional, List, Self
from datetime import date
import ui
import os
import json
import uuid

from models.bullet import Bullet

EXPERIENCES_PATH = os.getenv("EXPERIENCES_PATH", "./data/experiences.json")

class Experience(BaseModel):
  id: uuid.UUID = Field(default_factory=uuid.uuid4)
  title: str
  company: str
  start_date: date
  end_date: Optional[date]
  location: Optional[str]
  type: Optional[str] = None
  bullets: List[Bullet] = Field(default_factory=list, exclude=True)

  # Helper method to load without spinner, used for save to avoid two spinners
  @classmethod
  def _load_all(cls) -> List[Self]:
    try:
      with open(EXPERIENCES_PATH, "r") as f:
        data = json.load(f)
        return [cls(**item, bullets=Bullet.load_by_experience(item["id"])) for item in data]
    except Exception:
      return []

  @classmethod
  @ui.with_spinner("Loading experiences...")
  def load_all(cls) -> List[Self]:
    return cls._load_all()

  @ui.with_spinner("Saving experience...")
  def save(self):
    os.makedirs(os.path.dirname(EXPERIENCES_PATH), exist_ok=True)
    try:
      experiences = self._load_all()

      ids = [e.id for e in experiences]
      if self.id in ids:
        experiences[ids.index(self.id)] = self
      else:
        experiences.append(self)

      with open(EXPERIENCES_PATH, "w") as f:
        json.dump([exp.model_dump(mode="json") for exp in experiences], f)
      
      Bullet.save_all(self.id, self.bullets)
    except Exception as e:
      print(f"Error saving experience: {e}")