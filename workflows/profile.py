import ui
from models import Profile
from typing import Optional

def _display_education(edu: Profile.Education) -> None:
  ui.print_key_values({
    "Institution": edu.institution,
    "Program": edu.program,
    "Date range": f"{str(edu.start_date)} - {str(edu.end_date) if edu.end_date else 'Present'}",
    "Location": edu.location or "N/A"
  })
  ui.print_bullets("Achievements and Activities:", edu.bullets)

def _modify_education(edu: Profile.Education) -> Optional[Profile.Education]:
  """
  Modify or create an education entry.
  """
  edu = edu or Profile.Education.empty()

  entry = ui.form(
    institution=ui.text("What is the institution name?", default=edu.institution),
    program=ui.text("What is the program name?", default=edu.program),
    start_end_date=ui.date_range("What is the start and end date?", default_start=edu.start_date, default_end=edu.end_date),
    location=ui.text("What is the location?", instruction="(Optional)", default=(edu.location or "")),
    bullets=ui.bullets("Describe your achievements or activities.", default=edu.bullets)
  ).ask()

  if entry is None:
    return None

  entry["start_date"], entry["end_date"] = entry.pop("start_end_date")

  return Profile.Education(**entry)

def setup_profile_basic():
  profile = Profile.load() or Profile.empty()

  data = ui.form(
    full_name=ui.text("What is your full legal name?", default=profile.full_name),
    email=ui.text("What is your email address?", default=profile.email),
    phone=ui.text("What is your phone number?", default=profile.phone),
    location=ui.text("What is your location?", instruction="(Optional)", default=(profile.location or "")),
    website=ui.text("What is your website URL?", instruction="(Optional)", default=(profile.website or ""))
  ).ask()
  data["education"] = profile.education if profile else []

  if data is None:
    return
  
  profile = Profile(**data)
  profile.save()

def setup_education():
  profile = Profile.load() or Profile.empty()
  education_history = profile.education if profile else []

  ui.list_editor(
    "Education history",
    education_history,
    display_fn=_display_education,
    modify_fn=_modify_education,
    label_fn=lambda e: f"{e.institution} - {e.program}"
  )

  profile.education = education_history
  profile.save()

# TODO: Make not shit
def show_profile():
  profile = Profile.load()

  if not profile:
    ui.print("No profile found.")
    return
  
  ui.print_key_values({
    "Full Name": profile.full_name,
    "Email": profile.email,
    "Phone": profile.phone,
    "Location": profile.location or "N/A",
    "Website": profile.website or "N/A"
  })
  ui.print("\nEducation History:")
  for edu in profile.education:
    _display_education(edu)
