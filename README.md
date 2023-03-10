# Python Media Formatter

A python library for reformatting the subtitle `.ass` files and wrapping subtitles to the target videos.

## Installation

To install this library you need to use the following command lines:

```bash
git clone git@github.com:frankfanff53/MediaFormatter.git
cd MediaFormatter
make install
```

## Core Functionalities

- [x] Parse a subtitle file

### Usage of `mediaformatter.parse_title`

```python
import mediaformatter as mf
from pathlib import Path


if __name__ == "__main__":
    base_path = Path(__file__).parent
    doc = mf.parse_subtitle(
        base_path / "config" / "reference.ass"
    )
    if doc is None:
        print("Failed to parse subtitle file.")
        exit()
    else:
        print("Successfully parsed subtitle file.")

    print("Event count:", len(doc.events))
    print(doc.events[0].text)
```

If parsing is successful, you should expect the following printed result in teh console:

```txt
Successfully parsed subtitle file.
Event count: 426
《生活大爆炸》  前情提要\N{\fnTahoma\b0}Previously on The Big Bang Theory...{\r}
```

which is the last line that shows the first line of the dialog.

- [x] Extract the subtitles into different languages

### Usage of `mediaformatter.split_subtitle`

```python
base_path = Path(__file__).parent
split = mf.split_subtitle(
    base_path / "config" / "reference.ass"
)

print("English:")
for line in split["ENGLISH"][:5]:
    print(line["start"], line["end"], line["dialog"], sep=", ")
```

If the subtitle splitting is successful, you should expect the printed result in the console:

```txt
English:
0:00:02.160000, 0:00:04.060000, Previously on The Big Bang Theory...
0:00:03.960000, 0:00:07.840000, We now pronounce you husband and wife!
0:00:10.050000, 0:00:12.050000, I love this part!
0:00:12.050000, 0:00:13.650000, Me, too!
0:00:13.880000, 0:00:17.390000, I have strongly mixed feelings!
```

which is the first five English dialogs in the subtitle, with start and end timestamps.

- [ ] Reformat the subtitle with the default configuration
- [ ] Reformat the subtitle with the custom configuration
- [ ] Merge the subtitle files to the corresponding video file
