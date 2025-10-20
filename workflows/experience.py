import ui
from models import Experience, Bullet
from typing import Optional

WORK_EXPERIENCE_TYPES = ["work", "volunteer", "internship", "contract", "freelance"]

def _display_experience(exp: Experience) -> None:
  ui.print(
    f"{exp.title} at {exp.company}\n"
    f"{exp.start_date} - {exp.end_date or 'Present'}\n"
    f"Location: {exp.location or 'N/A'}\n"
    f"Responsibilities and Achievements:\n"
    f" - {"\n - ".join(Bullet.to_texts(exp.bullets))}"
  )
  ui.press_any_key_to_continue().ask()

def _modify_work(work: Experience = Experience.empty()) -> Optional[Experience]:
  """
  Modify or create a work experience entry, includes work, volunteer, internship, contract, freelance.
  """
  entry = ui.form(
    title=ui.text("What is your job title?", default=work.title),
    company=ui.text("What is the company name?", default=work.company),
    type=ui.select("What type of work is this?", choices=[ui.Choice(title=type.capitalize(), value=type) for type in WORK_EXPERIENCE_TYPES], default=work.type),
    start_end_date=ui.date_range("What is the date range of this experience?", default_start=work.start_date, default_end=work.end_date),
    location=ui.text("What is the location of this job?", instruction="(Optional)", default=work.location or ""),
    bullets=ui.bullets("Describe your responsibilities and achievements in this role.", default=Bullet.to_texts(work.bullets))
  ).ask()

  if entry is None:
    return None

  entry["start_date"], entry["end_date"] = entry.pop("start_end_date")
  entry["bullets"] = Bullet.from_texts(entry.pop("bullets"))

  return Experience(**entry)

def _modify_project(project: Experience = Experience.empty("project")) -> Optional[Experience]:
  """
  Modify or create a project experience entry.
  """
  entry = ui.form(
    title=ui.text("What is the project title?", default=project.title),
    company=ui.text("What is the organization or client name?", default=project.company),
    start_end_date=ui.date_range("What is the date range of this project?", default_start=project.start_date, default_end=project.end_date),
    location=ui.text("What is the location of this project?", instruction="(Optional)", default=project.location or ""),
    bullets=ui.bullets("Describe your responsibilities and achievements in this project.", default=Bullet.to_texts(project.bullets))
  ).ask()

  if entry is None:
    return None

  entry["start_date"], entry["end_date"] = entry.pop("start_end_date")
  entry["bullets"] = Bullet.from_texts(entry.pop("bullets"))
  entry["type"] = "project"

  return Experience(**entry)

def work_history():
  work_history = [e for e in Experience.load_all() if e.type in WORK_EXPERIENCE_TYPES]

  work_history = ui.list_editor(
    "Work history",
    work_history,
    display_fn=_display_experience,
    modify_fn=_modify_work,
    label_fn=lambda e: f"{e.title} at {e.company}"
  )

  Experience.save_all(work_history)

def project_history():
  project_history = [e for e in Experience.load_all() if e.type == "project"]

  project_history = ui.list_editor(
    "Project history",
    project_history,
    display_fn=_display_experience,
    modify_fn=_modify_project,
    label_fn=lambda e: f"{e.title}"
  )

  Experience.save_all(project_history)
