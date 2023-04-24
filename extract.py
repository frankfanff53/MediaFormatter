import argparse
import json
import subprocess
from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        default=".",
        help="Directory to extract subtitles from",
    )

    args = parser.parse_args()

    base_path = Path(args.directory)
    if not base_path.is_dir():
        raise ValueError(f"{base_path} is not a directory.")
        exit(1)
    if not base_path.exists():
        raise ValueError(f"{base_path} does not exist.")
        exit(1)

    for file in base_path.iterdir():
        if file.is_file() and file.suffix == ".mkv":
            result = subprocess.run(
                ["mkvmerge", "-J", file.name],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                mkv_info = json.loads(result.stdout)
                chi_track_ids = []
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
