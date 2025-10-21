from typing import Any, List, Callable, Optional
import ui
import os

def list_editor(
  message: str,
  items: List[Any],
  display_fn: Callable[[Any], None],
  modify_fn: Callable[[Any], Optional[Any]],
  label_fn: Callable[[Any], str] = lambda x: str(x)
) -> List[Any]:
  """
  Generic list editor: Add, edit, or delete items in a list.
  - message: Prompt message.
  - items: The list to edit (mutable).
  - display_fn: Function to display full contents of an item.
  - modify_fn: Function to generate display labels.
  - label_fn: Function to create/edit an item.
  Returns the updated list.
  """
  while True:
    options = []
    label_to_index = {}

    for i, item in enumerate(items):
      label = original_label = label_fn(item)
      count = 1

      while label in label_to_index:
        label = f"{original_label} ({count})"
        count += 1

      label_to_index[label] = i
      options.append((label, ["Show", "Edit", "Delete"]))
    
    options += ["New", "Exit"]

    ui.clear()
    match ui.accordion(message, options).ask():
      case (label, "Show"):
        item_idx = label_to_index[label]
        ui.clear()
        display_fn(items[item_idx])
        ui.press_any_key_to_continue().ask()
      case (label, "Edit"):
        item_idx = label_to_index[label]
        ui.clear()
        updated_item = modify_fn(items[item_idx])
        if updated_item is not None:
          items[item_idx] = updated_item
      case (label, "Delete"):
        item_idx = label_to_index[label]
        if ui.confirm(f"Are you sure you want to delete '{label}'?").ask():
          items.pop(item_idx)
      case "New":
        ui.clear()
        new_item = modify_fn(None)
        if new_item is not None:
          items.append(new_item)
      case "Exit":
        break
      case None:
        break

  return items
