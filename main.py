from typer import Option, Typer

import mediaformatter as mf

app = Typer()


@app.command()
def style(
    input: str,
    colour: str = Option(None, help="Colour to render subtitles in"),
    fontname: str = Option(None, help="Font to render subtitles in"),
    fontsize: int = Option(None, help="Font size to render subtitles in"),
    bold: bool = Option(False, help="Whether to render subtitles in bold"),
):
    mf.style(
        input=input,
        colour=colour,
        fontname=fontname,
        fontsize=fontsize,
        bold=bold,
    )


@app.command()
def rename(
    format: str,
    movie: bool = Option(False, help="Whether to rename files for a movie"),
):
    mf.rename(
        format=format,
        movie=movie,
    )


@app.command()
def preprocess(
    directory: str,
    fonts: str = Option(None, help="Directory containing fonts"),
    drop_attachments: bool = Option(False, help="Drop attachments"),
    with_jpn: bool = Option(
        False, help="Extract only files with Japanese audio"
    ),
):
    mf.preprocess(
        directory=directory,
        fonts=fonts,
        drop_attachments=drop_attachments,
        with_jpn=with_jpn,
    )


@app.command()
def extract(directory: str):
    mf.extract(directory=directory)


@app.command()
def srt2ass(
    input: str,
    output: str,
    style_name: str = Option(
        "Default", help="The name of style for the rendered ass file"
    ),
    font_size: int = Option(19, help="The font size of the rendered ass file"),
):
    mf.srt2ass(
        input=input,
        output=output,
        style_name=style_name,
        font_size=font_size,
    )


if __name__ == "__main__":
    app()