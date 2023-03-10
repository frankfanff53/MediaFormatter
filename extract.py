import json
import os
import subprocess
from pathlib import Path

from tqdm import tqdm

if __name__ == "__main__":
    base_path = Path(os.getcwd())
    for file in tqdm(base_path.iterdir()):
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
                        if track["properties"]["language"] == "chi":
                            chi_track_ids.append(track["id"])
                if len(chi_track_ids) > 0:
                    result = subprocess.run(
                        [
                            "mkvextract",
                            "tracks",
                            file.name,
                            f"{chi_track_ids[0]}:{file.stem}.ass",
                        ],
                    )
                    if result.returncode != 0:
                        print(f"Failed to extract {file.name}")
