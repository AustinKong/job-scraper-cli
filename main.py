from dotenv import load_dotenv
load_dotenv()

import ui
from workflows.profile import setup_profile, show_profile
from workflows.experience import list_experiences, add_experience
from workflows.generate_resume import generate_resume

def main():
  while True:
    ui.print("Job Scraper v0.1")
    match ui.select("What would you like to do?", choices=[
      ui.Choice("Generate CV from job listings", "generate_cv"),
      ui.Choice("Show candidate profile", "show_profile"),
      ui.Choice("Setup candidate profile", "setup_profile"),
      ui.Choice("Show work experiences", "show_experiences"),
      ui.Choice("Add work experience", "add_experience"),
      ui.Choice("Test", "test"),
      ui.Choice("Exit", "exit")
    ]).ask():
      case "generate_cv":
        generate_resume()
      case "show_profile":
        show_profile()
      case "setup_profile":
        setup_profile()
      case "show_experiences":
        list_experiences()
      case "add_experience":
        add_experience()
      case "test":
        ui.bullets("Test List Input").ask()
      case "exit":
        ui.print("Goodbye!")
        return

if __name__ == "__main__":
  main()