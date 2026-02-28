#!/usr/bin/env python3
"""Simple grid and circle plotter based on JSON input.

The script reads a JSON file containing an array of circle specifications.
Each spec should have x, y, and optionally radius and color. It then draws
an evenly spaced grid and places circles accordingly using matplotlib.

Usage:
    python fbchart.py data.json

JSON example:
[
    {"x": 1, "y": 2, "radius": 0.5, "color": "red"},
    {"x": 3, "y": 4}
]

"""

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt


def load_data(path):
    """Load JSON file from given path and return list of dicts."""
    with open(path, "r") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("JSON must contain a list of circle specs")
    return data


def draw_grid(ax, xmin, xmax, ymin, ymax, spacing=1):
    """Draw a grid on the provided axes."""
    # vertical lines
    for x in range(int(xmin), int(xmax) + 1, spacing):
        ax.axvline(x, color="lightgray", linewidth=0.5)
    # horizontal lines
    for y in range(int(ymin), int(ymax) + 1, spacing):
        ax.axhline(y, color="lightgray", linewidth=0.5)


def plot_circles(ax, circles):
    """Plot circles specified by list of dicts on the axes."""
    for circ in circles:
        x = circ.get("x")
        y = circ.get("y")
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

    # determine bounds
    xs = [c.get("x", 0) for c in circles if "x" in c]
    ys = [c.get("y", 0) for c in circles if "y" in c]
    if xs:
        xmin, xmax = min(xs) - 1, max(xs) + 1
    else:
        xmin, xmax = 0, 10
    if ys:
        ymin, ymax = min(ys) - 1, max(ys) + 1
    else:
        ymin, ymax = 0, 10

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
