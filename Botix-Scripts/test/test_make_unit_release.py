import shutil
from datetime import datetime
from pathlib import Path
from typing import Callable
from typing import Optional
from typing import Sequence

from botix.core.entities import PartEntity
from botix.core.entities import UnitEntity
from botix.core.key import UnitKey
from botix.core.registries import PartEntityRegistry
from botix.core.registries import PartsSectionRegistry
from botix.core.registries import UnitEntityRegistry
from botix.impl.loaders import ProjectEntityLoader


def _link(s: str, path: str) -> str:
    return f"[`{s}`]({path})"


def _img(src: str, height: int) -> str:
    return f'<img src="{src}" height="{height}">'


def _date() -> str:
    return datetime.now().strftime("%Y.%m.%d")


def _makeImagesTable(images: Sequence[Path], main_height: int) -> str:
    images_total = len(images)

    if images_total == 0:
        return ""

    main_image, *other_images = (i.name for i in images)

    main_img_tag = _img(main_image, main_height)

    if len(other_images) == 0:
        return main_img_tag

    other_image_height = main_height // (images_total - 1)

    other_images_tags_string = '\n'.join((
        _img(i, other_image_height) + "<br>"
        for i in other_images
    ))

    return f'\n<table>\n<tr valign="top">\n<td>\n{main_img_tag}\n</td>\n<td>\n{other_images_tags_string}\n</td>\n</tr>\n</table>\n'


def _makeHeader(unit: UnitEntity, current_date: str) -> str:
    transitions = [
        ('zip', f'./../{unit.metadata.getEntityName()}--{current_date}.zip'),
    ]

    if unit.transition_assembly:
        transitions.append(('step', unit.transition_assembly.name))

    transitions_string = ' '.join(
        _link(name, path)
        for name, path in transitions
    )

    return f"""
# [{unit.metadata.getDisplayName()} {unit.metadata.getDisplayVersion()}](.)

[Выпуск от {current_date}](.) {transitions_string}

{_makeImagesTable(unit.metadata.images, 360)}

# Детали

"""


def _makePartBlock(part: PartEntity, count: int, name_transformer: Callable[[str], str]) -> str:
    images_html = '\n'.join(
        f'<td>{_img(i.name, 180)}</td>'
        for i in part.metadata.images
    )

    def _makeExt(p: Path) -> str:
        first, *others = (s.strip('.') for s in p.suffixes)
        if len(others) == 0:
            return first

        return f'{' '.join(others)} ({first})'

    transitions_string = ' '.join(
        _link(_makeExt(t), name_transformer(t.name))
        for t in part.transitions
    )

    return f"""
<blockquote>

## {part.metadata.getDisplayName()} - {count} шт.

<table>
<tr valign="top">
{images_html}
</tr>
</table>

{transitions_string}

</blockquote>
"""


def _makeFooter() -> str:
    return "\n\nФайл сгенерирован инструментами проекта [Botix](https://github.com/KiraFlux/Botix)\n"


def _makeUnitAssemblyFiles(output_folder: Path, unit: UnitEntity, parts_registry: PartsSectionRegistry) -> None:
    assert unit.attributes is not None, f"Attributes (.unit) must exists"

    unit_release_folder = output_folder / unit.metadata.getEntityName()

    #

    if unit_release_folder.exists():
        print("cleanup...")
        shutil.rmtree(unit_release_folder)

    unit_release_folder.mkdir(parents=True)

    #

    def _move(p: Optional[Path], name_transformer: Callable[[str], str] = str) -> None:
        if p:
            dst = unit_release_folder / name_transformer(p.name)
            print(f"copy: {dst.name}")
            shutil.copyfile(p, dst)

    current_date = _date()

    with open(unit_release_folder / "README.md", "wt", encoding="utf-8") as out:

        out.write(_makeHeader(unit, current_date))

        _move(unit.transition_assembly)

        for image in unit.metadata.images:
            _move(image)

        part_registry = PartEntityRegistry(unit, parts_registry)

        for part_key, count in unit.attributes.part_count_map.items():
            part: Optional[PartEntity] = part_registry.get(part_key)

            if part is None:
                print(f"cannot find: {part_key}")

            else:
                def _nameTransformer(s: str) -> str:
                    return f"{s}--{count}x--{unit.metadata.getEntityName()}--Botix"

                out.write(_makePartBlock(part, count, _nameTransformer))

                for transition in part.transitions:
                    _move(transition, _nameTransformer)

                for image in part.metadata.images:
                    _move(image)

        out.write(_makeFooter())

    #

    archive_path = output_folder / f"{unit.metadata.getEntityName()}--{current_date}"

    print(f"{archive_path=}")
    shutil.make_archive(
        base_name=str(archive_path),
        format="zip",
        root_dir=str(unit_release_folder),
        base_dir="../src"
    )

    print(f"All done! {unit.metadata.getEntityName()}")

    return


def _main() -> None:
    root = Path("/")
    output_folder = root / "Производство"

    project = ProjectEntityLoader(root / "Модели").load()
    units = UnitEntityRegistry(project)
    parts = PartsSectionRegistry(project)

    print("\n".join(map(str, units.getAll().keys())))

    def _make(k: str):
        unit = units.get(UnitKey(k))
        _makeUnitAssemblyFiles(output_folder, unit, parts)

    # _make("Модули/Датчик-Расстояния-Sharp-2YA21F4XB-v1")
    # _make("Шасси/MidiQ-Всош-v2")
    _make("Модули/Манипулятор-2DOF-v2")

    return


if __name__ == "__main__":
    _main()
