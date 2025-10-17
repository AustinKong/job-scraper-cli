from models.bullet import Bullet
import ui
from models import Experience

def list_experiences():
  experiences = Experience.load_all()

  for exp in experiences:
    ui.print(f" - {exp.title} at {exp.company} ({exp.start_date} to {exp.end_date or 'Present'})")
    for bullet in exp.bullets:
      ui.print(f"   - {bullet.text}")

  return None

def add_experience():
  ui.print("Let's add a new work experience")

  title = ui.text("What is your job title?").ask()
  company = ui.text("What is the company name?").ask()
  start_date, end_date = ui.date_range("What is the date range of this experience?").ask()
  location = ui.text("What is the location of this job? (e.g., City, Country or Remote)").ask()
  
  bullets = ui.list("Now, let's add some bullet points describing your responsibilities and achievements in this role.").ask()

  experience = Experience(
    title=title,
    company=company,
    start_date=start_date,
    end_date=end_date if end_date else None,
    location=location,
    bullets=[Bullet(text=b) for b in bullets]
  )

  experience.save()