import unicodedata
from typing import NamedTuple

from . import cow
from .svg import MONO, Layer, escape, group, number

WIDTH = 880
TITLE_BAR_HEIGHT = 36
FONT_SIZE = 15
LINE_HEIGHT = 22
CHARACTER_WIDTH = FONT_SIZE * 0.6
TEXT_LEFT = 24
PROMPT_Y = 72
INFO_TOP = PROMPT_Y + 36
INFO_LEFT = 400
LABEL_WIDTH = 184
COW_LEFT = 40
COW_WIDTH = 320
BLOCK_WIDTH = 26
BLOCK_HEIGHT = 15
BLANK_LINE = ""

USER = "anthony@montreal"
ROOT_USER = "root@anthony"
COMMAND = "neofetch"
COMMAND_X = TEXT_LEFT + len(f"{USER} ~ $ ") * CHARACTER_WIDTH
TYPING_START = 0.45
TYPING_DURATION = 0.6
OUTPUT_DELAY = 1.35
LINE_DELAY = 0.06
CLOSING_PROMPT_DELAY = 0.2

GREEN = "#3fb950"
RED = "#f85149"
WHITE = "#e6edf3"
BLUE = "#58a6ff"
DIM = "#6e7681"
WINDOW_BUTTONS = [(22, "#ff5f57"), (42, "#febc2e"), (62, "#28c840")]
PALETTE = ["#484f58", "#ff7b72", GREEN, "#d29922", BLUE, "#bc8cff", "#39c5cf", "#b1bac4"]

PROMPT = (
    f'<tspan fill="{GREEN}" font-weight="700">{USER}</tspan>'
    f'<tspan fill="{BLUE}"> ~ </tspan><tspan fill="{WHITE}">$ </tspan>'
)

STYLE = f"""
    .mono {{ font-family: {MONO}; font-size: {FONT_SIZE}px; fill: {WHITE}; }}
    .title {{ font-family: {MONO}; font-size: 12.5px; fill: #8b949e; }}
    .out {{ animation: print .15s ease-out both; }}
    .cursor {{ animation: blink 1.05s steps(1) infinite; }}
    @keyframes print {{ from {{ opacity: 0; }} }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}"""


class Row(NamedTuple):
    key: str
    value: list[tuple[str, str]]


class Section(NamedTuple):
    title: str
    rows: list[Row]


class Terminal(NamedTuple):
    drawing: Layer
    height: int


def neofetch_terminal(sections: list[Section]) -> Terminal:
    lines = report_lines(sections)
    info_lines = len(lines)
    blocks_y = INFO_TOP + info_lines * LINE_HEIGHT - 6
    closing_prompt_y = blocks_y + 52
    height = closing_prompt_y + 52
    blocks_delay = OUTPUT_DELAY + LINE_DELAY * info_lines

    logo = cow_logo(info_lines)
    elements = [
        window(height),
        prompt_line(PROMPT_Y),
        typed_command(),
        logo.body,
        *printed_lines(lines),
        colour_blocks(blocks_y, blocks_delay),
        closing_prompt(closing_prompt_y, blocks_delay + CLOSING_PROMPT_DELAY),
    ]

    drawing = Layer("\n".join(elements), typing_clip() + logo.defs, STYLE + logo.style)
    return Terminal(drawing, height)


def window(height: int) -> str:
    buttons = "".join(f'<circle cx="{button_x}" cy="18" r="6" fill="{colour}"/>' for button_x, colour in WINDOW_BUTTONS)
    title_bar = (
        f"M14.5 .5 H{WIDTH - 14.5} A14 14 0 0 1 {WIDTH - 0.5} 14.5 V{TITLE_BAR_HEIGHT} H.5 V14.5 A14 14 0 0 1 14.5 .5 Z"
    )
    return (
        f'<rect x=".5" y=".5" width="{WIDTH - 1}" height="{height - 1}" rx="14" fill="#0d1117" stroke="#30363d"/>'
        f'<path d="{title_bar}" fill="#161b22"/>'
        f'<line x1=".5" y1="{TITLE_BAR_HEIGHT}" x2="{WIDTH - 0.5}" y2="{TITLE_BAR_HEIGHT}" stroke="#30363d"/>'
        f"{buttons}"
        f'<text class="title" x="{WIDTH / 2}" y="23" text-anchor="middle">{ROOT_USER}: ~</text>'
    )


def prompt_line(y: float) -> str:
    return f'<text class="mono" x="{TEXT_LEFT}" y="{y}">{PROMPT}</text>'


def typed_command() -> str:
    return (
        f'<text class="mono" x="{number(COMMAND_X)}" y="{PROMPT_Y}" fill="{WHITE}" '
        f'clip-path="url(#command)">{COMMAND}</text>'
    )


def typing_clip() -> str:
    widths = ";".join(number(typed * CHARACTER_WIDTH) for typed in range(len(COMMAND) + 1))
    return (
        f'<clipPath id="command"><rect x="{number(COMMAND_X)}" y="{PROMPT_Y - 18}" width="0" height="24">'
        f'<animate attributeName="width" begin="{TYPING_START}s" dur="{TYPING_DURATION}s" fill="freeze" '
        f'calcMode="discrete" values="{widths}"/></rect></clipPath>'
    )


def cow_logo(info_lines: int) -> Layer:
    left, top, right, bottom = cow.BOUNDS
    scale = COW_WIDTH / (right - left)
    logo_height = (bottom - top) * scale
    logo_top = INFO_TOP + (info_lines * LINE_HEIGHT - logo_height) / 2 + 6

    figure = cow.cow_figure()
    scaled = group(f'transform="scale({scale:.4f}) translate({-left} {-top})"', figure)
    return group(
        f'class="out" style="animation-delay:{OUTPUT_DELAY:.2f}s" transform="translate({COW_LEFT} {number(logo_top)})"',
        scaled,
    )


def report_lines(sections: list[Section]) -> list[str]:
    lines = []
    for section in sections:
        if lines:
            lines.append(BLANK_LINE)
        lines.extend(section_lines(section))

    return lines


def section_lines(section: Section) -> list[str]:
    title = f'<tspan fill="{GREEN}" font-weight="700">{escape(section.title)}</tspan>'
    rule = f'<tspan fill="{DIM}">{"─" * columns(section.title)}</tspan>'
    rows = [report_row(row) for row in section.rows]
    return [title, rule, *rows]


def printed_lines(lines: list[str]) -> list[str]:
    return [output_line(index, line) for index, line in enumerate(lines) if line != BLANK_LINE]


def report_row(row: Row) -> str:
    value = "".join(f'<tspan fill="{colour}">{escape(text)}</tspan>' for text, colour in row.value)
    return (
        f'<tspan fill="{GREEN}" font-weight="700">{escape(row.key)}</tspan>'
        f'<tspan x="{INFO_LEFT + LABEL_WIDTH}">{value}</tspan>'
    )


def output_line(index: int, line: str) -> str:
    line_y = INFO_TOP + index * LINE_HEIGHT
    delay = OUTPUT_DELAY + LINE_DELAY * index
    return f'<text class="mono out" x="{INFO_LEFT}" y="{line_y}" style="animation-delay:{delay:.2f}s">{line}</text>'


def colour_blocks(y: float, delay: float) -> str:
    blocks = "".join(
        f'<rect x="{INFO_LEFT + index * BLOCK_WIDTH}" y="{y}" width="{BLOCK_WIDTH}" height="{BLOCK_HEIGHT}" '
        f'fill="{colour}"/>'
        for index, colour in enumerate(PALETTE)
    )
    return f'<g class="out" style="animation-delay:{delay:.2f}s">{blocks}</g>'


def closing_prompt(y: float, delay: float) -> str:
    cursor = f'<rect class="cursor" x="{number(COMMAND_X)}" y="{y - 13}" width="9" height="17" fill="{WHITE}"/>'
    return f'<g class="out" style="animation-delay:{delay:.2f}s">{prompt_line(y)}{cursor}</g>'


def columns(text: str) -> int:
    return sum(2 if unicodedata.east_asian_width(character) in "WF" else 1 for character in text)
