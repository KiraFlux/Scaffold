from pathlib import Path
from typing import Callable, Final, Optional

from scaffold._models import AssemblyUnitModel
from scaffold._config import Config
from scaffold._models import Model
from scaffold._models import PartModel
from scaffold._registry import Registry


class Project:
    """
    Экземпляр проекта.
    Взаимодействие с сущностями проекта осуществляются через данный класс
    """

    @classmethod
    def default(cls, root_directory: Path):
        return cls(Config.default(root_directory))
        

    def __init__(self, config: Config) -> None:
        """Конфигурация проекта"""
        self.config: Final = config
        

        def _load_model[T: Model](identifier: str, provider: Callable[[Config, Path], T]) -> Optional[T]:
            p = config.content_path_from_identifier(identifier)
            
            if p is None:
                return None

            return provider(config, p)

        def _make_provider[T: Model](cls: type[T]) -> Callable[[str], Optional[T]]:
            return lambda identifier: _load_model(identifier, lambda path, config: cls(path, config))

        self._part_model_registry: Final[Registry[PartModel]] = Registry(
            item_provider=_make_provider(PartModel)
        )

        self._assembly_unit_model_registry: Final[Registry[AssemblyUnitModel]] = Registry(
            item_provider=_make_provider(AssemblyUnitModel)
        )

    def get_part_model(self, identifier: str) -> Optional[PartModel]:
        """Получить описание модели детали по идентификатору"""
        return self._part_model_registry.get(identifier)

    def get_assembly_unit_model(self, identifier: str) -> Optional[AssemblyUnitModel]:
        """Получить описание сборочной единицы по идентификатору"""
        return self._assembly_unit_model_registry.get(identifier)

    def get_model(self, identifier: str) -> Optional[Model]:
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
