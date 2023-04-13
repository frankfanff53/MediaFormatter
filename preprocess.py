import argparse
import json
import os
import subprocess
from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--directory",
        help="Directory to process",
    )

    parser.add_argument(
        "--fonts",
        help="Directory containing fonts",
        default=None,
    )

    parser.add_argument(
        "--drop-attachments",
        help="Drop attachments",
        action="store_true",
    )

    parser.add_argument(
        "--with-jpn",
        help="Extract only files with Japanese audio",
        action="store_true",
    )

    args = parser.parse_args()
    base_path = Path(os.getcwd()) / args.directory
    if args.fonts:
        fonts_path = Path(os.getcwd()) / args.fonts

    if args.with_jpn:
        jpn_audio_track_map = {}
        for file in base_path.iterdir():
            if file.is_file() and file.suffix == ".mkv":
                result = subprocess.run(
                    ["mkvmerge", "-J", str(base_path / file.name)],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    mkv_info = json.loads(result.stdout)
                    for track in mkv_info["tracks"]:
                        if track["type"] == "audio":
                            if track["properties"]["language"] == "jpn":
                                jpn_audio_track_map[file.stem] = track["id"]

    for file in base_path.iterdir():
        if file.is_file() and file.suffix == ".mkv":
            if args.with_jpn:
                commands = [
                    "mkvmerge",
                    "--audio-tracks",
                    str(jpn_audio_track_map[file.stem]),
                    "--no-subtitles",
                ]
            else:
                commands = [
                    "mkvmerge",
                    "--no-subtitles",
                ]

            if args.drop_attachments:
                commands.append("--no-attachments")
            commands.append(str(base_path / file.name))
            if args.fonts:
                for font in fonts_path.iterdir():
                    commands.extend(
                        [
                            "--attachment-mime-type",
                            "application/x-truetype-font",
                            "--attach-file",
                            str(fonts_path / font.name),
                        ]
                    )
            commands.extend(
                ["-o", str(base_path / (file.stem + "-modified.mkv"))]
            )

            result = subprocess.run(commands)

            if result.returncode != 0:
                print(f"Failed to extract {file.name}")
            else:
                print(f"Successfully extracted {file.name}")
                file.unlink()
                # rename the modified file
                os.rename(
                    base_path / (file.stem + "-modified.mkv"),
                    base_path / file.name,
                )
