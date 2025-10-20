from typing import List, Optional, Tuple, Union
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style
from questionary.question import Question
from questionary.constants import DEFAULT_QUESTION_PREFIX
from questionary.styles import merge_styles_default

Outer = Union[str, Tuple[str, List[str]]]  # "Single option" or ("Group label", ["Inner 1", "Inner 2", ...])

def accordion(
  message: str,
  groups: List[Outer],
  qmark: str = DEFAULT_QUESTION_PREFIX,
  style: Optional[Style] = None,
  wrap: bool = True
) -> Question:
  merged = merge_styles_default([style])
  # Normalize groups: single strings become (string, [string])
  groups_normalized = []
  for g in groups:
    if isinstance(g, str):
      groups_normalized.append((g, [g]))
    else:
      if len(g[1]) > 0:
        groups_normalized.append(g)
  groups_filtered = groups_normalized

  if not groups_filtered:
    raise ValueError("accordion: all groups are empty (no inner options).")

  outer_idx, inner_idx = 0, 0
  selected_text = None

  def _header() -> VSplit:
    left = Window(content=FormattedTextControl(FormattedText([("class:qmark", qmark)])),
                  width=1, height=1, dont_extend_width=True)
    spacer = Window(width=1, char=" ", dont_extend_width=True, height=1)
    right = Window(content=FormattedTextControl(text=lambda: FormattedText([
      ("class:question", f"{message} "),
    ] + ([("class:answer", selected_text)] if selected_text else [("class:instruction", "(Use arrow keys)")]))), height=1, dont_extend_height=True)

    return VSplit([left, spacer, right], width=D(preferred=80))

  def _render():
    if selected_text:
      return []

    out: List[Tuple[str, str]] = []

    for i, (outer_label, inner_list) in enumerate(groups_filtered):
      if len(inner_list) == 1 and inner_list[0] == outer_label:
        # Single selectable item
        sel = (i == outer_idx and inner_idx == 0)
        out.append(("class:outer" if sel else "class:outer", f"{' » ' if sel else '   '}{outer_label}\n"))
      else:
        # Group with multiple inners
        expanded = (i == outer_idx)
        out.append(("class:outer", f"{' ⌄ ' if expanded else ' > '}{outer_label}\n"))
        if expanded:
          for j, inner in enumerate(inner_list):
            sel = (j == inner_idx)
            out.append(("class:inner", f"{'    » ' if sel else '      '}{inner}\n"))

    if out:
      last_text = out[-1][1]
      if last_text.endswith('\n'):
        out[-1] = (out[-1][0], last_text[:-1])

    return out

  def _prev_group_with_inners(start: int) -> Optional[int]:
    for k in range(start, -1, -1):
      if groups_filtered[k][1]:
        return k

    return None

  def _next_group_with_inners(start: int) -> Optional[int]:
    for k in range(start, len(groups_filtered)):
      if groups_filtered[k][1]:
        return k

    return None

  def _move_up():
    nonlocal inner_idx, outer_idx
    if inner_idx > 0:
      inner_idx -= 1
      return

    # at first inner of this group -> jump to last inner of previous non-empty group
    prev_idx = _prev_group_with_inners(outer_idx - 1)
    if prev_idx is not None:
      outer_idx = prev_idx
      inner_idx = len(groups_filtered[outer_idx][1]) - 1

  def _move_down():
    nonlocal inner_idx, outer_idx
    inners = groups_filtered[outer_idx][1]
    if inner_idx < len(inners) - 1:
      inner_idx += 1
      return

    # at last inner -> jump to first inner of next non-empty group
    next_idx = _next_group_with_inners(outer_idx + 1)
    if next_idx is not None:
      outer_idx = next_idx
      inner_idx = 0

  def _bindings() -> KeyBindings:
    kb = KeyBindings()

    @kb.add("up")
    def _(event):
      _move_up()
      event.app.invalidate()

    @kb.add("down")
    def _(event):
      _move_down()
      event.app.invalidate()

    @kb.add("left")
    def _(event):
      event.app.output.bell()

    @kb.add("right")
    def _(event):
      nonlocal inner_idx
      inner_idx = 0
      event.app.invalidate()

    @kb.add("enter")
    def _(event):
      nonlocal selected_text
      selected_text = groups_filtered[outer_idx][1][inner_idx]
      event.app.layout = Layout(HSplit([_header()]))
      event.app.invalidate()
      event.app.exit(result=(groups_filtered[outer_idx][0], selected_text) if isinstance(groups[outer_idx], tuple) else groups[outer_idx])

    @kb.add("escape")
    @kb.add("c-c")
    def _(event):
      event.app.exit(result=None)

    return kb

  control = FormattedTextControl(_render, focusable=True, key_bindings=_bindings())
  body = Window(content=control, always_hide_cursor=True, wrap_lines=wrap)
  app = Application(
    layout=Layout(HSplit([_header(), body])),
    full_screen=False,
    mouse_support=False,
    style=merged,
  )

  return Question(app)