from collections import Counter
from datetime import date, timedelta

from .layout import WIDTH
from .svg import Layer, Point, number, points

WEEKS = 53
DAYS_PER_WEEK = 7
CELL_WIDTH = 13.4
ROW_HEIGHT = 10.5
SHEAR = 4.2
BACK_Y = 292
LEFT = (WIDTH - (WEEKS * CELL_WIDTH + (DAYS_PER_WEEK - 1) * SHEAR)) / 2
SLAB_OVERHANG = 0.6
FRONT_Y = BACK_Y + (DAYS_PER_WEEK + SLAB_OVERHANG) * ROW_HEIGHT
FRONT_EDGE_DEPTH = 7
PLANT_SCALE = 1.5
SWAY_DELAY_PER_WEEK = 0.09

SOIL = "#ad7646"
SOIL_LIGHT = "#b98250"
SLAB = "#7a4e2c"
SLAB_EDGE = "#5e3c22"

PLANT_SHAPES = {
    1: (
        '<path d="M0 0 C-1 -2 -3 -3 -4.5 -4 M0 0 C1 -2 3 -3 4.5 -4" stroke="#5fb83a" stroke-width="1.6" '
        'fill="none" stroke-linecap="round"/>'
    ),
    2: (
        '<path d="M0 0 V-8 M0 -3 C-2 -4 -3.5 -5 -5 -5.5 M0 -5.5 C2 -6.5 3.5 -7.5 5 -8" stroke="#46a12b" '
        'stroke-width="1.6" fill="none" stroke-linecap="round"/>'
    ),
    3: (
        '<path d="M0 0 V-12" stroke="#5c9e3a" stroke-width="1.6" stroke-linecap="round"/>'
        '<path d="M0 -4 C-2.5 -5 -4 -6.5 -5 -8 M0 -7 C2.5 -8 4 -9.5 5 -11" stroke="#5c9e3a" '
        'stroke-width="1.4" fill="none" stroke-linecap="round"/>'
        '<ellipse cx="0" cy="-14" rx="1.9" ry="3.4" fill="#93c95b"/>'
    ),
    4: (
        '<path d="M0 0 V-14" stroke="#c49a2c" stroke-width="1.7" stroke-linecap="round"/>'
        '<ellipse cx="0" cy="-17" rx="2.4" ry="4.4" fill="#f2c94c"/>'
        '<path d="M-1.5 -20 L-3.5 -24 M1.5 -20 L3.5 -24 M0 -21 V-25" stroke="#e0b23c" stroke-width="1" '
        'stroke-linecap="round"/>'
    ),
}

STYLE = """
    .plant { transform-box: fill-box; transform-origin: 50% 100%; animation: sway 2.8s ease-in-out infinite alternate; }
    @keyframes sway { from { transform: rotate(-4deg); } to { transform: rotate(4deg); } }"""


def field(commits_by_day: Counter[date], today: date) -> Layer:
    days = shown_days(today)
    levels = plant_levels(commits_by_day, days, today)

    soil = slab() + tiles(len(days))
    plants = planted(days, levels)
    return Layer(soil + plants, style=STYLE)


def shown_days(today: date) -> list[date]:
    last_sunday = today - timedelta(days=(today.weekday() + 1) % DAYS_PER_WEEK)
    first_day = last_sunday - timedelta(weeks=WEEKS - 1)
    return [first_day + timedelta(days=offset) for offset in range(WEEKS * DAYS_PER_WEEK)]


def plant_levels(commits_by_day: Counter[date], days: list[date], today: date) -> dict[date, int]:
    busy_days = [day for day in days if day <= today and commits_by_day[day]]
    if not busy_days:
        return {}

    busy_counts = sorted(commits_by_day[day] for day in busy_days)
    quartiles = [busy_counts[int(len(busy_counts) * share)] for share in (0.25, 0.5, 0.75)]
    return {day: 1 + sum(commits_by_day[day] > quartile for quartile in quartiles) for day in busy_days}


def corner(column: float, row: float) -> Point:
    corner_x = LEFT + column * CELL_WIDTH + (DAYS_PER_WEEK - 1 - row) * SHEAR
    corner_y = BACK_Y + row * ROW_HEIGHT
    return corner_x, corner_y


def slab() -> str:
    left, right = -SLAB_OVERHANG, WEEKS + SLAB_OVERHANG
    back, front = -SLAB_OVERHANG, DAYS_PER_WEEK + SLAB_OVERHANG
    top = [corner(left, back), corner(right, back), corner(right, front), corner(left, front)]

    (front_left_x, front_y), (front_right_x, _) = top[3], top[2]
    edge_bottom = front_y + FRONT_EDGE_DEPTH
    edge = points(
        (front_left_x, front_y),
        (front_right_x, front_y),
        (front_right_x, edge_bottom),
        (front_left_x, edge_bottom),
    )

    top_points = points(*top)
    return f'<polygon points="{edge}" fill="{SLAB_EDGE}"/><polygon points="{top_points}" fill="{SLAB}"/>'


def tiles(count: int) -> str:
    shapes = []
    for index in range(count):
        column, row = divmod(index, DAYS_PER_WEEK)
        outline = points(
            corner(column + 0.06, row + 0.08),
            corner(column + 0.94, row + 0.08),
            corner(column + 0.94, row + 0.92),
            corner(column + 0.06, row + 0.92),
        )
        colour = SOIL_LIGHT if row % 2 else SOIL
        shapes.append(f'<polygon points="{outline}" fill="{colour}"/>')

    return f"<g>{''.join(shapes)}</g>"


def planted(days: list[date], levels: dict[date, int]) -> str:
    spots = []
    for index, day in enumerate(days):
        if day in levels:
            column, row = divmod(index, DAYS_PER_WEEK)
            spots.append((row, column, levels[day]))

    back_to_front = sorted(spots)
    return "".join(plant(row, column, level) for row, column, level in back_to_front)


def plant(row: int, column: int, level: int) -> str:
    base_x, base_y = corner(column + 0.5, row + 0.5)
    delay = column * SWAY_DELAY_PER_WEEK
    return (
        f'<g transform="translate({number(base_x)} {number(base_y)}) scale({PLANT_SCALE})">'
        f'<g class="plant" style="animation-delay:-{delay:.2f}s">{PLANT_SHAPES[level]}</g></g>'
    )
