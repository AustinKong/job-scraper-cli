from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings

kb = KeyBindings()

# Handles enter on empty line to submit
@kb.add("enter")
def _(event):
  buf = event.app.current_buffer
  if buf.document.text.endswith("\n") or buf.text.strip() == "":
    event.app.exit(result=buf.text)
  else:
    buf.insert_text("\n")

class ListInput:
  def __init__(self, message: str):
    self.message = message
  
  def ask(self):
    user_input = prompt(
      self.message + " (Press enter twice to finish):\n", 
      multiline=True, 
      key_bindings=kb
    )
    return [i.strip() for i in user_input.splitlines() if i.strip()]

def list(message: str) -> ListInput:
  """
  Create a multiline list-style input prompt.

  This function displays a prompt that allows the user to enter multiple lines
  of text, one item per line. When called, it returns a prompt object that can
  be executed with `.ask()` to collect the user's input. The result is a list
  of strings, each representing a line entered by the user.

  Args:
      message (str): The message to display above the input prompt.

  Returns:
      ListInput: A prompt object that collects multiline input and returns a list of strings.
  """
  return ListInput(message)
