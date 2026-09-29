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
        str(text)
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


def safe_filename(text: str) -> str:
    text = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        str(text)
    )

    return text.strip("_") or "comic"


def create_comic_pdf(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
    story: str,
    layout=None,
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
        15,
        15,
        15
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    # --------------------------------
    # COVER PAGE
    # --------------------------------

    pdf.add_page()

    pdf.set_font(
        "Helvetica",
        "B",
        26
    )

    pdf.cell(
        180,
        15,
        "ComicCraft",
        align="C",
        new_x="LMARGIN",
        new_y="NEXT"
    )

    pdf.set_font(
        "Helvetica",
        "",
        13
    )

    pdf.cell(
        180,
        8,
        "AI Comic Story Creator",
        align="C",
        new_x="LMARGIN",
        new_y="NEXT"
    )

    pdf.ln(12)

    pdf.set_font(
        "Helvetica",
        "B",
        15
    )

    pdf.cell(
        180,
        10,
        "Comic Details",
        new_x="LMARGIN",
        new_y="NEXT"
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

        pdf.set_x(15)

        pdf.multi_cell(
            180,
            7,
            f"{label}: {clean_text(value)}"
        )

    # --------------------------------
    # PANEL PAGES
    # --------------------------------

    if layout:

        for panel in layout:

            pdf.add_page()

            panel_number = panel.get(
                "panel",
                ""
            )

            title = panel.get(
                "title",
                f"Panel {panel_number}"
            )

            image_path = panel.get(
                "image_path",
                ""
            )

            scene_description = panel.get(
                "scene_description",
                ""
            )

            panel_text = panel.get(
                "text",
                ""
            )

            # Panel heading
            pdf.set_font(
                "Helvetica",
                "B",
                17
            )

            pdf.cell(
                180,
                10,
                f"Panel {panel_number}: "
                f"{clean_text(title)}",
                align="C",
                new_x="LMARGIN",
                new_y="NEXT"
            )

            pdf.ln(4)

            # Panel image
            if (
                image_path
                and os.path.exists(image_path)
            ):

                try:

                    pdf.image(
                        image_path,
                        x=20,
                        y=35,
                        w=170
                    )

                    pdf.set_y(145)

                except Exception:
                    pdf.set_y(40)

            else:

                pdf.set_y(40)

                pdf.set_font(
                    "Helvetica",
                    "I",
                    11
                )

                pdf.multi_cell(
                    180,
                    7,
                    "[Comic panel image unavailable]"
                )

                pdf.ln(5)

            # Scene description
            if scene_description:

                pdf.set_font(
                    "Helvetica",
                    "I",
                    10
                )

                pdf.multi_cell(
                    180,
                    6,
                    f"Scene: {clean_text(scene_description)}"
                )

                pdf.ln(3)

            # Narration/dialogue
            if panel_text:

                pdf.set_font(
                    "Helvetica",
                    "",
                    11
                )

                pdf.multi_cell(
                    180,
                    7,
                    clean_text(panel_text)
                )

    else:

        # Fallback when no layout is supplied.
        pdf.add_page()

        pdf.set_font(
            "Helvetica",
            "B",
            16
        )

        pdf.cell(
            180,
            10,
            "AI Generated Comic Story",
            new_x="LMARGIN",
            new_y="NEXT"
        )

        pdf.set_font(
            "Helvetica",
            "",
            11
        )

        for line in clean_text(story).splitlines():

            line = line.strip()

            if not line:
                pdf.ln(3)
                continue

            pdf.set_x(15)

            pdf.multi_cell(
                180,
                7,
                line
            )

    # --------------------------------
    # FOOTER
    # --------------------------------

    pdf.ln(8)

    pdf.set_font(
        "Helvetica",
        "I",
        9
    )

    pdf.cell(
        180,
        6,
        "Created with ComicCraft",
        align="C"
    )

    pdf.output(output_path)

    return output_path