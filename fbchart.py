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
    """Load JSON file from given path and return validated list of dicts.

    Strings must be one of E, A, D, G, B, e and will be converted to
    corresponding y-values 0..5. Existing numeric "string" or "y" values
    are left alone unless a named string is provided. The returned list has
    only numeric coordinates (fret/y).
    """
    with open(path, "r") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("JSON must contain a list of circle specs")

    # normalize and validate entries
    normalized = []
    for entry in data:
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
    return normalized


def draw_grid(ax, xmin, xmax, ymin, ymax, spacing=1):
    """Draw a grid on the provided axes.

    Horizontal lines are locked at integer positions 0 through 5, labeled
    E, A, D, G, B, e from bottom to top. The y-limits passed to this
    function are ignored; we instead always use the fixed range. Vertical
    lines are drawn according to the given x bounds and spacing.
    """
    # vertical grid lines based on frets
    for x in range(int(xmin), int(xmax) + 1, spacing):
        ax.axvline(x, color="lightgray", linewidth=0.5)

    # always six horizontal string lines at 0..5
    labels = ["E", "A", "D", "G", "B", "e"]
    positions = list(range(len(labels)))
    for pos in positions:
        ax.axhline(pos, color="lightgray", linewidth=0.5)
    ax.set_yticks(positions)
    ax.set_yticklabels(labels)


def plot_circles(ax, circles):
    """Plot circles specified by list of dicts on the axes.

    ``fret`` provides the x-coordinate and ``string`` the y-coordinate.
    """
    for circ in circles:
        x = circ.get("fret")
        y = circ.get("string")
        if x is None or y is None:
            continue
        r = circ.get("radius", 0.5)
        color = circ.get("color", "blue")
        circle = plt.Circle((x, y), r, color=color, alpha=0.5)
        ax.add_patch(circle)


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <data.json>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File {path} does not exist")
        sys.exit(1)

    circles = load_data(path)

    # determine horizontal bounds from fret values; vertical is fixed
    xs = [c.get("fret", 0) for c in circles if "fret" in c]
    # we ignore the numeric ys because the grid is fixed at 0..5
    if xs:
        xmin, xmax = min(xs) - 1, max(xs) + 1
    else:
        xmin, xmax = 0, 10
    ymin, ymax = 0, 5  # fixed string range

    fig, ax = plt.subplots()
    draw_grid(ax, xmin, xmax, ymin, ymax)
    plot_circles(ax, circles)

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('FBChart grid')

    plt.show()


if __name__ == '__main__':
    main()
