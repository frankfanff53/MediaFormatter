import argparse
import os
from pathlib import Path

from tqdm import tqdm

import mediaformatter as mf

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        help="Input file path(s) to render",
    )

    parser.add_argument(
        "-c",
        "--colour",
        help="Colour to use",
        default=None,
    )

    parser.add_argument(
        "-fs",
        "--fontsize",
        help="Font size to use",
        default=None,
    )

    parser.add_argument(
        "-fn",
        "--fontname",
        help="Font name to use",
        default=None,
    )

    parser.add_argument(
        "-b",
        "--bold",
        help="Bold text",
        action="store_true",
    )

    args = parser.parse_args()

    base_path = Path(os.getcwd()) / args.input

    render_args = {
        "colour": args.colour,
        "fontsize": args.fontsize,
        "fontname": args.fontname,
        "bold": args.bold,
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
                    input_filepath.rename(backup_path)
                else:
                    print(
                        f"File {input_filepath.name} is not in supported subtitle format, aborted."
                    )
                    exit(1)
            else:
                for file in input_filepath.iterdir():
                    if file.suffix in set([".ass", ".srt"]):
                        file.rename(backup_path / file.name)
        else:
            if input_filepath.is_file():
                mf.render_to_subtitle(
                    backup_path, input_filepath, **render_args
                )
            else:
                for file in tqdm(
                    sorted(list(backup_path.iterdir())),
                    desc="Processing files",
                ):
                    mf.render_to_subtitle(
                        file, input_filepath / file.name, **render_args
                    )
        print("Finished processing.")
