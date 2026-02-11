import sys
import tkinter

try:
    import _tkinter as _tkinter  # C extension lives at top level on Windows
except ModuleNotFoundError:
    _tkinter = None

print("python:", sys.executable)
print("tkinter module path:", tkinter.__file__)
if _tkinter is None:
    print("_tkinter module path: (not found)")
else:
    print("_tkinter module path:", _tkinter.__file__)

