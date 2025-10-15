from typing import Optional, Tuple
import questionary
from questionary import Validator, ValidationError, Question
from datetime import datetime

DATE_FORMAT = "%Y/%m"

class DateValidator(Validator):
  def validate(self, document):
    text = document.text.strip()

    if text == "":
      return

    try:
      datetime.strptime(text, DATE_FORMAT)
    except ValueError:
      raise ValidationError(
        message="Enter a date in 'YYYY/MM' format or leave blank for ongoing (e.g., '2023/01' or '')",
        cursor_position=len(document.text)
      )

class DateInput:
  def __init__(self, message: str):
    self.message = message
  
  def ask(self) -> Optional[datetime]:
    response = questionary.text(f"{self.message} (Leave blank for ongoing)", validate=DateValidator).ask()
    return datetime.strptime(response, DATE_FORMAT) if response else None

def date(message: str):
  return DateInput(message)

class DateRangeValidator(Validator):
  def validate(self, document):
    text = document.text.strip()

    try:
      start_text, end_text = [s.strip() for s in text.split("-", 1)]
    except ValueError:
      raise ValidationError(
        message="Enter a range in 'YYYY/MM-YYYY/MM' format or 'YYYY/MM-' for ongoing.",
        cursor_position=len(document.text)
      )
    
    try:
      datetime.strptime(start_text, DATE_FORMAT)
    except ValueError:
      raise ValidationError(
        message="Start date must be in 'YYYY/MM' format (e.g., '2023/01')",
        cursor_position=len(document.text)
      )
    
    if end_text != "":
      try:
        datetime.strptime(end_text, DATE_FORMAT)
      except ValueError:
        raise ValidationError(
          message="End date must be in 'YYYY/MM' format or blank for ongoing (e.g., '2024/06' or '')",
          cursor_position=len(document.text)
        )

class DateRangeInput:
  def __init__(self, message: str):
    self.message = message
  
  def ask(self) -> Tuple[datetime, Optional[datetime]]:
    response = questionary.text(f"{self.message} (Leave blank for ongoing)", validate=DateRangeValidator).ask()

    start, end = response.split("-")
    start_date = datetime.strptime(start.strip(), "%Y/%m")
    end_date = datetime.strptime(end.strip(), "%Y/%m") if end.strip() else None

    return start_date, end_date
  
def date_range(message: str):
  return DateRangeInput(message)
