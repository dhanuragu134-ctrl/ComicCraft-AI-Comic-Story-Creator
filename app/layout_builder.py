from typing import List, Dict, Any


def build_comic_layout(
    panels: List[Dict[str, Any]],
    story: str
) -> List[Dict[str, Any]]:
    """
    Combine panel images, titles, scene descriptions,
    and story text into a structured comic layout.
    """

    layout = []

    for index, panel in enumerate(panels, start=1):

        panel_number = panel.get(
            "panel",
            index
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

        layout.append(
            {
                "panel": panel_number,
                "title": title,
                "image_path": image_path,
                "text": panel_text,
                "scene_description": scene_description,
                "story": story,
            }
        )

    return layout