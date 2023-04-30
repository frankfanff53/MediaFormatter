import json
import os
import subprocess
from pathlib import Path


def preprocess(directory, fonts, drop_attachments, with_jpn):
    base_path = Path(os.getcwd()) / directory
    if fonts:
        fonts_path = Path(os.getcwd()) / fonts

    if with_jpn:
        jpn_audio_track_map = {}
        for file in sorted(base_path.iterdir()):
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

    for file in sorted(base_path.iterdir()):
        if file.is_file() and file.suffix == ".mkv":
            if with_jpn:
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

            if drop_attachments:
                commands.append("--no-attachments")
            commands.append(str(base_path / file.name))
            if fonts:
                for font in fonts_path.iterdir():
                    if font.is_file() and font.suffix in set([".ttf", ".otf"]):
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
