from yaspin import yaspin
from functools import wraps
from langchain_core.runnables import RunnableLambda, Runnable, RunnableConfig

def with_spinner_chain(runnable: Runnable, message: str):
  """
  Wraps a LangChain Runnable to display a spinner during its `invoke` call.

  Args:
    runnable: The LangChain runnable to wrap.
    message: The text to display while the runnable is invoking.

  Returns:
    A new RunnableLambda that includes the spinner logic.
  """
  def _invoke_with_spinner(input, config: RunnableConfig | None = None):
    with yaspin(text=message) as spinner:
      try:
        out = runnable.invoke(input, config=config)
        spinner.ok("✅")
        return out
      except Exception as e:
        spinner.fail("💥")
        raise e

  return RunnableLambda(_invoke_with_spinner)

def with_spinner(message: str):
  """
  A decorator factory that adds a spinner to a function.

  Args:
    message: The text to display while the spinner is active.
  """
  def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
      with yaspin(text=message) as spinner:
        try:
          result = func(*args, **kwargs)
          spinner.ok("✅")
          return result
        except Exception as e:
          spinner.fail("💥")
          raise e

    return wrapper

  return decorator
