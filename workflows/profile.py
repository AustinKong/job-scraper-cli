import ui
from models import Profile
from types import SimpleNamespace
from typing import Optional, Tuple

def _setup_one_education(default: Optional[Profile.Education] = None):
  education = default or SimpleNamespace(
    institution="",
    program="",
    start_date=None,
    end_date=None,
    location="",
    bullets=[]
  )

  data = ui.form(
    institution=ui.text("What is the institution name?", default=education.institution),
    program=ui.text("What is the program name?", default=education.program),
    start_end_date=ui.date_range("What is the start and end date?", default_start=education.start_date, default_end=education.end_date),
    location=ui.text("What is the location?", default=(education.location or "")),
    bullets=ui.bullets("Describe your achievements or activities.", default=education.bullets)
  ).ask()

  if data is None:
    return None

  start_date, end_date = data.pop("start_end_date")

  return Profile.Education(**data, start_date=start_date, end_date=end_date)

def setup_profile():
  profile = Profile.load() or SimpleNamespace(
    full_name="",
    email="",
    phone="",
    location="",
    website="",
    education=[]
  )

  data = ui.form(
    full_name=ui.text("What is your full legal name?", default=profile.full_name),
    email=ui.text("What is your email address?", default=profile.email),
    phone=ui.text("What is your phone number?", default=profile.phone),
    location=ui.text("What is your location?", instruction="Optional", default=(profile.location or "")),
    website=ui.text("What is your website URL?", instruction="Optional", default=(profile.website or ""))
  ).ask()

  data["education"] = profile.education if profile else []

  ui.list_editor(
    "Education history",
    data["education"],
    display_fn=lambda e: ui.print(f"{e.institution} - {e.program}"), # TODO: MAke better
    modify_fn=_setup_one_education,
    label_fn=lambda e: f"{e.institution} - {e.program}"
  )

  profile = Profile(**data)
  profile.save()

def show_profile():
  profile = Profile.load()

  if not profile:
    ui.print("No profile found. Please create a profile first.")
    return
  
  ui.print("Current Profile:")
  ui.print(f"Full Name: {profile.full_name}")
  ui.print(f"Email: {profile.email}")
  ui.print(f"Phone: {profile.phone}")
  ui.print(f"Location: {profile.location}")
  ui.print(f"Website: {profile.website}")
