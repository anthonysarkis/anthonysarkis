import html
import math
from typing import NamedTuple

FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
REDUCED_MOTION = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }"

Point = tuple[float, float]


class Layer(NamedTuple):
    body: str
    defs: str = ""
    style: str = ""


def stack(*layers: Layer) -> Layer:
    body = "".join(layer.body for layer in layers)
    defs = "".join(layer.defs for layer in layers)
    style = "".join(layer.style for layer in layers)
    return Layer(body, defs, style)


def group(attributes: str, layer: Layer) -> Layer:
    return Layer(f"<g {attributes}>{layer.body}</g>", layer.defs, layer.style)


def svg_document(width: int, height: int, label: str, drawing: Layer) -> str:
    accessible_label = html.escape(label)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{accessible_label}">\n'
        f"<style>{drawing.style}</style>\n"
        f"<defs>{drawing.defs}</defs>\n"
        f"{drawing.body}\n"
        "</svg>\n"
    )


def number(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def points(*corners: Point) -> str:
    return " ".join(f"{number(corner_x)},{number(corner_y)}" for corner_x, corner_y in corners)


def escape(text: str) -> str:
    return html.escape(text, quote=False)


def closed_curve(outline: list[Point]) -> str:
    start_x, start_y = outline[0]
    commands = [f"M{number(start_x)} {number(start_y)}"]

    count = len(outline)
    for index in range(count):
        before = outline[index - 1]
        start = outline[index]
        end = outline[(index + 1) % count]
        after = outline[(index + 2) % count]
        commands.append(smooth_segment(before, start, end, after))

    return "".join(commands) + "Z"


def smooth_segment(before: Point, start: Point, end: Point, after: Point) -> str:
    first_control_x = start[0] + (end[0] - before[0]) / 6
    first_control_y = start[1] + (end[1] - before[1]) / 6
    second_control_x = end[0] - (after[0] - start[0]) / 6
    second_control_y = end[1] - (after[1] - start[1]) / 6
    return (
        f"C{number(first_control_x)} {number(first_control_y)} "
        f"{number(second_control_x)} {number(second_control_y)} "
        f"{number(end[0])} {number(end[1])}"
    )


def blob_path(center: Point, radius_x: float, radius_y: float, wobble: tuple[float, ...]) -> str:
    center_x, center_y = center
    count = len(wobble)
    outline = []

    for index, factor in enumerate(wobble):
        angle = 2 * math.pi * index / count
        point_x = center_x + radius_x * factor * math.cos(angle)
        point_y = center_y + radius_y * factor * math.sin(angle)
        outline.append((point_x, point_y))

    return closed_curve(outline)
