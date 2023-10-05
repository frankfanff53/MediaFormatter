import json
import os
import subprocess
from pathlib import Path


def extract(directory):
    base_path = Path(os.getcwd()) / directory

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
                    if track["type"] == "subtitles":
                        track_id = track["id"]
                        try:
                            track_name = track["properties"]["track_name"]
                        except KeyError:
                            track_name = track["properties"]["language"]
                        codec = track["codec"]
                        if "substationalpha" in codec.lower():
                            subtitle_suffix = "ass"
                        elif "srt" in codec.lower():
                            subtitle_suffix = "srt"
                        else:
                            raise ValueError(
                                f"Subtitle format {codec} is not supported."
                            )

                        result = subprocess.run(
                            [
                                "mkvextract",
                                "tracks",
                                file.name,
                                f"{track_id}:{file.stem}_{'_'.join(track_name.split())}.{subtitle_suffix}",
                            ],
                        )
                        if result.returncode != 0:
                            print(f"Failed to extract {file.name}")
