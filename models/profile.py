import json
import os
from pydantic import BaseModel, Field
from typing import List, Optional, Self
import ui
from datetime import date

PROFILE_PATH = os.getenv("PROFILE_PATH", "./data/profile.json")

class Education(BaseModel):
  institution: str
  program: str
  start_date: date
  end_date: Optional[date]
  location: Optional[str]
  bullets: List[str] = Field(default_factory=list)

# TODO: Add more descriptive error messages
class Profile(BaseModel):
  full_name: str
  email: str
  phone: str
  location: Optional[str]
  website: Optional[str]
  education: List[Education] = Field(default_factory=list)

  @ui.with_spinner("Saving profile...")
  def save(self):
    os.makedirs(os.path.dirname(PROFILE_PATH), exist_ok=True)
    try:
      with open(PROFILE_PATH, "w") as f:
        json.dump(self.model_dump(), f)
    except Exception as e:
      print(f"Error saving profile: {e}")
  
  @classmethod
  @ui.with_spinner("Loading profile...")
  def load(cls) -> Optional[Self]:
    try:
      with open(PROFILE_PATH, "r") as f:
        data = json.load(f)
        return cls(**data)
    except Exception:
      return None
