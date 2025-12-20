from datetime import datetime
from itertools import chain
from pathlib import Path
import shutil
from typing import Callable, Final, Optional
from typing import Sequence

from scaffold._logger import Logger
from scaffold._models import AssemblyUnitModel
from scaffold._models import Model
from scaffold._models import PartModel
from scaffold._project import Project

class Job:

    def __init__(self) -> None:
        self._log: Final = Logger(self.__class__.__name__)


class ModelInfoJob(Job):
    
    def display(self, model: Model) -> None:
        self._display_model(model)

    def _display_model(self, model: Model) -> None:
        self._log.info(f"{model.identifier} {model.__class__.__name__} ({model.content_directory})")
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

        for model in chain(assembly_unit_model.parts.values(), assembly_unit_model.assembly_units.values()):
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


class MakeArtifactsJob(Job):

    def __init__(self, project: Project):
        super().__init__()
        self.project: Final = project

    def _link(self, s: str, path: str) -> str:
        return f"[`{s}`]({path})"

    def _img(self, src: str, height: int) -> str:
        return f'<img src="{src}" height="{height}">'

    def _date(self) -> str:
        return datetime.now().strftime("%Y.%m.%d")

    def _make_images_table(self, images: Sequence[Path], main_height: int) -> str:
        images_total = len(images)

        if images_total == 0:
            return ""

        main_image, *other_images = (i.name for i in images)

        main_img_tag = self._img(main_image, main_height)

        if len(other_images) == 0:
            return main_img_tag

        other_image_height = main_height // (images_total - 1)

        other_images_tags_string = '\n'.join((
            self._img(i, other_image_height) + "<br>"
            for i in other_images
        ))

        return f'\n<table>\n<tr valign="top">\n<td>\n{main_img_tag}\n</td>\n<td>\n{other_images_tags_string}\n</td>\n</tr>\n</table>\n'

    def _make_header(self, unit: AssemblyUnitModel, current_date: str) -> str:
        transitions = [
            ('zip', f'./../{unit.identifier}--{current_date}.zip'),
        ]

        transitions_string = ' '.join(
            self._link(name, path)
            for name, path in transitions
        )

        return f"""
# [{unit.identifier}](.)

[Выпуск от {current_date}](.) {transitions_string}

{self._make_images_table(unit.renders, 360)}

# Детали
    """

    def _make_part_block(self, part: PartModel, count: int, name_transformer: Callable[[str], str]) -> str:
        images_html = '\n'.join(
            f'<td>{self._img(i.name, 180)}</td>'
            for i in part.renders
        )

        def _makeExt(p: Path) -> str:
            return '.'.join(p.suffixes)

        transitions_string = ' '.join(
            self._link(_makeExt(t), name_transformer(t.name))
            for t in part.transitions
        )

        return f"""
<blockquote>

## {part.identifier} - {count} шт.

<table>
<tr valign="top">
{images_html}
</tr>
</table>

{transitions_string}

</blockquote>
    """

    def _make_footer(self) -> str:
        return "\n\nФайл сгенерирован инструментами проекта [Botix](https://github.com/KiraFlux/Botix)\n"

    def run(self, unit: AssemblyUnitModel) -> None:
        if unit.export is None:
            print("no export file")
            return
        
        unit_artifacts_directory = self.project.config.artifacts_directory / unit.identifier

        #

        if unit_artifacts_directory.exists():
            print("cleanup...")
            shutil.rmtree(unit_artifacts_directory)

        unit_artifacts_directory.mkdir(parents=True, exist_ok=True)

        #

        def _move(p: Optional[Path], name_transformer: Callable[[str], str] = str) -> None:
            if p:
                dst = unit_artifacts_directory / (name_transformer(p.parent.stem) + p.suffix)
                print(f"copy: {dst.name}")
                shutil.copyfile(p, dst)

        current_date = self._date()

        def _resolve_part_by_key(key: str) -> Optional[PartModel]:
            ret = self.project.get_part_model(key)

            if ret is not None:
                return ret
            
            return unit.parts.get(key)
            

        with open(unit_artifacts_directory / "README.md", "wt", encoding="utf-8") as out:
            out.write(self._make_header(unit, current_date))

            for part_id, count in unit.export.items():
                part = _resolve_part_by_key(part_id)

                if part is None:
                    print(f"fail: {part_id}")
                    continue

                def _name_transformer(s: str) -> str:
                    return f"{s}--{count}x--{unit.identifier}"

                for transition in part.transitions:
                    _move(transition, _name_transformer)

            out.write(self._make_footer())


        archive_path = self.project.config.artifacts_directory / f"{unit.identifier}--{current_date}"

        print(f"{archive_path=}")
        shutil.make_archive(
            base_name=str(archive_path),
            format="zip",
            root_dir=str(unit_artifacts_directory),
        )

        print(f"All done! {unit.identifier}")

        return
