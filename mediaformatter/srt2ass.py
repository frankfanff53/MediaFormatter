import json
import os
import re
from datetime import datetime
from pathlib import Path

from ass import Dialogue, Style
from ass.data import Color
from tqdm import tqdm

from .assemble import get_colour
from .utils import parse_subtitle


def format_timestring(time_string):
    datetime_obj = datetime.strptime(time_string, "%H:%M:%S.%f")
    return datetime_obj.strftime("%H:%M:%S.%f")[:-4]


def srt2ass(directory, style_name, font_size, colour):
    base_path = Path().cwd() / directory

    for file in tqdm(
        sorted(base_path.glob("*.srt")), desc="Converting srt file(s)"
    ):
        output_file = file.with_suffix(".ass").name
        convert(
            input=file,
            output=base_path / output_file,
            style_name=style_name,
            font_size=font_size,
            colour=colour,
        )
    print("Finish converting srt file(s).")


def convert(
    input,
    output,
    style_name,
    font_size,
    colour,
):
    subtitle_path = input
    base_path = Path(__file__).parent.parent

    with open(subtitle_path, "r", encoding="utf-8-sig") as f:
        contents = f.readlines()

    dialog_start_index, dialog_end_index = 1, 1

    dialogs = []

    next_is_start_of_dialog = False
    for i, line in enumerate(contents):
        if i == 0:
            continue
        if line.replace("\n", "").isdigit() and next_is_start_of_dialog:
            next_is_start_of_dialog = False
            dialog_end_index = i
            dialog = contents[dialog_start_index:dialog_end_index]
            dialog = [
                line.replace("\n", "") for line in dialog if line != "\n"
            ]
            dialog_start_index = dialog_end_index + 1
            timerange, text = dialog[0].replace(",", "."), " ".join(dialog[1:])
            start, end = timerange.split(" --> ")
            # format the styled text with black border
            style = re.search(
                r"\{[^\{]*?(\\pos|\\fad|\\move)[^\{]*\}", text
            )
            text = re.sub(r"\{.*?\}", "", text)
            if style:
                style = style.group()
                # check if the style already has a border
                border = re.search(r"\\bord\d", style)
                if border is None:
                    style = style.replace(
                        "}",
                        r"\bord1\shad0\blur1}",
                    )
                else:
                    style = style.replace(
                        border.group(),
                        r"\bord1",
                    )

                # make sure the border colour is black
                border_colour = re.search(r"\\3c&H[0-9a-fA-F]{6}&", style)
                if border_colour is None:
                    style = style.replace(
                        "}",
                        r"\3c&H000000&}",
                    )
                else:
                    style = style.replace(
                        border_colour.group(),
                        r"\3c&H000000&",
                    )

                text = style + text

            dialogs.append({"start": start, "end": end, "dialog": text})
        elif line == "\n":
            next_is_start_of_dialog = True

    doc = parse_subtitle(base_path / "config" / "template.ass")
    doc.styles._lines = []
    doc.events._lines = []

    with open(base_path / "config" / "styles" / "Default.json", "r") as f:
        default_style = json.load(f)
        default_style["Name"] = style_name
        default_style["Fontsize"] = font_size

    for key in default_style:
        if "Colour" in key:
            default_style[key] = Color(*default_style[key].values())
    if colour:
        r, g, b = get_colour(colour)
        default_style["OutlineColour"] = Color(
            r=int(r), g=int(g), b=int(b), a=0
        )

    doc.styles._lines.append(Style(**default_style))

    with open(base_path / "config" / "field_order.json", "r") as f:
        doc.events.field_order = json.load(f)

    with open(base_path / "config" / "styles" / "event.json", "r") as f:
        event_style = json.load(f)

    for dialog in dialogs:
        # fill the dialog to the event style
        event_style["Start"] = format_timestring(dialog["start"])
        event_style["End"] = format_timestring(dialog["end"])
        event_style["Style"] = default_style["Name"]
        event_style["Text"] = dialog["dialog"]
        doc.events._lines.append(Dialogue(**event_style))

    with open(output, "w", encoding="utf-8-sig") as f:
        doc.dump_file(f)
