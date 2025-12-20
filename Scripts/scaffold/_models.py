from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Iterable, Mapping, Optional
from typing import Final
from typing import Sequence

from scaffold import Config


class Model:
    """
    Описание сущности 3D-модели
    """

    def __init__(
            self, 
            config: Config, 
            content_directory: Path, 
            model_file_extension: str,
        ) -> None:
        """
        :param config: Конфигурация проекта
        :param content_directory: Путь к директории файлов модели
        :param model_file_extension: Расширение файла модели
        """

        path = content_directory / self._nameless_filename_from_extension(model_file_extension)
        if not path.exists():
            raise FileNotFoundError(f"Model not found: {path}")

        self.content_directory: Final = content_directory
        """Путь к директории файлов модели"""

        self.identifier: Final = config.get_identifier_from_dir(self.content_directory) 
        """Идентификатор модели"""

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
        super().__init__(config, content_directory, config.part_model_extension)

        self.transitions: Final = self.__get_transitions(config)
        """Пути к файлам обменного формата модели"""

    def __get_transitions(self, config: Config):
        return self._search_by_extensions(config, config.part_model_transition_file_extensions)


class AssemblyUnitModel(Model):
    """
    Описание модели сборочной единицы
    """

    def __init__(self, config: Config, content_directory: Path):
        super().__init__(config, content_directory, config.assembly_unit_model_extension)

        self.parts: Final[Mapping] = self.__load_parts(config)
        """Модели деталей"""

        self.assembly_units: Final[Mapping] = self.__load_assembly_units(config)
        """Модели сборочных единиц"""

        self.export: Final = self.__load_export(config)
        """Параметры экспорта артефактов"""

    def __load_parts(self, config: Config) -> Mapping[str, PartModel]:
        parts = self._apply_on_paths(config, lambda path: PartModel(config, path), config.part_model_extension)
        
        return {
            part.content_directory.stem : part
            for part in parts
        }

    def __load_assembly_units(self, config: Config) -> Mapping[str, AssemblyUnitModel]:
        units = self._apply_on_paths(config, lambda path: AssemblyUnitModel(config, path), config.assembly_unit_model_extension)
        
        return {
            unit.content_directory.stem : unit
            for unit in units
        }

    def __load_export(self, config: Config) -> Optional[Mapping[str, int]]:
        p = self.content_directory / self._nameless_filename_from_extension(config.assembly_unit_model_export_settings_extension)
        
        if not p.exists():
            return None

        with open(p) as f:
            return json.load(f)