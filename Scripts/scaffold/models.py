from __future__ import annotations

from pathlib import Path
from typing import Callable
from typing import Final
from typing import Sequence

from scaffold.config import Config


class Model:
    """
    Описание сущности 3D-модели
    """

    def __init__(self, config: Config, content_directory: Path) -> None:
        """
        :param content_directory: Путь к директории файлов модели
        """

        self.content_directory: Final = content_directory
        """Путь к директории файлов модели"""

        self.renders: Final = self.__get_renders(config)
        """Пути к рендерам модели"""

    @classmethod
    def _nameless_filename_from_extension(cls, extension: str) -> str:
        return f".{extension}"

    @classmethod
    def _mask_from_extension(cls, extension: str) -> str:
        return f"*{cls._nameless_filename_from_extension(extension)}"

    def _apply_on_paths[T](self, config: Config, on_path: Callable[[Path], T], extension: str) -> Sequence[T]:
        return tuple(map(
            on_path,
            config.iter_folders_contains_file_with_mask(self.content_directory, self._nameless_filename_from_extension(extension))
        ))

    def _search_by_extensions(self, config: Config, extensions: Sequence[str]) -> Sequence[Path]:
        return tuple(config.search_by_masks(
            self.content_directory,
            map(self._mask_from_extension, extensions)
        ))

    def __get_renders(self, config: Config):
        return self._search_by_extensions(config, config.model_render_extensions)


class PartModel(Model):
    """
    Описание модели детали
    """

    def __init__(self, config: Config, content_directory: Path):
        super().__init__(config, content_directory)

        self.transitions: Final = self.__get_transitions(config)
        """Пути к файлам обменного формата модели"""

    def __get_transitions(self, config: Config):
        return self._search_by_extensions(config, config.part_model_transition_file_extensions)


class AssemblyUnitModel(Model):
    """
    Описание модели сборочной единицы
    """

    def __init__(self, config: Config, content_directory: Path):
        super().__init__(config, content_directory)

        self.parts: Final = self.__get_parts(config)
        """Модели деталей"""

        self.assembly_units: Final = self.__get_assembly_units(config)
        """Модели сборочных единиц"""

    def __get_parts(self, config: Config) -> Sequence[Model]:
        return self._apply_on_paths(config, lambda path: Model(config, path), config.part_model_extension)

    def __get_assembly_units(self, config: Config) -> Sequence[AssemblyUnitModel]:
        return self._apply_on_paths(config, lambda path: AssemblyUnitModel(config, path), config.assembly_unit_model_extension)
