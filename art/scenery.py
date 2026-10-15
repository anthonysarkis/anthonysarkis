from typing import NamedTuple

from .layout import SCENE_HEIGHT, WIDTH
from .svg import Layer, number


class Cloud(NamedTuple):
    start_x: int
    y: int
    scale: float
    crossing_seconds: int


class Tower(NamedTuple):
    left: int
    width: int
    height: int


CLOUDS = [Cloud(120, 70, 1.0, 95), Cloud(520, 46, 0.8, 120), Cloud(330, 128, 0.65, 140)]
DOWNTOWN = [
    Tower(690, 7, 16),
    Tower(699, 6, 24),
    Tower(707, 9, 30),
    Tower(718, 6, 38),
    Tower(726, 8, 34),
    Tower(736, 6, 22),
    Tower(744, 7, 18),
]
HORIZON_Y = 252
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
    towers = "".join(
        f'<rect x="{tower.left}" y="{HORIZON_Y - tower.height}" width="{tower.width}" height="{tower.height}"/>'
        for tower in DOWNTOWN
    )
    mount_royal = '<path d="M560 252 C585 238 610 232 640 236 C660 239 676 246 690 252 Z"/>'
    olympic_stadium = '<path d="M762 252 L766 252 L781 226 L778 224 Z"/><path d="M758 252 C766 244 784 243 794 252 Z"/>'
    return Layer(f'<g fill="#a9c3df" opacity=".75">{mount_royal}{towers}{olympic_stadium}</g>')


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
