import math
from itertools import groupby

from .svg import Layer, Point, number

COLUMNS = 30
ROWS = 22
PIXEL = 3.2
REAR_AXLE = (8.5, 15.5)
FRONT_AXLE = (24.5, 18.5)
EXHAUST_TOP = (21.5, 1.5)
PUFFS = 3
PUFF_INTERVAL = 0.45
HEIGHT_ABOVE_ROAD = 48

HUB = "#30363d"
RIM = "#e3b341"
TYRE = "#3d444d"
TREAD = "#5a636e"

STYLE = """
    .drive { animation: drive 26s linear infinite; }
    .puff { fill: #c9d1d9; opacity: 0; transform-box: fill-box; transform-origin: center; animation: puff 1.35s ease-out infinite; }
    .chassis { animation: idle .32s steps(1) infinite; }
    @keyframes drive { from { transform: translateX(-110px); } to { transform: translateX(900px); } }
    @keyframes puff { 0% { opacity: .75; transform: translate(0, 0) scale(.6); }
                      100% { opacity: 0; transform: translate(-10px, -26px) scale(2.2); } }
    @keyframes idle { 50% { transform: translateY(-1px); } }
    @media (prefers-reduced-motion: reduce) { .puff { display: none; } .drive { transform: translateX(560px); } }"""


def tractor(road_top: float) -> Layer:
    top = road_top - HEIGHT_ABOVE_ROAD
    return Layer(
        f'<g class="drive"><g transform="translate(0 {number(top)})">{chassis()}{exhaust()}</g></g>',
        style=STYLE,
    )


def chassis() -> str:
    rectangles = [rectangle for row in range(ROWS) for rectangle in row_rectangles(row)]
    return f'<g class="chassis">{"".join(rectangles)}</g>'


def row_rectangles(row: int) -> list[str]:
    colours = [pixel_colour(column, row) for column in range(COLUMNS)]
    rectangles = []
    column = 0

    for colour, run in groupby(colours):
        run_length = len(list(run))
        if colour:
            rectangles.append(pixel_run(column, row, run_length, colour))
        column += run_length

    return rectangles


def pixel_run(column: int, row: int, length: int, colour: str) -> str:
    left = number(column * PIXEL)
    top = number(row * PIXEL)
    width = number(length * PIXEL)
    return f'<rect x="{left}" y="{top}" width="{width}" height="{number(PIXEL)}" fill="{colour}"/>'


def exhaust() -> str:
    exhaust_x, exhaust_y = EXHAUST_TOP
    return "".join(
        f'<circle class="puff" cx="{number(exhaust_x * PIXEL)}" cy="{number(exhaust_y * PIXEL)}" '
        f'r="{number(PIXEL * 0.9)}" style="animation-delay:{index * PUFF_INTERVAL:.2f}s"/>'
        for index in range(PUFFS)
    )


def pixel_colour(column: int, row: int) -> str | None:
    return wheel_colour(column, row) or body_colour(column, row)


def wheel_colour(column: int, row: int) -> str | None:
    rear = distance(column, row, REAR_AXLE)
    front = distance(column, row, FRONT_AXLE)

    if rear <= 1.3:
        return HUB
    if rear <= 3.4:
        return RIM
    if rear <= 6.0:
        return TREAD if rear > 5.0 and is_tread(column, row) else TYRE

    if front <= 0.9:
        return HUB
    if front <= 1.9:
        return RIM
    if front <= 3.4:
        return TYRE

    return None


def body_colour(column: int, row: int) -> str | None:
    if row == 2 and 20 <= column <= 22:
        return "#8b949e"
    if column == 21 and 3 <= row <= 7:
        return "#6e7681"
    if column == 27 and row == 8:
        return "#fff8c5"
    if column == 27 and 10 <= row <= 12:
        return "#11502a"
    if 1 <= row <= 2 and 3 <= column <= 15:
        return "#1a7f37"
    if 6 <= column <= 13 and 3 <= row <= 8:
        return "#d8ecff" if (column - row) in (3, 4) else "#a5d6ff"
    if 4 <= column <= 15 and 3 <= row <= 10:
        return "#3fb950"
    if 15 <= column <= 27 and 7 <= row <= 12:
        return "#56d364" if row == 7 else "#3fb950"
    if 3 <= column <= 26 and 11 <= row <= 13:
        return "#2ea043"
    if 6.0 < distance(column, row, REAR_AXLE) <= 7.2 and row <= 15:
        return "#2ea043"
    return None


def distance(column: int, row: int, axle: Point) -> float:
    axle_x, axle_y = axle
    return math.hypot(column + 0.5 - axle_x, row + 0.5 - axle_y)


def is_tread(column: int, row: int) -> bool:
    axle_x, axle_y = REAR_AXLE
    angle = math.atan2(row + 0.5 - axle_y, column + 0.5 - axle_x)
    return int((angle + math.pi) / (math.pi / 8)) % 2 == 1
