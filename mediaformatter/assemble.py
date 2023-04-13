import json
from pathlib import Path

import numpy as np
from ass import Dialogue, Style
from ass.data import Color
from matplotlib.colors import to_rgb

from .utils import parse_subtitle, split_subtitle

COLOUR_MAP = {
    "green": np.array([8, 77, 42]) / 255,
    "black": "black",
    "red": "firebrick",
    "blue": "royalblue",
}


def render_to_subtitle(input_path, output_path, **kwargs):
    base_path = Path(__file__).parent.parent

    doc = parse_subtitle(input_path)
    # Split subtitle into languages
    split = split_subtitle(doc)

    chinese_dialogs = split["CHINESE"]
    english_dialogs = split["ENGLISH"]

    colour_overwrite = kwargs.get("colour")
    font_overwrite = kwargs.get("fontname")
    fontsize_overwrite = kwargs.get("fontsize")
    bold = kwargs.get("bold")

    # Get chinese dialog style
    with open(base_path / "config" / "styles" / "CHINESE.json", "r") as f:
        chinese_style = json.load(f)
    if colour_overwrite:
        if colour_overwrite not in COLOUR_MAP:
            try:
                r, g, b = np.array(to_rgb(colour_overwrite)) * 255
            except Exception:
                print(
                    f"Colour {colour_overwrite} is not supported, please try it again"
                )
                exit(1)
        else:
            r, g, b = np.array(to_rgb(COLOUR_MAP[colour_overwrite])) * 255
        chinese_style["OutlineColour"] = {
            "r": int(r),
            "g": int(g),
            "b": int(b),
            "a": 0,
        }
    if font_overwrite:
        chinese_style["Fontname"] = font_overwrite
    if bold:
        chinese_style["Bold"] = True
    if fontsize_overwrite:
        chinese_style["Fontsize"] = fontsize_overwrite

    # Get english dialog style
    with open(base_path / "config" / "styles" / "ENGLISH.json", "r") as f:
        english_style = json.load(f)
    if fontsize_overwrite:
        english_style["Fontname"] = font_overwrite
        english_style["Fontsize"] = fontsize_overwrite

    # reformat the dialog style
    for style in [chinese_style, english_style]:
        for key in style:
            if "Colour" in key:
                c = style[key]
                style[key] = Color(*c.values())

    doc.styles._lines = []
    doc.events._lines = []
    with open(base_path / "config" / "field_order.json", "r") as f:
        doc.events.field_order = json.load(f)

    # Add chinese dialog style
    doc.styles._lines.append(Style(**chinese_style))
    # Add english dialog style
    doc.styles._lines.append(Style(**english_style))

    # Get event style
    with open(base_path / "config" / "styles" / "event.json", "r") as f:
        event_style = json.load(f)

    # Add english dialogs
    for dialog in english_dialogs:
        # fill the dialog to the event style
        event_style["Start"] = dialog["start"]
        event_style["End"] = dialog["end"]
        event_style["Style"] = "ENGLISH"
        event_style["Text"] = dialog["dialog"]
        doc.events._lines.append(Dialogue(**event_style))
    # Add chinese dialogs
    for dialog in chinese_dialogs:
        # fill the dialog to the event style
        event_style["Start"] = dialog["start"]
        event_style["End"] = dialog["end"]
        event_style["Style"] = "CHINESE"
        event_style["Text"] = dialog["dialog"]
        doc.events._lines.append(Dialogue(**event_style))

    # Save the result
    with open(output_path, "w", encoding="utf-8-sig") as f:
        doc.dump_file(f)
