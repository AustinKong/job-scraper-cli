from dotenv import load_dotenv
load_dotenv()

import argparse
import sys
import ui
from workflows.profile import show_profile, setup_profile_basic, setup_education
from workflows.experience import work_history, project_history
from workflows.generate_resume import generate_resume

parser = argparse.ArgumentParser(description="Job Scraper CLI")

parser.add_argument(
  "-i", "--interactive",
  action="store_true",
  help="Run the application in interactive mode"
)

subparsers = parser.add_subparsers(dest="command")

profile_parser = subparsers.add_parser("profile", help="Set up or view your profile")
profile_parser.add_argument("--view", action="store_true", help="View your profile")
profile_parser.add_argument("--edit-basic", action="store_true", help="Edit your basic profile information")
profile_parser.add_argument("--edit-education", action="store_true", help="Edit your education history")

def main():
  args = parser.parse_args(sys.argv[1:])

  if args.interactive:
    _interactive()
    return

  match args.command:
    case "profile":
      if args.view: show_profile()
      elif args.edit_basic: setup_profile_basic()
      elif args.edit_education: setup_education()
    case _:
      parser.print_help()

# TODO: Update to follow args version
def _interactive():
  while True:
    match ui.select("Job Scraper v0.1.1", choices=[
      "Profile",
      "Work history",
      "Project history",
      "Generate resume",
      "Exit"
    ]).ask():
      case "Profile":
        setup_profile_basic()
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
