from yaspin import yaspin
from langchain_core.runnables import RunnableLambda

def with_spinner(runnable, label):
  def _invoke(input, config=None):
    with yaspin(text=label) as spinner:
      out = runnable.invoke(input, config=config)
      spinner.ok("✅ ")
      return out
  return RunnableLambda(_invoke)
