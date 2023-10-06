import json
import re
from datetime import timedelta
from pathlib import Path

import ass

base_path = Path(__file__).parent.parent
with open(base_path / "config" / "encodings.json", "r") as f:
    ENCODINGS = json.load(f)
ENCODINGS = [encoding.replace("_", "-") for encoding in ENCODINGS]


def parse_subtitle(path, available_encodings=ENCODINGS):
    """Parse subtitle file.

    Args:
        path (Union[str, PurePath]): Path to the subtitle file.
        available_encodings (Optional[List[str]], optional): List of available encodings. Defaults to ENCODINGS.

    Returns:
        Parsed subtitle file if parsing success and None otherwise.
    """
    parse_success = False
    for encoding in available_encodings:
        try:
            with open(path, "r", encoding=encoding) as f:
                doc = ass.parse(f)
                parse_success = True
                break
        except Exception:
            continue

    if parse_success:
        return doc
    else:
        raise Exception("Failed to parse subtitle file.")


def split_subtitle(doc, align, languages=['ENGLISH', 'CHINESE']):
    """Split subtitle file into different languages.

    Args:
        path (Union[str, PurePath]): Path to the subtitle file.
        align (Union[float, None]): Time interval to align the video and subtitle.
        languages (Optional[str], optional): List of languages to split. Defaults to ['ENGLISH', 'CHINESE'].

    Returns:
        A dictionary of language and list of dialogues.
    """
    if len(languages) == 0:
        raise ValueError("No language specified.")
    split = {language: [] for language in languages}

    prev_end = None
    for i, event in enumerate(doc.events):
        # extract the text
        dialog = event.text
        if re.search(r"\\pos|\\move|\\fad", dialog):
            lines = [dialog]
        else:
            lines = dialog.split(r'\N')
        start, end = event.start, event.end
        if align:
            align = float(align)
            start += timedelta(seconds=align)
            end += timedelta(seconds=align)

        if prev_end and start < prev_end:
            start = prev_end
        prev_end = end

        for j, line in enumerate(lines):
            style = ""
            # handle with special styles
            if re.search(r"\\pos|\\move|\\fad", line):
                # extract the part with \pos, \move, \fad only
                style = re.search(
                    r"\{[^\{]*?(\\pos|\\fad|\\move)[^\{]*\}", line
                ).group()
                # remove the original style from the text
                line = re.sub(r"\{.*?\}", "", line)
                # check if the style has a border
                border = re.search(r"\\bord\d+", style)
                if border:
                    # replace the border with 1
                    style = re.sub(r"\\bord\d+", r"\\bord1", style)
                else:
                    # remove the closing bracket and add border
                    style = style[:-1] + r"\bord1}"
                # check if the style has a border colour
                border_colour = re.search(r"\\3c&H[0-9a-fA-F]{6}&", style)
                if border_colour:
                    # replace the border colour with black
                    style = re.sub(r"\\3c&H[0-9a-fA-F]{6}&", r"\\3c&H000000&", style)
                else:
                    # remove the closing bracket and add border colour
                    style = style[:-1] + r"\3c&H000000&}"
            else:
                if line.strip() == "":
                    continue
                # check if numberpad \an<alignment> is used
                numpad = re.search(r"\\an\d", line)
                if numpad:
                    style = "{" + numpad.group() + "}"
                # remove all styles
                line = re.sub(r"\{.*?\}", "", line)
                # check if line is in pattern <i></i> or </i><i> (italics)
                if re.match(r"<i>.*</i>", line) or re.match(
                    r"</i>.*<i>", line
                ):
                    # remove the <i></i> tags
                    line = re.sub(r"<i>|</i>", "", line)
                    # add italics
                    style = r"{\i1}" if len(style) == 0 else style[:-1] + r"\i1}"

            # detect the language
            # 1st principle: if the line contains any Chinese characters, it is Chinese
            if re.search(u"[\u4e00-\u9fff]", line):
                language = "CHINESE"
            elif re.match(r"^[0-9.,!?;:'\"\s\-]*$", line):
                language = "CHINESE" if j == 0 else "ENGLISH"
            else:
                language = "ENGLISH"

            # add the line to the corresponding language
            split[language].append(
                {
                    "start": start,
                    "end": end,
                    "dialog": style + line,
                }
            )
    return split
