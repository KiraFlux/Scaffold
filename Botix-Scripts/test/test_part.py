from pathlib import Path

from botix.impl.loaders import PartEntityLoader

root = Path("/")

p = root / "Модели/Шасси/MidiQ/Стенка-Задняя-v2.m3d"

part = PartEntityLoader(p).load()
print(part.transitions)
