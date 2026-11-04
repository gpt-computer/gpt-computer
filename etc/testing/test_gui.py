import sys

from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from gptc.gui import run_gui

run_gui()
