import os
from numbers import Integral
from pathlib import Path, PurePath
from typing import Union

from tqdm import tqdm

from .assemble import render_to_subtitle


def style(
    input: Union[str, PurePath],
    colour: str,
    fontname: str,
    fontsize: Integral,
    bold: bool,
) -> None:
    base_path = Path(os.getcwd()) / input

    render_args = {
        "colour": colour,
        "fontsize": fontsize,
        "fontname": fontname,
        "bold": bold,
    }

    if not base_path.exists():
        print(f"File {base_path} does not exist.")
        exit(1)
    else:
        input_filepath = base_path
        backup_path = base_path.parent / "backup" / base_path.name
        if not backup_path.exists():
            backup_path.mkdir(parents=True)
            if input_filepath.is_file():
                if input_filepath.suffix in set(".ass", ".srt"):
                    input_filepath.rename(backup_path / input_filepath.name)
                else:
                    print(
                        f"File {input_filepath.name} is not in supported subtitle format, aborted."
                    )
                    exit(1)
            else:
                for file in input_filepath.iterdir():
                    if file.suffix in set([".ass", ".srt"]):
                        file.rename(backup_path / file.name)
        for file in tqdm(
            sorted(list(backup_path.iterdir())),
            desc="Processing files",
        ):
            render_to_subtitle(file, input_filepath / file.name, **render_args)
        print("Finished processing.")
