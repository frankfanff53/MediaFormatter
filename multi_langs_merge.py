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
    doc_secondary = mf.parse_subtitle(args.secondary_subtitle)

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

        if abs(primary_line.start - secondary_line.start) >= timedelta(
            seconds=1
        ):
            # if both heads are not close enough, we just append the one with the earlier start time
            if primary_line.start < secondary_line.start:
                output_doc.events._lines.append(primary_line)
                i += 1
            else:
                output_doc.events._lines.append(secondary_line)
                j += 1
        else:
            # if both heads are close enough, we look at the end time
            # if the end time of the primary line is earlier than the end time of the secondary line,
            # we keep appending the primary line until the end time of the primary line is later than the end time of the secondary line
            # then we append the secondary line
            # otherwise, we append the secondary line
            if primary_line.end < secondary_line.end:
                synchromised_text = []
                while (
                    i < len(primary_lines)
                    and primary_line.end < secondary_line.end
                ):
                    synchromised_text.append(primary_line.text)
                    i += 1
                    primary_line = primary_lines[i]
                primary_line.start = secondary_line.start
                primary_line.text = " ".join(synchromised_text)
                primary_line.end = secondary_line.end

            elif primary_line.end > secondary_line.end:
                synchromised_text = []
                while (
                    j < len(secondary_lines)
                    and primary_line.end > secondary_line.end
                ):
                    synchromised_text.append(secondary_line.text)
                    j += 1
                    secondary_line = secondary_lines[j]
                secondary_line.start = primary_line.start
                secondary_line.text = " ".join(synchromised_text)
                secondary_line.end = primary_line.end

            output_doc.events._lines.append(secondary_line)
            output_doc.events._lines.append(primary_line)
            i += 1
            j += 1

    with open(args.output, "w", encoding="utf-8-sig") as f:
        output_doc.dump_file(f)
