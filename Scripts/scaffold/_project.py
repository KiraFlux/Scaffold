from typing import Final

from scaffold import AssemblyUnitModel
from scaffold import Config
from scaffold import Model
from scaffold import PartModel
from scaffold._registry import Registry


class Project:
    """
    Экземпляр проекта.
    Взаимодействие с сущностями проекта осуществляются через данный класс
    """

    def __init__(self, config: Config) -> None:
        """Конфигурация проекта"""
        self.config: Final = config

        self._part_model_registry: Final[Registry[PartModel]] = Registry(
            lambda identifier: PartModel(
                config,
                config.content_path_from_identifier(identifier)
            )
        )

        self._assembly_unit_model_registry: Final[Registry[AssemblyUnitModel]] = Registry(
            lambda identifier: AssemblyUnitModel(
                config,
                config.content_path_from_identifier(identifier)
            )
        )

    def get_part_model(self, identifier: str) -> PartModel:
        """Получить описание модели детали по идентификатору"""
        return self._part_model_registry.get(identifier)

    def get_assembly_unit_model(self, identifier: str) -> AssemblyUnitModel:
        """Получить описание сборочной единицы по идентификатору"""
        return self._assembly_unit_model_registry.get(identifier)

    def get_model(self, identifier: str) -> Model:
        """Получить описание модели по идентификатору"""
        model = self.get_part_model(identifier)

        if model is not None:
            return model

        return self.get_assembly_unit_model(identifier)


def __test():
    from pathlib import Path

    scaffold_project = Project(Config.default(Path(r"D:/Projects/Klyax/Scaffold")))

    esp32_live_mini = scaffold_project.get_assembly_unit_model("Boards/Dev/ESP32/Live-Mini-Kit")

    print(esp32_live_mini.content_directory, esp32_live_mini.parts, esp32_live_mini.renders)

    return


if __name__ == '__main__':
    __test()
