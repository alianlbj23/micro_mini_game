from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import pygame


SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

WHITE = (255, 255, 255)
BLACK = (15, 23, 42)
BG = (239, 246, 255)
CARD = (255, 255, 255)
INK = (30, 41, 59)
MUTED = (100, 116, 139)
LINE = (203, 213, 225)
BLUE = (37, 99, 235)
CYAN = (8, 145, 178)
GREEN = (22, 163, 74)
RED = (220, 38, 38)
AMBER = (217, 119, 6)
VIOLET = (124, 58, 237)
SLATE = (51, 65, 85)
SOFT_BLUE = (219, 234, 254)
SOFT_GREEN = (220, 252, 231)
SOFT_AMBER = (254, 243, 199)


def load_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Return a font that works with Chinese and Japanese when available."""
    font_dir = Path(__file__).with_name("assets") / "fonts"
    local_regular = font_dir / "NotoSansCJK-Regular.ttc"
    local_bold = font_dir / "NotoSansCJK-Bold.ttc"
    candidates = [
        str(local_bold if bold else local_regular),
        str(local_regular),
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" if bold else "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return pygame.font.Font(path, size)

    names = [
        "Noto Sans CJK TC",
        "Noto Sans CJK JP",
        "WenQuanYi Zen Hei",
        "Microsoft JhengHei",
        "Microsoft YaHei",
        "PingFang TC",
        "Hiragino Sans",
        "Heiti TC",
        "STHeiti",
        "SimHei",
        "Arial Unicode MS",
    ]
    for name in names:
        matched = pygame.font.match_font(name, bold=bold)
        if matched:
            return pygame.font.Font(matched, size)
    return pygame.font.SysFont(None, size, bold=bold)


def make_fonts() -> Dict[str, pygame.font.Font]:
    return {
        "title": load_font(32, True),
        "subtitle": load_font(22, True),
        "normal": load_font(18),
        "small": load_font(15),
        "tiny": load_font(13),
        "button": load_font(19, True),
        "number": load_font(30, True),
    }


def tr(data: Dict[str, str], lang: str) -> str:
    return data.get(lang) or data.get("zh") or next(iter(data.values()))


def draw_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: Tuple[int, int, int],
    pos: Tuple[int, int],
) -> pygame.Rect:
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(topleft=pos)
    surface.blit(rendered, rect)
    return rect


def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> List[str]:
    lines: List[str] = []
    for raw_line in text.splitlines():
        current = ""
        for token in raw_line.split(" "):
            candidate = token if not current else f"{current} {token}"
            if font.size(candidate)[0] <= max_width:
                current = candidate
                continue
            if current:
                lines.append(current)
            current = token
            while font.size(current)[0] > max_width and len(current) > 1:
                cut = max(1, len(current) - 1)
                while cut > 1 and font.size(current[:cut])[0] > max_width:
                    cut -= 1
                lines.append(current[:cut])
                current = current[cut:]
        lines.append(current)
    return lines


def draw_wrapped(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: Tuple[int, int, int],
    rect: pygame.Rect,
    line_gap: int = 6,
    max_lines: int | None = None,
) -> int:
    y = rect.y
    lines = wrap_text(text, font, rect.width)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        if y + font.get_height() > rect.bottom:
            break
        draw_text(surface, line, font, color, (rect.x, y))
        y += font.get_height() + line_gap
    return y


def button(
    surface: pygame.Surface,
    rect: pygame.Rect,
    label: str,
    font: pygame.font.Font,
    bg: Tuple[int, int, int],
    fg: Tuple[int, int, int] = WHITE,
    border: Tuple[int, int, int] | None = None,
) -> None:
    pygame.draw.rect(surface, bg, rect, border_radius=8)
    if border:
        pygame.draw.rect(surface, border, rect, 2, border_radius=8)
    rendered = font.render(label, True, fg)
    surface.blit(rendered, rendered.get_rect(center=rect.center))
