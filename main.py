from dotenv import load_dotenv
load_dotenv()

import ui
from workflows import setup_profile, show_profile

def main():
  ui.print("Job Scraper v0.1")

  match ui.select("What would you like to do?", choices=[
    ui.Choice("Generate CV from job listings", "generate_cv"),
    ui.Choice("Show candidate profile", "show_profile"),
    ui.Choice("Setup candidate profile", "setup_profile"),
    ui.Choice("Update experience database", "update_experience"),
    ui.Choice("Exit", "exit")
  ]).ask():
    case "generate_cv":
      print("Generating CV...")
    case "show_profile":
      show_profile()
    case "setup_profile":
      setup_profile()
    case "update_experience":
      print("Updating experience database...")
    case "exit":
      ui.print("Goodbye!")
      return

if __name__ == "__main__":
  main()