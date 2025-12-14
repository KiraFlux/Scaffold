from abc import ABC
from typing import Final

from scaffold import Project


class Job(ABC):
    """Работа выполняемая над проектом"""

    def __init__(self, project: Project) -> None:
        self.project: Final = project


class DisplayModelInfo(Job):

    def run(self, identifier: str) -> str:
        model = self.project.get_model(identifier)

        return model.__str__()
