import ui
from models import Profile

def setup_education():
  test = ui.form(
    date=ui.date("Enter a date"),
    date_range=ui.date_range("enter a date range"),
    selection=ui.select("selection", ['a', 'b', 'c'])
  ).ask()
  print(test)

def setup_profile():
  ui.print("Let's build your candidate profile")
  ui.print("This information will NOT be fed into LLMs, only fed to the resume formatter")

  full_name = ui.text("What is your full legal name?").ask()
  email = ui.text("What is your email address?").ask()
  phone = ui.text("What is your phone number?").ask()
  location = ui.text("What is your location? (e.g., City, Country or Remote)").ask()
  website = ui.text("What is your personal website/LinkedIn URL?").ask()

  profile = Profile(
    full_name=full_name,
    email=email,
    phone=phone,
    location=location,
    website=website
  )

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
