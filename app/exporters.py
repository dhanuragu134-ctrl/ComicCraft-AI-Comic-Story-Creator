import os
import re
from datetime import datetime

from fpdf import FPDF


EXPORT_DIR = "app/static/exports"


def clean_text(text: str) -> str:
    replacements = {
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "—": "-",
        "–": "-",
        "…": "...",
        "→": "->",
        "←": "<-",
        "•": "-",
        "\t": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return (
        text
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


def safe_filename(text: str) -> str:
    text = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        text
    )

    return text.strip("_") or "comic"


def add_wrapped_text(
    pdf: FPDF,
    text: str,
    font_size: int = 11,
    line_height: float = 7,
):
    text = clean_text(str(text))

    pdf.set_x(15)

    pdf.multi_cell(
        w=180,
        h=line_height,
        text=text,
        border=0,
        align="L",
    )

    pdf.set_x(15)


def create_comic_pdf(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
    story: str,
) -> str:

    os.makedirs(
        EXPORT_DIR,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"{safe_filename(character_name)}_"
        f"ComicCraft_{timestamp}.pdf"
    )

    output_path = os.path.join(
        EXPORT_DIR,
        filename
    )

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4"
    )

    pdf.set_margins(
        left=15,
        top=15,
        right=15
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    pdf.add_page()

    # TITLE
    pdf.set_font(
        "Helvetica",
        "B",
        24
    )

    pdf.set_x(15)

    pdf.cell(
        w=180,
        h=15,
        text="ComicCraft",
        border=0,
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.set_font(
        "Helvetica",
        "",
        12
    )

    pdf.set_x(15)

    pdf.cell(
        w=180,
        h=8,
        text="AI Comic Story Creator",
        border=0,
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.ln(8)

    # COMIC DETAILS
    pdf.set_font(
        "Helvetica",
        "B",
        16
    )

    pdf.set_x(15)

    pdf.cell(
        w=180,
        h=10,
        text="Comic Details",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.set_font(
        "Helvetica",
        "",
        11
    )

    details = [
        ("Story Prompt", story_prompt),
        ("Character", character_name),
        ("Setting", setting),
        ("Tone", tone),
        ("Art Style", art_style),
    ]

    for label, value in details:

        add_wrapped_text(
            pdf,
            f"{label}: {clean_text(str(value))}",
            font_size=11,
            line_height=7,
        )

    pdf.ln(6)

    # AI STORY
    pdf.set_font(
        "Helvetica",
        "B",
        16
    )

    pdf.set_x(15)

    pdf.cell(
        w=180,
        h=10,
        text="AI Generated Comic Story",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.set_font(
        "Helvetica",
        "",
        11
    )

    story_text = clean_text(str(story))

    for line in story_text.splitlines():

        line = line.strip()

        if not line:
            pdf.ln(3)
            continue

        add_wrapped_text(
            pdf,
            line,
            font_size=11,
            line_height=7,
        )

    pdf.ln(8)

    # FOOTER
    pdf.set_font(
        "Helvetica",
        "I",
        9
    )

    pdf.set_x(15)

    pdf.cell(
        w=180,
        h=6,
        text="Created with ComicCraft",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.output(output_path)

    return output_path