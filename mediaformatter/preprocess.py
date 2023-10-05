import json
import os
import subprocess
from pathlib import Path


def preprocess(directory, fonts, drop_attachments, with_jpn):
    base_path = Path(os.getcwd()) / directory
    if fonts:
        extra_fonts_path = Path(os.getcwd()) / fonts

    if with_jpn:
        jpn_audio_track_map = {}
        for file in sorted(base_path.glob("*.mkv")):
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

    for file in sorted(base_path.glob("*.mkv")):
        commands = [
            "mkvmerge",
            "--no-subtitles",
        ]
        if with_jpn:
            commands.extend(
                [
                    "--audio-tracks",
                    str(jpn_audio_track_map[file.stem]),
                ]
            )

        if drop_attachments:
            commands.append("--no-attachments")
        commands.append(str(base_path / file.name))
        for attachment in os.listdir(Path(__file__).parent.parent / "fonts"):
            commands.extend(
                [
                    "--attachment-mime-type",
                    "application/x-truetype-font",
                    "--attach-file",
                    str(Path(__file__).parent.parent / "fonts" / attachment),
                ]
            )
        if fonts:
            for font in extra_fonts_path.glob("*.[o|t]tf"):
                commands.extend(
                    [
                        "--attachment-mime-type",
                        "application/x-truetype-font",
                        "--attach-file",
                        str(extra_fonts_path / font.name),
                    ]
                )
        commands.extend(
            [
                "-o",
                str(base_path / (file.with_suffix("").name + "-modified.mkv"))
            ]
        )

        result = subprocess.run(commands)

        if result.returncode != 0:
            print(f"Failed to extract {file.name}")
        else:
            print(f"Successfully extracted {file.name}")
            file.unlink()
            # rename the modified file
            (base_path / (file.with_suffix("").name + "-modified.mkv")).rename(
                base_path / file.name,
            )
