import os

def clear():
  """
  Clear terminal screen.
  """
  os.system('cls' if os.name == 'nt' else 'clear')
