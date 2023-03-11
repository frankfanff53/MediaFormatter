import argparse
from pathlib import Path
import subprocess


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n",
        "--name",
        help="Name of the Media Folder (Series Name)",
        required=True,
    )
    parser.add_argument(
        "--start",
        help="Start of the season",
        required=True,
    )

    parser.add_argument(
        "--end",
        help="End of the season",
        required=True,
    )

    parser.add_argument(
        "-s",
        "--style",
        help="Style to use",
        default="comedy",
    )

    args = parser.parse_args()

    for i in range(int(args.start), int(args.end) + 1):
        directory = f"{args.name}.S{i:02d}"
        if not Path(directory).exists():
            print(f"Directory {directory} does not exist.")
            continue
        print(f"Processing {directory}")
        result = subprocess.run([
            "merge",
            "-d",
            directory,
            "-s",
            args.style,
        ])
        if result.returncode != 0:
            print(f"Failed to process {directory}")
            exit(1)
