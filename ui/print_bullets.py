import textwrap
import shutil
import questionary

def print_bullets(message: str, bullets: list[str]) -> None:
  terminal_width = shutil.get_terminal_size().columns

  questionary.print(message, style="bold")
  for bullet in bullets:
    wrapped = textwrap.fill(bullet, width=terminal_width - 4, initial_indent=" - ", subsequent_indent="   ")
    questionary.print(wrapped)
