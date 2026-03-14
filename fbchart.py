#!/usr/bin/env python3
"""Simple grid and circle plotter based on JSON input.

Coordinates in the JSON are provided as `fret` (horizontal position)
and `string` (vertical position). Fret corresponds to the x-axis and string
to the y-axis. Radius and color remain optional.

Usage:
    python fbchart.py data.json

JSON example:
[
    {"fret": 1, "string": 2, "radius": 0.5, "color": "red"},
    {"fret": 3, "string": 4}
]

"""

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt

# mapping of string names to y-axis integers
STRING_MAP = {"E": 0, "A": 1, "D": 2, "G": 3, "B": 4, "e": 5}


def load_data(path):
    """Load JSON file from given path and return (note list, title).

    JSON must be an object with keys:
      "title": chart title (optional),
      "notes": list of note specs

    Strings must be one of E, A, D, G, B, e and will be converted to
    corresponding y-values 0..5. Existing numeric "string" or "y" values
    are left alone unless a named string is provided. The returned list has
    only numeric coordinates (fret/y).
    """
    with open(path, "r") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("JSON must be an object with 'notes' and optional 'title'")

    title = data.get("title")
    notes = data.get("notes")
    if not isinstance(notes, list):
        raise ValueError("JSON 'notes' key must contain a list of note specs")

    normalized = []
    for entry in notes:
        if not isinstance(entry, dict):
            continue
        item = entry.copy()
        # process string -> numeric y
        if "string" in item:
            val = item["string"]
            if isinstance(val, str):
                if val not in STRING_MAP:
                    raise ValueError(f"Invalid string value '{val}', must be one of {list(STRING_MAP.keys())}")
                item["string"] = STRING_MAP[val]
            # otherwise assume numeric and leave it
        normalized.append(item)
    return normalized, title


def draw_grid(ax, xmin, xmax, ymin, ymax, spacing=1):
    """Draw a grid on the provided axes.

    Horizontal lines are locked at integer positions 0 through 5, labeled
    E, A, D, G, B, e from bottom to top. The y-limits passed to this
    function are ignored; we instead always use the fixed range. Vertical
    lines are drawn according to the given x bounds and spacing.
    """
    # vertical grid lines based on frets; emphasize zero
    for x in range(int(xmin), int(xmax) + 1, spacing):
        if x == 0:
            ax.axvline(x, color="gray", linewidth=1.5)
        else:
            ax.axvline(x, color="lightgray", linewidth=0.5)

    # always six horizontal string lines at 0..5
    labels = ["E", "A", "D", "G", "B", "e"]
    positions = list(range(len(labels)))
    for pos in positions:
        ax.axhline(pos, color="lightgray", linewidth=0.5)
    ax.set_yticks(positions)
    ax.set_yticklabels(labels)


def plot_notes(ax, notes):
    """Plot notes specified by list of dicts on the axes.

    ``fret`` provides the x-coordinate and ``string`` the y-coordinate.
    Radius is fixed at 0.4 for every note; any value in the JSON is
    ignored. We offset the x position by -0.5 so the marker is centered on
    the fret line.
    """
    for note in notes:
        x = note.get("fret") - 0.5  # center the note on the fret
        y = note.get("string")
        if x is None or y is None:
            continue
        r = 0.4
        color = note.get("color", "blue")
        # if color is a two-element array, draw left/right halves
        if isinstance(color, (list, tuple)) and len(color) >= 2:
            # left half (180° to 360°) and right half (0° to 180°)
            from matplotlib.patches import Wedge
            left = Wedge((x, y), r, 90, 270, facecolor=color[0], alpha=0.5, clip_on=False)
            right = Wedge((x, y), r, -90, 90, facecolor=color[1], alpha=0.5, clip_on=False)
            ax.add_patch(left)
            ax.add_patch(right)
        else:
            circle = plt.Circle((x, y), r, color=color, alpha=0.5, clip_on=False)
            ax.add_patch(circle)


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <data.json>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File {path} does not exist")
        sys.exit(1)

    notes, title = load_data(path)

    # determine horizontal bounds from fret values; vertical is fixed
    xs = [n.get("fret", 0) for n in notes if "fret" in n]
    # we ignore the numeric ys because the grid is fixed at 0..5
    if xs:
        xmin, xmax = min(xs) - 1, max(xs) + 1
    else:
        xmin, xmax = 0, 10
    ymin, ymax = 0, 5  # fixed string range
    # add padding equal to radius so circles aren't clipped
    pad = 0.4
    xmin -= pad
    xmax += pad
    ymin -= pad
    ymax += pad

    fig, ax = plt.subplots()
    draw_grid(ax, xmin, xmax, ymin, ymax)
    plot_notes(ax, notes)

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect('equal', adjustable='box')
    ax.set_title(title or 'FBChart grid')

    plt.show()


if __name__ == '__main__':
    main()
