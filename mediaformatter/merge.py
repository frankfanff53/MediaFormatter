import os
import subprocess
from pathlib import Path

from tqdm import tqdm


def merge(input, subtitle_only):
    directory = Path(input)
    if not directory.exists():
        print(f"Directory {directory} does not exist.")
        exit(1)

    backup_directory = directory.parent / "backup" / "videos" / directory.name

    if not backup_directory.exists():
        backup_directory.mkdir(parents=True)
        for file in directory.iterdir():
            # backup file
            backup_file = backup_directory / file.name
            if not backup_file.exists():
                file.rename(backup_file)

    if not subtitle_only:
        for file in tqdm(
            sorted(backup_directory.glob("*.mkv")),
            desc="Dropping attachments and subtitles",
        ):
            # drop all attachments and subtitles
            filename = file.name
            modified_file = backup_directory / \
                filename.with_suffix(".mod.mkv").name
            commands = [
                "mkvmerge",
                "--no-subtitles",
                "--no-attachments",
                str(file),
                "-o",
                str(modified_file),
            ]
            result = subprocess.run(commands, capture_output=True)
            if result.returncode != 0:
                print(result.stderr.decode("utf-8"))
                exit(1)
            else:
                # delete original file
                file.unlink()
                # rename modified file
                modified_file.rename(backup_directory / filename)

    for file in tqdm(
        sorted(backup_directory.glob("*.[mkv|mp4]")),
        desc="Merging subtitles",
    ):

        commands = [
            "mkvmerge",
            "--no-subtitles",
            str(file),
            "--language",
            "0:chi",
            "--default-language",
            "chi",
            str(backup_directory / file.with_suffix(".ass").name),
            "-o",
            str(directory / file.with_suffix(".mkv").name),
        ]
        for attachment in os.listdir(Path(__file__).parent.parent / "fonts"):
            commands.extend(
                ["--attachment-mime-type", "application/x-truetype-font"]
            )
            commands.extend(
                [
                    "--attach-file",
                    str(Path(__file__).parent.parent / "fonts" / attachment),
                ]
            )
        result = subprocess.run(commands, capture_output=True)
        if result.returncode != 0:
            print(result.stderr.decode("utf-8"))
            exit(1)
        else:
            # delete original file
            file.unlink()
    print("Done.")
