from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from typing import Iterator
from typing import Sequence


@dataclass(frozen=True, kw_only=True)
class Config:
    """Конфигурация проекта"""

    models_directory: Path
    """Директория нативных моделей"""

    artifacts_directory: Path
    """Директория выходных артефактов"""

    # расширения

    part_model_extension: str = "m3d"
    """Расширение файла модели детали"""

    part_model_transition_file_extensions: Sequence[str]
    """Расширения файлов обменного формата для моделей"""

    assembly_unit_model_extension: str = "a3d"
    """Расширение файла модели сборочной единицы"""

    model_render_extensions: Sequence[str]
    """Расширения файлов рендеров модели"""

    @classmethod
    def default(
            cls,
            root_directory: Path
    ):
        """Настройки по умолчанию"""
        return cls(
            models_directory=root_directory / "Models",
            artifacts_directory=root_directory / "Artifacts",
            part_model_extension="m3d",
            assembly_unit_model_extension="a3d",
            model_render_extensions=(
                "jpg",
                "png",
                "jpeg",
            ),
            part_model_transition_file_extensions=(
                "stp",
                "step",
                "stl",
                "obj",
                "3mf",
                "gcode",
            )
        )

    @staticmethod
    def search_by_masks(target_folder: Path, masks: Iterable[str]) -> Iterator[Path]:
        """Yield files in target folder matching any of the provided glob masks"""
        for mask in masks:
            yield from target_folder.glob(mask)

    @staticmethod
    def iter_folders_contains_file_with_mask(folder: Path, mask: str) -> Iterator[Path]:
        """Yields folders from folder если данный folder содержит файл подходящий по mask"""
        if not folder.is_dir():
            raise NotADirectoryError(folder)

        for entry in folder.iterdir():
            if entry.is_dir():
                if any(entry.glob(mask)):
                    yield entry

    def content_path_from_identifier(self, identifier: str) -> Path:
        """Получить путь к директории модели из идентификатора"""
        path = Path(self.models_directory).joinpath(identifier)

        if path.exists():
            return path

        raise FileNotFoundError(f"Directory '{path=}' ({identifier=}) not exists")
