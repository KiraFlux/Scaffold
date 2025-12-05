from pathlib import Path

from botix.tools import iterDirs

p = Path('/Botix-Scripts/test/Mock/Модели/Конструктив')

print(tuple(iterDirs(p)))
