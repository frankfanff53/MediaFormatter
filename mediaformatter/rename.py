import os
import re
from pathlib import Path

from tqdm import tqdm


def rename(
    format: str,
    movie: bool,
    start: int = 1,
    name: str = None,
) -> None:
    base_path = Path().cwd()
    working_dir = base_path.name if not name else name
    renamed_files = sorted(base_path.glob(f"*.{format}"))

    if len(re.findall(r"S\d{2}", working_dir)) == 0 and not movie:
        working_dir += ".S01"
    print("Renaming Schema:")
    renaming_schema = []
    for i, file in enumerate(renamed_files):
        if movie:
            renamed_file = f"{working_dir}.{format}"
        else:
            renamed_file = f"{working_dir}E{i+start:0>2}.{format}"
        print(f"Renaming: {file} -> {renamed_file}")
        renaming_schema.append((file, renamed_file))
    choice = input("Continue? (y/n): ")
    if choice.lower() == "y":
        for file, renamed_file in tqdm(renaming_schema):
            os.rename(file, renamed_file)
        print("Done.")
    else:
        print("Aborted.")
