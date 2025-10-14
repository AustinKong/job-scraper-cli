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

def list_prompt(text):
  input = prompt(text + " (Press enter twice to finish):\n", multiline=True, key_bindings=kb)
  return [i.strip() for i in input.splitlines() if i.strip()]

