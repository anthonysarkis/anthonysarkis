from harvest.stats import Harvest

from .field import FRONT_Y, field
from .layout import SCENE_HEIGHT, WIDTH
from .report import HEADER, report_label, report_rows
from .scenery import barn, clouds, hills, road, sky, skyline, sun
from .svg import FONT, REDUCED_MOTION, Layer, group, stack, svg_document
from .terminal import neofetch_terminal
from .tractor import tractor

LABEL = "Hey, I'm Anthony. A farm where every plant is a day of commits."
ROAD_TOP = FRONT_Y + 18
TERMINAL_MARGIN = 24
TERMINAL_TOP = SCENE_HEIGHT + 10
TERMINAL_SCALE = (WIDTH - 2 * TERMINAL_MARGIN) / WIDTH

TITLES_STYLE = f"""
    text {{ font-family: {FONT}; }}
    .hello {{ font-size: 36px; font-weight: 800; fill: #1f2a37; letter-spacing: -.5px; }}
    .tagline {{ font-size: 19px; font-weight: 500; fill: #334155; }}
    .caption {{ font-size: 12px; font-weight: 600; fill: #24421a; }}"""


def farm_svg(harvest: Harvest) -> str:
    rows = report_rows(harvest)
    terminal = neofetch_terminal(HEADER, rows)
    card_height = round(TERMINAL_TOP + terminal.height * TERMINAL_SCALE + TERMINAL_MARGIN)

    scene = farm_scene(harvest, card_height)
    farm = card(scene, card_height)
    report = group(
        f'transform="translate({TERMINAL_MARGIN} {TERMINAL_TOP}) scale({TERMINAL_SCALE:.4f})"',
        terminal.drawing,
    )
    reduced_motion = Layer("", style=f"\n    {REDUCED_MOTION}\n")
    picture = stack(farm, report, reduced_motion)

    summary = report_label(harvest)
    label = f"{LABEL} {summary}"
    return svg_document(WIDTH, card_height, label, picture)


def farm_scene(harvest: Harvest, height: int) -> Layer:
    parts = [
        sky(),
        sun(),
        clouds(),
        skyline(),
        hills(height),
        barn(),
        field(harvest.commits_by_day, harvest.day),
        road(ROAD_TOP),
        tractor(ROAD_TOP),
        titles(),
    ]
    return stack(*parts)


def titles() -> Layer:
    return Layer(
        '<text class="hello" x="34" y="64">Hey, I\'m Anthony 👋</text>'
        '<text class="tagline" x="36" y="96">Software dev. Farmer at heart.</text>'
        f'<text class="caption" x="{WIDTH - 24}" y="{SCENE_HEIGHT - 14}" text-anchor="end">'
        "My field: every plant is a day of commits, last 12 months</text>",
        style=TITLES_STYLE,
    )


def card(scene: Layer, height: int) -> Layer:
    clip = f'<clipPath id="farm-card"><rect width="{WIDTH}" height="{height}" rx="18"/></clipPath>'
    border = (
        f'<rect x=".5" y=".5" width="{WIDTH - 1}" height="{height - 1}" rx="17.5" fill="none" '
        'stroke="rgba(0,0,0,.08)"/>'
    )
    clipped = group('clip-path="url(#farm-card)"', scene)
    return Layer(clipped.body + border, clip + clipped.defs, clipped.style)
