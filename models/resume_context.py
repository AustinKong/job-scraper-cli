from pydantic import BaseModel, Field
from typing import Optional, Self, List
from datetime import date

class ResumeContext(BaseModel):
  class ResumeExperience(BaseModel):
    title: str
    company: str
    start_date: date
    end_date: Optional[date]
    location: Optional[str]
    bullets: List[str] = Field(default_factory=list)

  class ResumeEducation(BaseModel):
    institution: str
    program: str
    start_date: date
    end_date: Optional[date]
    location: Optional[str]
    bullets: List[str] = Field(default_factory=list)

  full_name: str
  email: str
  phone: str
  location: Optional[str]
  website: Optional[str]

  skills: List[str] = Field(default_factory=list)
  education: List[ResumeEducation] = Field(default_factory=list)
  work_experience: List[ResumeExperience] = Field(default_factory=list)
  projects: List[ResumeExperience] = Field(default_factory=list)
  awards: List[str] = Field(default_factory=list)
