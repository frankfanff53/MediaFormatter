import argparse
import os
import re
from pathlib import Path

from tqdm import tqdm

if __name__ == "__main__":
    base_path = Path(os.getcwd())
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--format",
        choices=["ass", "mkv", "mp4"],
        help="File format to rename",
        required=True,
    )
    args = parser.parse_args()
    format = args.format

    if os.name == "nt":
        working_dir = str(base_path).split("\\")[-1]
    else:
        working_dir = str(base_path).split("/")[-1]
    renamed_files = sorted(
        [file for file in os.listdir(base_path) if file.endswith("." + format)]
    )

    if len(re.findall(r"S\d{2}", working_dir)) == 0:
        working_dir += ".S01"
    print("Renaming Schema:")
    renaming_schema = []
    for i, file in enumerate(renamed_files):
        renamed_file = f"{working_dir}E{i+1:0>2}.{format}"
        print(f"Renaming: {file} -> {renamed_file}")
        renaming_schema.append((file, renamed_file))
    choice = input("Continue? (y/n): ")
    if choice.lower() == "y":
        for file, renamed_file in tqdm(renaming_schema):
            os.rename(file, renamed_file)
        print("Done.")
    else:
        print("Aborted.")
