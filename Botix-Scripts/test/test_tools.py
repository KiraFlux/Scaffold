from pathlib import Path

from botix.tools import iterDirs

root = Path("/") / "Модели"

dirs = iterDirs(root, 1)

for d in dirs:
    print(d)
