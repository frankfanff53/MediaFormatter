import json
import re
from pathlib import Path

import ass

# import pycorrector
from lingua import Language, LanguageDetectorBuilder

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


def split_subtitle(doc, languages=[Language.ENGLISH, Language.CHINESE]):
    """Split subtitle file into different languages.

    Args:
        path (Union[str, PurePath]): Path to the subtitle file.
        languages (Optional[List[Language]], optional): List of languages to split. Defaults to [Language.ENGLISH, Language.CHINESE].

    Returns:
        A dictionary of language and list of dialogues.
    """
    if len(languages) == 0:
        raise Exception("No language specified.")
    detector = LanguageDetectorBuilder.from_languages(*languages).build()
    split = {language.name: [] for language in languages}
    for event in doc.events:
        use_style = False
        # check if special formatting is used
        if (
            r"\pos" in event.text
            or r"\move" in event.text
            or r"\fad" in event.text
        ):
            # get the style
            use_style = True
            # extract the part with \pos, \move, \fad only
            style = re.search(
                r"\{[^\{]*?(\\pos|\\fad|\\move)[^\{]*\}", event.text
            )
            # remove the style from the text
            dialog = re.sub(r"\{.*?\}", "", event.text)
            language_detect = detector.detect_language_of(dialog)
            if language_detect is None:
                continue
            else:
                language = language_detect.name

            split[language].append(
                {
                    "start": event.start,
                    "end": event.end,
                    "dialog": event.text,
                }
            )
        else:
            # check if numpad \an<alignment> is used
            use_numpad = False
            numpad = re.search(r"\\an\d", event.text)
            if numpad is not None:
                use_numpad = True

            # split text into lines
            lines = event.text.split(r"\N")
            start = event.start
            end = event.end
            for i, line in enumerate(lines):
                # remove all styles
                line = re.sub(r"\{.*?\}", "", line)
                # if the punctuation is not followed by a space, add a space
                line = re.sub(
                    r"(?<=[.,!?])(?=[^\s\d\.,!?])",
                    " ",
                    line,
                )
                language_detect = detector.detect_language_of(line)
                if language_detect is None:
                    language = "CHINESE" if i == 0 else "ENGLISH"
                else:
                    language = language_detect.name

                # if language == "CHINESE":
                #     line, _ = pycorrector.correct(line)

                if use_style:
                    line = style.group() + line

                if use_numpad:
                    line = "{" + numpad.group() + "}" + line

                split[language].append(
                    {
                        "start": start,
                        "end": end,
                        "dialog": line,
                    }
                )
    return split


if __name__ == "__main__":
    base_path = Path(__file__).parent.parent
    doc = parse_subtitle(base_path / "config" / "ref.ass")

    print(doc.events.field_order)
