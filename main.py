from dotenv import load_dotenv
load_dotenv()

import ui
from workflows import generate_cv, update_profile, update_experience

def main():
  ui.print("Job Scraper v0.1")

  match ui.select("What would you like to do?", choices=[
    ui.Choice("Generate CV from job listings", "generate_cv"),
    ui.Choice("Update candidate profile", "update_profile"),
    ui.Choice("Update experience database", "update_experience"),
    ui.Choice("Exit", "exit")
  ]).ask():
    case "generate_cv":
      generate_cv()
    case "update_profile":
      update_profile()
    case "update_experience":
      update_experience()
    case "exit":
      ui.print("Goodbye!")
      return

if __name__ == "__main__":
  main()