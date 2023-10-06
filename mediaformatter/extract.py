import json
import subprocess
from pathlib import Path


def extract(directory):
    base_path = Path().cwd() / directory

    for file in sorted(base_path.glob("*.mkv")):
        result = subprocess.run(
            ["mkvmerge", "-J", str(file)],
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
                        sub_suffix = "ass"
                    elif "srt" in codec.lower():
                        sub_suffix = "srt"
                    else:
                        raise ValueError(
                            f"Subtitle format {codec} is not supported."
                        )

                    assert isinstance(file, Path)
                    result = subprocess.run(
                        [
                            "mkvextract",
                            "tracks",
                            str(file),
                            f"{track_id}:"
                            f"{file.with_suffix(f'.{track_name}.{sub_suffix}')}"
                        ],
                    )
                    if result.returncode != 0:
                        print(f"Failed to extract {file.name}")
