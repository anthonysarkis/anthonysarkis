from .svg import Layer, blob_path, closed_curve, number

GRASS = "#8cc63e"
GRASS_DEEP = "#74ad35"
INK = "#2b2622"
COAT = "#fffdf8"
COAT_FAR = "#ebe5db"
PINK = "#f6b9ae"
PINK_DEEP = "#e3928a"
HORN = "#ead09b"
HOOF = "#74675d"
HOOF_FAR = "#5d5249"
SHADOW = "#18261c"

BOUNDS = (-18, 30, 332, 197)
GROUND_Y = 190
LEG_TOP = 112
HOOF_HEIGHT = 13
RIM_WIDTH = 3
BLADE_WIDTH = 6.5

BODY_OUTLINE = closed_curve(
    [
        (165, 38),
        (202, 42),
        (248, 33),
        (280, 38),
        (300, 64),
        (299, 102),
        (283, 131),
        (252, 149),
        (205, 155),
        (160, 147),
        (130, 135),
        (112, 122),
        (98, 130),
        (86, 150),
        (66, 134),
        (76, 100),
        (100, 66),
        (130, 44),
    ]
)
BODY_PATCHES = [
    closed_curve(
        [
            (186, 28),
            (214, 26),
            (240, 24),
            (246, 44),
            (236, 58),
            (241, 72),
            (224, 84),
            (205, 79),
            (189, 87),
            (175, 76),
            (180, 60),
            (171, 46),
        ]
    ),
    closed_curve(
        [
            (270, 22),
            (312, 26),
            (316, 100),
            (299, 106),
            (287, 98),
            (276, 104),
            (268, 90),
            (274, 76),
            (265, 60),
            (271, 44),
        ]
    ),
    closed_curve([(167, 114), (185, 106), (202, 113), (200, 129), (186, 138), (170, 133), (160, 124)]),
]
HEAD_OUTLINE = "M0 -50C34 -50 44 -28 41 -4C38 16 30 26 0 28C-30 26 -38 16 -41 -4C-44 -28 -34 -50 0 -50Z"
HEAD_PATCH = blob_path((-25, -42), 21, 15, (1.0, 1.1, 0.9, 1.15, 0.95, 1.05, 0.9))

SMALL_TUFT = [(-6, 12, -3, GRASS_DEEP), (0, 17, 1, GRASS), (6, 11, 4, GRASS_DEEP)]
EATEN_TUFT = [
    (-14, 16, -3, GRASS_DEEP),
    (-6, 24, -2, GRASS),
    (2, 20, 3, GRASS_DEEP),
    (10, 26, 4, GRASS),
    (17, 15, 5, GRASS_DEEP),
]

STYLE = """
    .nod { animation: nod 6.5s ease-in-out infinite; }
    .chew { animation: chew .55s ease-in-out infinite alternate; }
    .swish { transform-origin: 288px 42px; animation: swish 5.2s ease-in-out infinite; }
    .flick { animation: flick 7.3s ease-in-out infinite; }
    .eyes { transform-box: fill-box; transform-origin: center; animation: eye-blink 4.8s infinite; }
    .blades { transform-box: fill-box; transform-origin: 50% 100%; animation: blade-sway 3.4s ease-in-out infinite alternate; }
    .blades-slow { animation-duration: 4.6s; }
    @keyframes nod { 0%, 52% { transform: rotate(0deg); } 62%, 70% { transform: rotate(3deg); } 82%, 100% { transform: rotate(0deg); } }
    @keyframes chew { from { transform: translateX(-1.3px); } to { transform: translateX(1.3px); } }
    @keyframes swish { 0%, 70% { transform: rotate(0deg); } 76% { transform: rotate(-13deg); } 84% { transform: rotate(7deg); }
                       90% { transform: rotate(-3deg); } 96%, 100% { transform: rotate(0deg); } }
    @keyframes flick { 0%, 84% { transform: rotate(0deg); } 87% { transform: rotate(-16deg); } 90% { transform: rotate(5deg); }
                       93%, 100% { transform: rotate(0deg); } }
    @keyframes eye-blink { 0%, 93%, 100% { transform: scaleY(1); } 96% { transform: scaleY(.12); } }
    @keyframes blade-sway { from { transform: rotate(-3deg); } to { transform: rotate(3deg); } }
"""


def cow_figure() -> Layer:
    parts = [
        shadow(),
        tail(),
        leg(155, 25, COAT_FAR, HOOF_FAR),
        leg(228, 25, COAT_FAR, HOOF_FAR),
        udder(),
        leg(124, 27, COAT, HOOF),
        leg(257, 27, COAT, HOOF),
        body(),
        head(),
        tuft(70, GROUND_Y + 4, EATEN_TUFT, "blades blades-slow"),
        tuft(114, GROUND_Y + 2, SMALL_TUFT, "blades"),
        tuft(293, GROUND_Y + 3, SMALL_TUFT, "blades blades-slow"),
    ]
    clips = (
        f'<clipPath id="cow-body"><path d="{BODY_OUTLINE}"/></clipPath>'
        f'<clipPath id="cow-head"><path d="{HEAD_OUTLINE}"/></clipPath>'
    )
    return Layer("\n".join(parts), clips, STYLE)


def shadow() -> str:
    return f'<ellipse cx="203" cy="{GROUND_Y}" rx="100" ry="7" fill="{SHADOW}"/>'


def tail() -> str:
    return (
        '<g class="swish">'
        f'<path d="M288 42C306 48 313 80 309 106S305 126 307 130" fill="none" stroke="{COAT}" stroke-width="7" '
        'stroke-linecap="round"/>'
        f'<path fill="{HOOF}" d="M307 121C317 131 316 149 306 155C296 149 297 131 307 121Z"/>'
        "</g>"
    )


def leg(left_x: float, width: float, coat: str, hoof: str) -> str:
    whole_leg = rounded_bottom(left_x, LEG_TOP, width, GROUND_Y)
    hoof_only = rounded_bottom(left_x, GROUND_Y - HOOF_HEIGHT, width, GROUND_Y)
    return f'<path fill="{coat}" d="{whole_leg}"/><path fill="{hoof}" d="{hoof_only}"/>'


def rounded_bottom(left_x: float, top_y: float, width: float, bottom_y: float) -> str:
    corner = 7
    right_x = left_x + width
    return (
        f"M{number(left_x)} {number(top_y)}H{number(right_x)}V{number(bottom_y - corner)}"
        f"Q{number(right_x)} {number(bottom_y)} {number(right_x - corner)} {number(bottom_y)}"
        f"H{number(left_x + corner)}Q{number(left_x)} {number(bottom_y)} {number(left_x)} {number(bottom_y - corner)}Z"
    )


def udder() -> str:
    return (
        f'<path fill="{PINK}" d="M199 146C197 165 233 165 231 146Z"/>'
        f'<rect x="206" y="159" width="6" height="10" rx="3" fill="{PINK_DEEP}"/>'
        f'<rect x="219" y="159" width="6" height="10" rx="3" fill="{PINK_DEEP}"/>'
    )


def body() -> str:
    patches = "".join(f'<path d="{patch}"/>' for patch in BODY_PATCHES)
    return (
        f'<path fill="{COAT}" d="{BODY_OUTLINE}"/>'
        f'<g clip-path="url(#cow-body)" fill="{INK}">{patches}</g>'
        f"{coat_rim(BODY_OUTLINE, 'cow-body')}"
    )


def head() -> str:
    face = horns() + ears() + skull() + eyes() + muzzle()
    return (
        f'<g class="nod" style="transform-origin:96px 104px"><g transform="translate(70 136) rotate(-6)">{face}</g></g>'
    )


def horns() -> str:
    return (
        f'<g fill="{HORN}">'
        '<path d="M-20 -43C-27 -49 -31 -57 -28 -65C-27 -67 -24 -67 -23 -65C-21 -58 -16 -52 -9 -48Z"/>'
        '<path d="M20 -43C27 -49 31 -57 28 -65C27 -67 24 -67 23 -65C21 -58 16 -52 9 -48Z"/>'
        "</g>"
    )


def ears() -> str:
    return (
        f'<g transform="translate(-36 -24)">{ear(COAT)}</g>'
        '<g class="flick" style="transform-origin:36px -22px">'
        f'<g transform="translate(36 -24) scale(-1 1)">{ear(INK)}</g>'
        "</g>"
    )


def ear(colour: str) -> str:
    return (
        f'<path fill="{colour}" d="M0 0C-19 -16 -41 -15 -48 -5C-54 4 -35 20 -1 17Z"/>'
        f'<path fill="{PINK}" d="M-4 4C-18 -6 -34 -5 -40 1C-43 6 -31 14 -5 13Z"/>'
    )


def skull() -> str:
    return (
        f'<path fill="{COAT}" d="{HEAD_OUTLINE}"/>'
        f'<path clip-path="url(#cow-head)" fill="{INK}" d="{HEAD_PATCH}"/>'
        f"{coat_rim(HEAD_OUTLINE, 'cow-head')}"
    )


def eyes() -> str:
    return (
        f'<g class="eyes" fill="{INK}">'
        '<circle cx="-16" cy="-11" r="8.8"/><circle cx="16" cy="-11" r="8.8"/>'
        '<circle cx="-19" cy="-14.8" r="3.1" fill="#fff"/><circle cx="13" cy="-14.8" r="3.1" fill="#fff"/>'
        "</g>"
    )


def muzzle() -> str:
    eaten_blade = blade(0, 0, 5, 26, 3)
    return (
        '<g class="chew">'
        f'<g transform="translate(-23 40) rotate(-125)"><path fill="{GRASS}" d="{eaten_blade}"/></g>'
        f'<ellipse cx="0" cy="27" rx="33" ry="21" fill="{PINK}"/>'
        f'<ellipse cx="-12" cy="26" rx="3.8" ry="5.6" transform="rotate(-18 -12 26)" fill="{PINK_DEEP}"/>'
        f'<ellipse cx="12" cy="26" rx="3.8" ry="5.6" transform="rotate(18 12 26)" fill="{PINK_DEEP}"/>'
        "</g>"
    )


def coat_rim(outline: str, clip_id: str) -> str:
    return (
        f'<path clip-path="url(#{clip_id})" d="{outline}" fill="none" stroke="{COAT}" stroke-width="{RIM_WIDTH * 2}"/>'
    )


def tuft(base_x: float, base_y: float, blades: list[tuple[float, float, float, str]], motion: str) -> str:
    shapes = "".join(
        f'<path fill="{colour}" d="{blade(base_x + offset, base_y, BLADE_WIDTH, height, lean)}"/>'
        for offset, height, lean, colour in blades
    )
    return f'<g class="{motion}">{shapes}</g>'


def blade(base_x: float, base_y: float, width: float, height: float, lean: float) -> str:
    left = base_x - width / 2
    right = base_x + width / 2
    return (
        f"M{number(left)} {number(base_y)}"
        f"Q{number(left + lean * 0.35)} {number(base_y - height * 0.55)} {number(base_x + lean)} {number(base_y - height)}"
        f"Q{number(right + lean * 0.25)} {number(base_y - height * 0.5)} {number(right)} {number(base_y)}Z"
    )
