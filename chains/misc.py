from langchain_core.runnables import RunnableLambda
from typing import List, Any

def _filter_none(xs: List[Any]) -> List[Any]:
  return [x for x in xs if x is not None]

filter_none = RunnableLambda(_filter_none)

to_dict = RunnableLambda(lambda input: input.model_dump())

def flatten(keys_to_flatten: tuple[str, ...]):
  def _flatten(x: dict[str, Any]) -> dict[str, Any]:
    return {
      **{k: v for k, v in x.items() if k not in keys_to_flatten},
      **{
        kk: vv
        for key in keys_to_flatten
        if key in x and isinstance(x[key], dict)
        for kk, vv in x[key].items()
      }
    }

  return RunnableLambda(_flatten)
