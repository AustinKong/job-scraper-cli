from dotenv import load_dotenv
load_dotenv()

import ui
from workflows.profile import setup_profile, show_profile
from workflows.experience import work_history, project_history
from workflows.generate_resume import generate_resume

def main():
  while True:
    match ui.select("Job Scraper v0.1.1", choices=[
      "Profile",
      "Work history",
      "Project history",
      "Generate resume",
      "Exit"
    ]).ask():
      case "Profile":
        setup_profile()
      case "Work history":
        work_history()
      case "Project history":
        project_history()
      case "Generate resume":
        generate_resume()
      case "Exit":
        break
      case None:
        break

if __name__ == "__main__":
  main()