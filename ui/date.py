from typing import Any, Optional, Tuple, List
from prompt_toolkit import PromptSession
from questionary.styles import merge_styles_default
from questionary.constants import DEFAULT_KBI_MESSAGE, DEFAULT_QUESTION_PREFIX
from questionary import Validator, ValidationError, Question
from questionary.prompts.common import build_validator
from prompt_toolkit.lexers import SimpleLexer
from datetime import datetime

DATE_FORMAT = "%Y/%m"

def _build_header(message, instruction = "(Date in 'YYYY/MM' format)", qmark = DEFAULT_QUESTION_PREFIX):
  def _header():
    result = [("class:qmark", qmark), ("class:question", " {} ".format(message))]
    if instruction:
      result.append(("class:instruction", " {} ".format(instruction)))
    return result
  
  return _header

class DateQuestion(Question):
  def __init__(self, message: str, **kwargs: Any):
    merged_style = merge_styles_default([kwargs.get("style")])

    session: PromptSession = PromptSession(
      _build_header(message=message),
      style=merged_style,
      validator=build_validator(self.validate),
      lexer=SimpleLexer("class:answer"),
      **kwargs
    )

    super().__init__(session.app)
    self.message = message

  def validate(self, text):
    text = text.strip()

    if text == "":
      return True

    try:
      datetime.strptime(text, DATE_FORMAT)
    except ValueError:
      raise ValidationError(
        message="Enter a date in 'YYYY/MM' format or leave blank for ongoing (e.g., '2023/01' or '')"
      )
    
    return True
  
  def _parse_response(self, response):
    return datetime.strptime(response, DATE_FORMAT)
  
  def ask(self, patch_stdout: bool = False, kbi_msg: str = DEFAULT_KBI_MESSAGE) -> Optional[datetime]:
    return self._parse_response(super().ask(patch_stdout=patch_stdout, kbi_msg=kbi_msg))
  
  def unsafe_ask(self, patch_stdout: bool = False) -> Any:
    return self._parse_response(super().unsafe_ask(patch_stdout=patch_stdout))

class DateRangeQuestion(Question):
  def __init__(self, message: str, **kwargs: Any):
    merged_style = merge_styles_default([kwargs.get("style")])

    session: PromptSession = PromptSession(
      _build_header(message=message),
      style=merged_style,
      validator=build_validator(self.validate),
      lexer=SimpleLexer("class:answer"),
      **kwargs
    )

    super().__init__(session.app)
    self.message = message

  def validate(self, text):
    text = text.strip()

    try:
      start_text, end_text = [s.strip() for s in text.split("-", 1)]
    except ValueError:
      raise ValidationError(
        message="Enter a range in 'YYYY/MM-YYYY/MM' format or 'YYYY/MM-' for ongoing."
      )
    
    try:
      datetime.strptime(start_text, DATE_FORMAT)
    except ValueError:
      raise ValidationError(
        message="Start date must be in 'YYYY/MM' format (e.g., '2023/01')"
      )
    
    if end_text != "":
      try:
        datetime.strptime(end_text, DATE_FORMAT)
      except ValueError:
        raise ValidationError(
          message="End date must be in 'YYYY/MM' format or blank for ongoing (e.g., '2024/06' or '')"
        )
    
    return True
  
  def _parse_response(self, response):
    start_text, end_text = [s.strip() for s in response.split("-", 1)]
    start_date = datetime.strptime(start_text, DATE_FORMAT)
    end_date = datetime.strptime(end_text, DATE_FORMAT) if end_text else None
    return start_date, end_date

  def ask(self, patch_stdout: bool = False, kbi_msg: str = DEFAULT_KBI_MESSAGE) -> Tuple[datetime, Optional[datetime]]:
    return self._parse_response(super().ask(patch_stdout=patch_stdout, kbi_msg=kbi_msg))
  
  def unsafe_ask(self, patch_stdout: bool = False) -> Any:
    return self._parse_response(super().unsafe_ask(patch_stdout))

def date(message: str):
  return DateQuestion(message)

def date_range(message: str):
  return DateRangeQuestion(message)
