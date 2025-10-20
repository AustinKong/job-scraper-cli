from typing import Callable, List, Optional, Tuple

from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.formatted_text import AnyFormattedText, FormattedText
from prompt_toolkit.styles import Style

from questionary.constants import DEFAULT_QUESTION_PREFIX
from questionary.styles import merge_styles_default
from questionary.question import Question

def _split_items(text: str) -> List[str]:
  out = []
  for line in text.splitlines():
    head, sep, tail = line.partition(". ")
    out.append(tail if head.isdigit() and sep else line)

  return out

def _render(items: List[str]) -> str:
  return "\n".join(f"{i+1}. {items[i]}" for i in range(len(items))) if items else "1. "

def _prefix_len(line: str) -> int:
  head, sep, _ = line.partition(". ")
  return len(head) + 2 if head.isdigit() and sep else 0

# Converts cursor position to logical (row, content_col), i.e. ignoring prefix
def _logical_cursor(doc: Document) -> Tuple[int, int]:
  row = doc.cursor_position_row
  col = doc.cursor_position_col
  line = doc.lines[row] if 0 <= row < len(doc.lines) else ""
  return row, max(0, col - _prefix_len(line))

def _absolute_cursor(row: int, content_col: int, items: List[str]) -> int:
  pos = 0
  for r in range(len(items)):
    pref = f"{r+1}. "
    content = items[r]
    
    if r == row:
      return pos + len(pref) + min(content_col, len(content))

    pos += len(pref) + len(content) + 1

  return len(_render(items))

# Soft-wrap continuation indent under the bullet
def make_wrap_indent_prefix(buf: Buffer) -> Callable[[int, int], AnyFormattedText]:
  def _prefix(line_no: int, wrap_count: int) -> AnyFormattedText:
    if wrap_count == 0:
      return ""

    lines = buf.document.lines

    if 0 <= line_no < len(lines):
      line = lines[line_no]
      head, sep, _ = line.partition(". ")
      pref_len = (len(head) + 2) if head.isdigit() and sep else 0
      return FormattedText([("", " " * pref_len)])

    return ""

  return _prefix

# Normalizer (renumber on any edit), with a suspend flag to avoid Enter races
def attach_normalizer(buf: Buffer):
  suspend = {"on": False}

  def normalize():
    if suspend["on"]:
      return

    old_doc = buf.document
    row, content_col = _logical_cursor(old_doc)
    items = _split_items(old_doc.text or "")
    new_text = _render(items) if items else "1. "

    if new_text == old_doc.text:
      if not buf.text:
        buf.set_document(Document("1. ", cursor_position=3))
      return

    target_row = min(row, max(0, len(items) - 1)) if items else 0
    new_cursor = _absolute_cursor(target_row, content_col, items if items else [""])
    buf.set_document(Document(new_text, cursor_position=min(new_cursor, len(new_text))))

  buf.on_text_changed += lambda _: normalize()
  return suspend

# Key bindings (no Up/Down navigation)
def make_key_bindings(buf: Buffer, suspend) -> KeyBindings:
  kb = KeyBindings()

  def line_content_blank(line: str) -> bool:
    return line[_prefix_len(line):].strip() == ""

  def in_prefix(forward: bool) -> bool:
    p = _prefix_len(buf.document.current_line)
    c = buf.document.cursor_position_col
    return (c <= p) if not forward else (c < p)

  def remove_line_at_cursor():
    doc = buf.document
    row = doc.cursor_position_row
    lines = doc.lines
    before, after = lines[:row], lines[row+1:]

    def strip_pref(L):
      h, s, t = L.partition(". ")
      return t if h.isdigit() and s else L

    items = [strip_pref(L) for L in (before + after)]
    new_text = _render(items) if items else "1. "
    buf.set_document(Document(new_text, cursor_position=len(new_text)))

  def at_end_of_item(doc: Document) -> bool:
    line = doc.current_line
    p = _prefix_len(line)
    content_len = len(line) - p
    return doc.cursor_position_col == p + content_len

  @kb.add("enter")
  def _(event):
    """
    Submit if current item is blank.
    Otherwise insert newline + next prefix directly.
    """
    doc = buf.document
    lines = doc.lines or ["1. "]
    row = doc.cursor_position_row

    if line_content_blank(lines[row]):
      final_items = [s.strip() for s in _split_items(buf.text) if s.strip()]
      event.app.exit(result=final_items)
      return

    if in_prefix(forward=True):
      buf.cursor_right(count=_prefix_len(doc.current_line) - doc.cursor_position_col)
      doc = buf.document

    items = _split_items(doc.text or "")
    next_num = row + 2 if row < len(items) else len(items) + 1
    insert_text = f"\n{next_num}. "
    suspend["on"] = True

    try:
      buf.insert_text(insert_text)
    finally:
      suspend["on"] = False

  @kb.add("backspace")
  def _(event):
    if in_prefix(forward=False):
      remove_line_at_cursor()
    else:
      buf.delete_before_cursor(1)

  @kb.add("delete")
  def _(event):
    doc = buf.document
    if in_prefix(forward=True):
      remove_line_at_cursor()
      return

    # Merge with next item at end-of-line (avoid pulling next "N. ")
    if at_end_of_item(doc):
      lines = doc.lines
      row = doc.cursor_position_row

      if row + 1 < len(lines):
        items = _split_items(buf.text or "")
        items[row] = items[row] + items[row + 1]
        del items[row + 1]
        joined_cursor = _absolute_cursor(row, len(items[row]), items)
        txt = _render(items)
        buf.set_document(Document(txt, cursor_position=joined_cursor))

      return

    buf.delete(1)

  @kb.add("home")
  def _(event):
    doc = buf.document
    p = _prefix_len(doc.current_line)
    buf.cursor_left(count=doc.cursor_position_col)

    if p:
      buf.cursor_right(count=p)

  @kb.add("c-c")
  def _(event):
    event.app.exit(result=None)
  
  @kb.add("<any>")
  def _(event):
    if not event.data:
      return

    if in_prefix(forward=True):
      event.app.output.bell()
      return

    buf.insert_text(event.data)

  return kb

def build_questionary_header(message: str, instruction: Optional[str], qmark: str) -> VSplit:
  left = Window(
    content=FormattedTextControl(FormattedText([("class:qmark", qmark)])),
    width=1, height=1, dont_extend_width=True
  )
  spacer = Window(width=1, char=" ", dont_extend_width=True, height=1)
  parts: List[Tuple[str, str]] = [("class:question", f"{message} ")]

  if instruction:
    parts.append(("class:instruction", f"{instruction}"))

  right = Window(
    content=FormattedTextControl(FormattedText(parts)),
    height=1, dont_extend_height=True
  )
  return VSplit([left, spacer, right], width=D(preferred=80))

def bullets(
  message: str,
  *,
  qmark: str = DEFAULT_QUESTION_PREFIX,
  style: Optional[Style] = None,
  instruction: Optional[str] = "(Enter on blank to finish)",
  default: List[str] = [],
  wrap: bool = True,
) -> Question:
  """
  Numbered list input:
    - shows blue "?" and styled message
    - numbered, paste-safe, immutable 'N. ' prefixes
    - Enter on blank submits; Delete at EOL merges lines
    - Up/Down disabled; Home jumps after prefix
    - optional soft wrap aligning under the bullet

  Returns a Question (use `.ask()`), whose result is List[str].
  """
  merged_style = merge_styles_default([style])

  buf = Buffer(multiline=True)
  initial_text = _render(default) if default else "1. "
  initial_cursor = len(initial_text) if default else 3
  buf.set_document(Document(initial_text, cursor_position=initial_cursor))
  suspend = attach_normalizer(buf)
  kb = make_key_bindings(buf, suspend)

  header = build_questionary_header(message, instruction, qmark)
  editor = Window(
    content=BufferControl(buffer=buf),
    wrap_lines=wrap,
    get_line_prefix=make_wrap_indent_prefix(buf) if wrap else None,
  )

  app = Application(
    layout=Layout(HSplit([header, editor])),
    key_bindings=kb,
    full_screen=False,
    mouse_support=False,
    style=merged_style,
  )

  return Question(app)
