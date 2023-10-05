import re
from pathlib import Path

from .utils import parse_subtitle


def get_fonts_from_doc(doc):
    styles = doc.styles._lines
    fonts = set()
    for style in styles:
        fonts.add(style.fontname)

    for event in doc.events:
        text = event.text
        if r"\fn" in text:
            # get the font name
            # and the font name may contain spaces
            font = re.search(r"\\fn(.*?)([\}\\])", text)
            if font is not None:
                font = font.group(1)
                fonts.add(font)

    return fonts


def analyse_fonts_from_doc(input_path, default_fonts):
    doc = parse_subtitle(input_path)
    additional_fonts = get_fonts_from_doc(doc) - default_fonts
    return additional_fonts


def fonts(input: str):
    base_path = Path().getcwd()
    input_path = base_path / input
    default_fonts_path = Path(__file__).parent.parent / "fonts"
    # get font names under the default_fonts_paths
    # where the fonts have suffix .ttf or .otf
    default_fonts = set([
        str(font.name.with_suffix(""))
        for font in default_fonts_path.glob("*.[o|t]tf")
        if font.is_file()
    ])

    if not input_path.exists():
        raise FileNotFoundError(f"Input path {input_path} does not exist")

    if input_path.is_file():
        if input_path.suffix == ".ass":
            additional_fonts = analyse_fonts_from_doc(
                input_path, default_fonts
            )
        else:
            raise ValueError(f"File {input_path} cannot be analysed.")
        print("Fonts used in the subtitle:", list(additional_fonts))
    elif input_path.is_dir():
        fonts_pool = set()
        for file in sorted(input_path.glob("*.ass")):
            additional_fonts = analyse_fonts_from_doc(file, default_fonts)
            fonts_pool.update(additional_fonts)
        print("Fonts used in the subtitle:", list(fonts_pool))
