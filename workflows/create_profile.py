import ui

ui.print("Let's build your candidate profile")
ui.print("This information will NOT be fed into LLMs, only fed to the resume formatter")
full_name = ui.text("What is your full legal name?").ask()
email = ui.text("What is your email address?").ask()
phone = ui.text("What is your phone number?").ask()
website = ui.text("What is your personal website/LinkedIn URL?").ask()

profile = {
  "full_name": full_name,
  "email": email,
  "phone": phone,
  "website": website
}

ui.print("Let's build your experience database")
ui.print("This information will be fed into LLMs, so remove any personally identifiable information (PII)")
# ui.text("Please enter your education history")



title = ui.text("What is your job title?").ask()
company = ui.text("What is the company name?").ask()
start_date, end_date = ui.date_range("What is the start and end date?").ask()
location = ui.text("What is the job location? (e.g., City, Country or Remote)").ask()
type = ui.text("What is the job type? (e.g., Full-time, Internship, Contract)").ask()

experience = Experience(
  title=title,
  company=company,
  start_date=start_date,
  end_date=end_date,
  location=location,
  type=type
)