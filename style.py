import argparse
from pathlib import Path

from tqdm import tqdm

import mediaformatter as mf

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--directory",
        help="Directory to process",
    )
    parser.add_argument(
        "-i",
        "--input",
        help="Input file to process",
    )
    parser.add_argument(
        "-s",
        "--style",
        help="Style to use",
        default="comedy",
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
    )

    parser.add_argument(
        "--ignore-last-lines",
        help="Ignore last lines",
        type=int,
        default=0,
    )

    args = parser.parse_args()
    style = args.style
    font_size = args.fontsize

    if style == "comedy":
        color = None
        font_name = "LXGWWenKaiMono-Bold"
        bold = False
        font_size = None
    elif style == "movie":
        color = "black"
        font_name = "LXGWWenKaiMono-Bold"
        bold = True
    elif style == "thriller":
        color = "green"
        font_name = "LXGWWenKaiMono-Bold"
        bold = True

    if args.colour:
        color = args.colour

    if not args.directory:
        input_file = Path(args.input)
        if not input_file.exists():
            print(f"File {input_file} does not exist.")
            exit(1)
        # backup file
        backup_file = input_file.parent / "backup" / input_file.name
        if not backup_file.exists():
            backup_file.parent.mkdir(parents=True)
            input_file.rename(backup_file)

        mf.render_to_subtitle(
            backup_file, input_file, color, font_name, bold, font_size, args.ignore_last_lines
        )
    else:
        directory = Path(args.directory)

        if not directory.exists():
            print(f"Directory {directory} does not exist.")
            exit(1)

        # set up backup directory
        backup_dir = directory.parent / "backup" / directory.name

        if not backup_dir.exists():
            backup_dir.mkdir(parents=True)

            # move all .ass files from directory to backup directory
            for file in directory.iterdir():
                # check if file path ends with .ass extension
                if str(file).endswith(".ass"):
                    # move file to backup directory
                    file.rename(backup_dir / file.name)

        # process the backup directory
        for file in tqdm(
            sorted(list(backup_dir.iterdir())), desc="Processing files"
        ):
            mf.render_to_subtitle(
                file, directory / file.name, color, font_name, bold, font_size, args.ignore_last_lines
            )

        print("Finished processing files.")
