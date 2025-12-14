from itertools import chain
from pathlib import Path
from typing import Final
from typing import Sequence

from scaffold._logger import Logger
from scaffold._models import AssemblyUnitModel
from scaffold._models import Model
from scaffold._models import PartModel


class ModelInfoJob:

    def __init__(self) -> None:
        self._log: Final = Logger(self.__class__.__name__)

    def display(self, model: Model) -> None:
        self._display_model(model)

    def _display_model(self, model: Model) -> None:
        self._log.info(f"{model.__class__.__name__} {model.content_directory!s}")
        self._display_list("Renders", model.renders)

        if isinstance(model, PartModel):
            self._display_part_model(model)
        elif isinstance(model, AssemblyUnitModel):
            self._display_assembly_unit_model(model)
        else:
            raise TypeError(f"Unsupported {model.__class__=}")

    def _display_part_model(self, part_model: PartModel) -> None:
        self._display_list("Transitions", part_model.transitions)

    def _display_assembly_unit_model(self, assembly_unit_model: AssemblyUnitModel) -> None:
        self._log.push()

        for model in chain(assembly_unit_model.parts, assembly_unit_model.assembly_units):
            self._display_model(model)

        self._log.pop()

    def _display_list(self, label: str, paths: Sequence[Path]) -> None:
        items = len(paths)

        if items == 0:
            return

        self._log.info(f"{label} ({items})")

        self._log.push()

        for path in paths:
            self._log.info(path.name)

        self._log.pop()
        self._log.info("")
