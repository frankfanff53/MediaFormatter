import argparse
import json
from datetime import datetime
from pathlib import Path

from ass import Dialogue, Style
from ass.data import Color

import mediaformatter as mf


def format_timestring(time_string):
    datetime_obj = datetime.strptime(time_string, "%H:%M:%S.%f")
    return datetime_obj.strftime("%H:%M:%S.%f")[:-4]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        help="The input path of the srt file",
        required=True,
    )

    parser.add_argument(
        "-o",
        "--output",
        help="The output path of the converted ass file",
        required=True,
    )

    parser.add_argument(
        "--style-name",
        help="The name of style for the rendered ass file",
        default="Default",
    )

    parser.add_argument(
        "--font-size",
        help="The font size of the rendered ass file",
        default=19,
    )

    args = parser.parse_args()
    subtitle_path = args.input
    base_path = Path(__file__).parent

    with open(subtitle_path, "r", encoding="utf-8-sig") as f:
        contents = f.readlines()

    dialog_start_index, dialog_end_index = 1, 1

    dialogs = []

    next_is_start_of_dialog = False
    for i, line in enumerate(contents):
        if i == 0:
            continue
        if line.replace('\n', '').isdigit() and next_is_start_of_dialog:
            next_is_start_of_dialog = False
            dialog_end_index = i
            dialog = contents[dialog_start_index:dialog_end_index]
            dialog = [line.replace('\n', '') for line in dialog if line != '\n']
            dialog_start_index = dialog_end_index + 1
            timerange, text = dialog[0].replace(",", "."), " ".join(dialog[1:])
            start, end = timerange.split(" --> ")
            dialogs.append({"start": start, "end": end, "dialog": text})
        elif line == '\n':
            next_is_start_of_dialog = True

    doc = mf.parse_subtitle(base_path / "config" / "template.ass")
    doc.styles._lines = []
    doc.events._lines = []

    with open(base_path / "config" / "styles" / "Default.json", "r") as f:
        default_style = json.load(f)
        default_style["Name"] = args.style_name
        default_style["Fontsize"] = args.font_size

    for key in default_style:
        if "Colour" in key:
            default_style[key] = Color(*default_style[key].values())

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

    with open(args.output, "w", encoding="utf-8-sig") as f:
        doc.dump_file(f)
