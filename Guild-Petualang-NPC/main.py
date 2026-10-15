import os
import subprocess
import sys

def buka_gui():
    folder = os.path.dirname(os.path.abspath(__file__))
    subprocess.run([sys.executable, os.path.join(folder, "gui.py")], cwd=folder)

if __name__ == "__main__":
    buka_gui()
