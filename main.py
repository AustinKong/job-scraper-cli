from dotenv import load_dotenv
load_dotenv()

import ui
from workflows.profile import setup_profile, show_profile
from workflows.experience import list_experiences, add_experience
from workflows.generate_resume import generate_resume

def main():
  while True:
    match ui.accordion("Job Scraper v0.1", groups=[
      ("Profile", [
        "Show profile",
        "Setup profile"
      ]),
      ("Experiences", [
        "Show experiences",
        "Add experience"
      ]),
      "Generate resume",
      "Exit"
    ]).ask():
      case "Show profile":
        show_profile()
      case "Setup profile":
        setup_profile()
      case "Show experiences":
        list_experiences()
      case "Add experience":
        add_experience()
      case "Generate resume":
        generate_resume()
      case "Exit":
        break
      case None:
        break

if __name__ == "__main__":
  main()