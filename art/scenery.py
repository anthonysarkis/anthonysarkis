from typing import NamedTuple

from .layout import SCENE_HEIGHT, WIDTH
from .svg import Layer, number, points


class Cloud(NamedTuple):
    start_x: int
    y: int
    scale: float
    crossing_seconds: int


class Tower(NamedTuple):
    left: float
    width: float
    top: float


CLOUDS = [Cloud(120, 70, 1.0, 95), Cloud(520, 46, 0.8, 120), Cloud(330, 128, 0.65, 140)]
SKYLINE_BASE = 262
SKYLINE_FILL = "#a9c3df"
MOUNTAIN_FILL = "#c2d6eb"
RIB_STROKE = "#c3d6eb"

MOUNT_ROYAL = (
    "M544 262 C558 248 576 230 598 220 C612 214 626 212 640 212.5 C654 213 664 218 676 227 C690 238 702 250 710 262 Z"
)
MOUNT_ROYAL_CROSS = Tower(627.2, 1.6, 198)
MOUNT_ROYAL_CROSSBAR = Tower(623.5, 9, 202.5)

PLAIN_TOWERS = [
    Tower(646, 8, 236),
    Tower(655, 7, 227),
    Tower(678, 8, 231),
    Tower(709, 9, 223),
    Tower(719, 7, 233),
    Tower(727, 8, 229),
]
PLACE_VILLE_MARIE = Tower(663, 14, 219)
LA_GAUCHETIERE = Tower(687, 10, 214)
RENE_LEVESQUE = Tower(698, 10, 216)

OLYMPIC_TOWER = "M742 262 V247.5 C762 246.5 779 238 792 204 L802 201.5 C797 211 788 226 781 240 L778 262 Z"
OLYMPIC_TOWER_SLATS = "M767.5 241 H779.5 M771.5 237.5 H780.5 M775.5 234 H782.5 M778.5 230.5 H784.5"
OLYMPIC_TOWER_TOP = (800, 204)
OLYMPIC_BOWL = "M770 262 C770 250 773 241.5 784 240.5 C800 238.2 834 237.5 850 240 C858 241.5 864 248 865 262 Z"
OLYMPIC_ROOF_RIM = "M793 242.5 C807 240 834 240 849 242.5"
OLYMPIC_ROOF_ANCHORS = [(814, 238.2), (824, 238.2), (834, 238.5), (844, 239.2)]
OLYMPIC_RIB_TOPS = range(798, 848, 6)
OLYMPIC_RIB_TOP_Y = 244
OLYMPIC_MIDDLE_X = 821
OLYMPIC_RIB_LEAN = 0.3
SUN_CENTER = (792, 82)
ROAD_HEIGHT = 26

SKY_GRADIENT = (
    '<linearGradient id="farm-sky" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#8fcbff"/><stop offset=".5" stop-color="#cfe9ff"/>'
    '<stop offset=".62" stop-color="#ffe9c7"/></linearGradient>'
)
SUN_GRADIENTS = (
    '<radialGradient id="sun-glow"><stop offset="0" stop-color="#fff3c4" stop-opacity=".9"/>'
    '<stop offset="1" stop-color="#fff3c4" stop-opacity="0"/></radialGradient>'
    '<radialGradient id="sun-face" cx=".4" cy=".35"><stop offset="0" stop-color="#fff6d5"/>'
    '<stop offset="1" stop-color="#ffd56b" stop-opacity="0"/></radialGradient>'
)
SUN_STYLE = """
    .rays { animation: spin 60s linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }"""
CLOUD_STYLE = """
    .cloud { animation: drift linear infinite; }
    @keyframes drift { from { transform: translateX(-160px); } to { transform: translateX(1040px); } }"""


def sky() -> Layer:
    return Layer(f'<rect width="{WIDTH}" height="{SCENE_HEIGHT}" fill="url(#farm-sky)"/>', SKY_GRADIENT)


def sun() -> Layer:
    center_x, center_y = SUN_CENTER
    rays = "".join(
        f'<path d="M-3 -44 L0 -62 L3 -44 Z" fill="#ffd56b" opacity=".55" transform="rotate({angle})"/>'
        for angle in range(0, 360, 30)
    )
    body = (
        f'<g transform="translate({center_x} {center_y})"><circle r="120" fill="url(#sun-glow)"/>'
        f'<g class="rays">{rays}</g>'
        '<circle r="30" fill="#ffd56b"/><circle r="30" fill="url(#sun-face)"/></g>'
    )
    return Layer(body, SUN_GRADIENTS, SUN_STYLE)


def clouds() -> Layer:
    shapes = "".join(cloud(drifting) for drifting in CLOUDS)
    return Layer(shapes, style=CLOUD_STYLE)


def cloud(drifting: Cloud) -> str:
    duration = drifting.crossing_seconds
    head_start = duration * drifting.start_x / 1080
    return (
        f'<g class="cloud" style="animation-duration:{duration}s;animation-delay:-{head_start:.1f}s">'
        f'<g transform="translate(0 {drifting.y}) scale({drifting.scale})" fill="#ffffff" opacity=".92">'
        '<ellipse cx="0" cy="0" rx="46" ry="16"/><ellipse cx="-18" cy="-10" rx="22" ry="16"/>'
        '<ellipse cx="14" cy="-14" rx="26" ry="20"/></g></g>'
    )


def skyline() -> Layer:
    mountain = mount_royal()
    cross = mount_royal_cross()
    city = downtown()
    stadium = olympic_stadium()
    return Layer(f'{mountain}<g fill="{SKYLINE_FILL}" opacity=".75">{cross}{city}{stadium}</g>')


def mount_royal() -> str:
    return f'<path d="{MOUNT_ROYAL}" fill="{MOUNTAIN_FILL}" opacity=".75"/>'


def mount_royal_cross() -> str:
    upright = bar(MOUNT_ROYAL_CROSS, 213)
    crossbar = bar(MOUNT_ROYAL_CROSSBAR, MOUNT_ROYAL_CROSSBAR.top + 1.6)
    return upright + crossbar


def downtown() -> str:
    plain = "".join(plain_tower(tower) for tower in PLAIN_TOWERS)
    beacon = beacon_tower(PLACE_VILLE_MARIE)
    pyramid = pyramid_tower(LA_GAUCHETIERE)
    stepped = stepped_tower(RENE_LEVESQUE)
    return plain + beacon + pyramid + stepped


def plain_tower(tower: Tower) -> str:
    return bar(tower, SKYLINE_BASE)


def beacon_tower(tower: Tower) -> str:
    body = plain_tower(tower)
    mast_left = tower.left + tower.width / 2 - 0.6
    mast = Tower(mast_left, 1.2, tower.top - 6)
    return body + plain_tower(mast)


def pyramid_tower(tower: Tower) -> str:
    body = plain_tower(tower)
    right = tower.left + tower.width
    peak = (tower.left + tower.width / 2, tower.top - tower.width * 0.9)
    corners = points((tower.left, tower.top), peak, (right, tower.top))
    return f'{body}<polygon points="{corners}"/>'


def stepped_tower(tower: Tower) -> str:
    body = plain_tower(tower)
    first_step = Tower(tower.left + 1.5, tower.width - 3, tower.top - 3)
    second_step = Tower(tower.left + 3, tower.width - 6, tower.top - 6)
    return body + plain_tower(first_step) + plain_tower(second_step)


def bar(tower: Tower, bottom: float) -> str:
    left = number(tower.left)
    top = number(tower.top)
    width = number(tower.width)
    height = number(bottom - tower.top)
    return f'<rect x="{left}" y="{top}" width="{width}" height="{height}"/>'


def olympic_stadium() -> str:
    ribs = olympic_ribs()
    cables = olympic_cables()
    return (
        f'<path d="{OLYMPIC_TOWER}"/>'
        f'<path d="{OLYMPIC_TOWER_SLATS}" stroke="{RIB_STROKE}" stroke-width=".9"/>'
        f'<path d="{OLYMPIC_BOWL}"/>'
        f'<path d="{OLYMPIC_ROOF_RIM} {ribs}" stroke="{RIB_STROKE}" stroke-width=".9" fill="none"/>'
        f'<path d="{cables}" stroke="{SKYLINE_FILL}" stroke-width=".8" fill="none"/>'
    )


def olympic_ribs() -> str:
    ribs = []
    for top_x in OLYMPIC_RIB_TOPS:
        lean = (top_x - OLYMPIC_MIDDLE_X) * OLYMPIC_RIB_LEAN
        bottom_x = number(top_x + lean)
        ribs.append(f"M{top_x} {OLYMPIC_RIB_TOP_Y} Q{top_x} 255 {bottom_x} {SKYLINE_BASE}")

    return " ".join(ribs)


def olympic_cables() -> str:
    top_x, top_y = OLYMPIC_TOWER_TOP
    cables = [f"M{top_x} {top_y} L{number(anchor_x)} {number(anchor_y)}" for anchor_x, anchor_y in OLYMPIC_ROOF_ANCHORS]
    return " ".join(cables)


def hills(bottom: int) -> Layer:
    far_hill = (
        f"M0 262 C120 226 240 236 360 250 C480 264 600 238 720 246 C800 251 850 258 880 262 L880 {bottom} L0 {bottom} Z"
    )
    near_hill = f"M0 286 C140 266 300 274 440 282 C600 291 760 276 880 284 L880 {bottom} L0 {bottom} Z"
    return Layer(f'<path d="{far_hill}" fill="#a9d18e"/><path d="{near_hill}" fill="#8cc06c"/>')


def barn() -> Layer:
    silo = (
        '<rect x="70" y="10" width="26" height="70" fill="#d5d9e0"/>'
        '<path d="M70 10 A13 13 0 0 1 96 10 Z" fill="#aab1bc"/>'
        '<path d="M70 30 H96 M70 50 H96" stroke="#b8bec8" stroke-width="2"/>'
    )
    shed = (
        '<path d="M0 36 L36 8 L72 36 V82 H0 Z" fill="#c0392b"/>'
        '<path d="M-4 38 L36 4 L76 38" fill="none" stroke="#f5f1e8" stroke-width="4" stroke-linejoin="round"/>'
        '<rect x="22" y="48" width="28" height="34" fill="#9e2f24" stroke="#f5f1e8" stroke-width="2.5"/>'
        '<path d="M22 48 L50 82 M50 48 L22 82" stroke="#f5f1e8" stroke-width="2"/>'
        '<rect x="30" y="22" width="12" height="10" fill="#f5f1e8"/>'
    )
    return Layer(f'<g transform="translate(38 196)">{silo}{shed}</g>')


def road(top: float) -> Layer:
    lanes = f"M0 {number(top + 9)} H{WIDTH} M0 {number(top + 18)} H{WIDTH}"
    return Layer(
        f'<rect x="0" y="{number(top)}" width="{WIDTH}" height="{ROAD_HEIGHT}" fill="#d2b083"/>'
        f'<path d="{lanes}" stroke="#bf9a6a" stroke-width="2" stroke-dasharray="6 8"/>'
    )
