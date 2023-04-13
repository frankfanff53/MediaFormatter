import argparse
from copy import deepcopy
from datetime import timedelta

import mediaformatter as mf

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--primary-subtitle",
        help="The path to the primary subtitle file",
        required=True,
    )

    parser.add_argument(
        "--secondary-subtitle",
        help="The path to the secondary subtitle file",
        required=True,
    )

    parser.add_argument(
        "-o",
        "--output",
        help="The path to the output subtitle file",
        required=True,
    )

    args = parser.parse_args()

    doc_primary = mf.parse_subtitle(args.primary_subtitle)
    doc_secondary = mf.parse_subtitle("output_secondary.ass")

    output_doc = deepcopy(doc_primary)
    output_doc.styles._lines = (
        doc_primary.styles._lines + doc_secondary.styles._lines
    )

    output_doc.events._lines = []
    primary_lines = doc_primary.events._lines
    secondary_lines = doc_secondary.events._lines

    i, j = 0, 0
    while i < len(primary_lines) and j < len(secondary_lines):
        primary_line = primary_lines[i]
        secondary_line = secondary_lines[j]

        primary_line_start = primary_line.start
        primary_line_end = primary_line.end

        secondary_line_start = secondary_line.start
        secondary_line_end = secondary_line.end

        while primary_line_start < secondary_line_start:
            # this means current secondary line is way further
            # than the current primary line on the timeline
            output_doc.events._lines.append(primary_line)
            i += 1
            primary_line = primary_lines[i]
            primary_line_start = primary_line.start
            primary_line_end = primary_line.end

        try:
            assert primary_line_start == secondary_line_start
        except AssertionError:
            print("Start time does not match")
            print(
                f"Primary Lang: start: {primary_line.start}, "
                f"end: {primary_line.end}, text: {primary_line.text}"
            )
            print(
                f"Secondary Lang: start: {secondary_line.start}, "
                f"end: {secondary_line.end}, text: {secondary_line.text}"
            )
            print("Aborted.")
            exit(1)

        if primary_line_end != secondary_line_end:
            synchronised_text = []
            while True:
                if primary_line_end > secondary_line_end:
                    synchronised_text.append(secondary_line.text)
                    j += 1
                    secondary_line = secondary_lines[j]
                    secondary_line_start = secondary_line.start
                    secondary_line_end = secondary_line.end
                    if abs(primary_line_end - secondary_line_end) < timedelta(
                        seconds=0.5
                    ):
                        synchronised_text.append(secondary_line.text)
                        secondary_line.start = primary_line_start
                        secondary_line.end = primary_line_end
                        secondary_line.text = " ".join(synchronised_text)
                        break
                else:
                    synchronised_text.append(primary_line.text)
                    i += 1
                    primary_line = primary_lines[i]
                    primary_line_start = primary_line.start
                    primary_line_end = primary_line.end
                    if abs(primary_line_end - secondary_line_end) < timedelta(
                        seconds=0.5
                    ):
                        synchronised_text.append(primary_line.text)
                        primary_line.start = secondary_line_start
                        primary_line.end = secondary_line_end
                        primary_line.text = " ".join(synchronised_text)
                        break
        output_doc.events._lines.append(secondary_line)
        output_doc.events._lines.append(primary_line)
        i += 1
        j += 1

    with open(args.output, "w", encoding="utf-8-sig") as f:
        output_doc.dump_file(f)
