from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import FormattedText

def print_key_values(data: dict[str, str]) -> None:
  """
  Print key-value pairs in a formatted manner.
  """
  max_key_length = max(len(key) for key in data.keys()) if data else 0

  for key, value in data.items():
    padded_key = key.ljust(max_key_length)
    print_formatted_text(FormattedText([("bold", f"{padded_key}: "), ("", value)]))

