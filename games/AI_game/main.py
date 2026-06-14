from __future__ import annotations

import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pygame


# -----------------------------
# Main settings
# -----------------------------
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TOTAL_ROUNDS = 10
FEEDBACK_DURATION = 800

BASE_DIR = Path(__file__).resolve().parent
AI_DIR = BASE_DIR / "pic" / "AI"
NON_AI_DIR = BASE_DIR / "pic" / "non_AI"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


# -----------------------------
# Colors
# -----------------------------
WHITE = (255, 255, 255)
BG = (239, 246, 255)
CARD = (255, 255, 255)
BLACK = (15, 23, 42)
INK = (30, 41, 59)
MUTED = (100, 116, 139)
LINE = (203, 213, 225)
BLUE = (37, 99, 235)
GREEN = (22, 163, 74)
RED = (220, 38, 38)
AMBER = (217, 119, 6)
SOFT_BLUE = (219, 234, 254)
SOFT_GREEN = (220, 252, 231)
SOFT_RED = (254, 226, 226)


TEXT: Dict[str, Dict[str, str]] = {
    "zh": {
        "title": "AI 照片判斷遊戲",
        "subtitle": "請從左右兩張圖片中選出 AI 生成照片",
        "start": "開始遊戲",
        "restart": "重新開始",
        "back": "回主畫面",
        "round": "第 {current} / {total} 關",
        "score": "答對數：{score}",
        "time": "時間：{seconds:.1f} 秒",
        "left": "左邊",
        "right": "右邊",
        "correct": "答對了！",
        "wrong": "答錯了！",
        "finished": "遊戲結束",
        "correct_count": "你答對了 {score} / {total} 題",
        "clear_time": "通關時間：{seconds:.1f} 秒",
        "perfect": "全部答對！",
        "review": "錯誤題目回顧",
        "answer_is_ai": "正確答案是 AI 圖",
        "load_error": "圖片數量不足或讀取失敗，請確認 pic/AI 與 pic/non_AI 資料夾各至少有 10 張圖片。",
    },
    "ja": {
        "title": "AI 写真判定ゲーム",
        "subtitle": "左右2枚の写真から AI 生成写真を選んでください",
        "start": "ゲーム開始",
        "restart": "もう一度",
        "back": "メニューへ",
        "round": "第 {current} / {total} ステージ",
        "score": "正解数：{score}",
        "time": "時間：{seconds:.1f} 秒",
        "left": "左",
        "right": "右",
        "correct": "正解です！",
        "wrong": "不正解です！",
        "finished": "ゲーム終了",
        "correct_count": "{score} / {total} 問正解しました",
        "clear_time": "クリアタイム：{seconds:.1f} 秒",
        "perfect": "全問正解！",
        "review": "間違えた問題の確認",
        "answer_is_ai": "正解は AI 画像です",
        "load_error": "画像数が足りない、または読み込みに失敗しました。pic/AI と pic/non_AI に各10枚以上あるか確認してください。",
    },
}


def load_font(size: int, bold: bool = False) -> pygame.font.Font:
    font_dir = BASE_DIR.parents[1] / "assets" / "fonts"
    regular = font_dir / "NotoSansCJK-Regular.ttc"
    bold_font = font_dir / "NotoSansCJK-Bold.ttc"
    if bold and bold_font.exists():
        return pygame.font.Font(str(bold_font), size)
    if regular.exists():
        return pygame.font.Font(str(regular), size)

    candidates = [
        "Noto Sans CJK TC",
        "Noto Sans CJK JP",
        "Microsoft JhengHei",
        "Microsoft YaHei",
        "PingFang TC",
        "Hiragino Sans",
        "Arial Unicode MS",
    ]
    for name in candidates:
        matched = pygame.font.match_font(name, bold=bold)
        if matched:
            return pygame.font.Font(matched, size)
    return pygame.font.SysFont(None, size, bold=bold)


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


def draw_center_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: Tuple[int, int, int],
    center: Tuple[int, int],
) -> pygame.Rect:
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=center)
    surface.blit(rendered, rect)
    return rect


def natural_key(path: Path) -> Tuple[int, object]:
    return (0, int(path.stem)) if path.stem.isdigit() else (1, path.name.lower())


def fit_image(image: pygame.Surface, max_size: Tuple[int, int]) -> pygame.Surface:
    max_w, max_h = max_size
    src_w, src_h = image.get_size()
    scale = min(max_w / src_w, max_h / src_h)
    new_size = (max(1, int(src_w * scale)), max(1, int(src_h * scale)))
    return pygame.transform.smoothscale(image, new_size)


class Button:
    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        font: pygame.font.Font,
        bg_color: Tuple[int, int, int] = BLUE,
        text_color: Tuple[int, int, int] = WHITE,
        border_color: Optional[Tuple[int, int, int]] = None,
    ) -> None:
        self.rect = rect
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.border_color = border_color

    def draw(self, surface: pygame.Surface) -> None:
        mouse = pygame.mouse.get_pos()
        bg = self.bg_color
        if self.rect.collidepoint(mouse):
            bg = tuple(min(255, value + 18) for value in self.bg_color)
        pygame.draw.rect(surface, bg, self.rect, border_radius=8)
        if self.border_color:
            pygame.draw.rect(surface, self.border_color, self.rect, 2, border_radius=8)
        draw_center_text(surface, self.text, self.font, self.text_color, self.rect.center)

    def is_clicked(self, event: pygame.event.Event) -> bool:
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


@dataclass
class ImageQuestion:
    round_number: int
    ai_image: Path
    non_ai_image: Path
    answer: str

    @property
    def left_image(self) -> Path:
        return self.ai_image if self.answer == "left" else self.non_ai_image

    @property
    def right_image(self) -> Path:
        return self.non_ai_image if self.answer == "left" else self.ai_image

    @property
    def correct_image(self) -> Path:
        return self.ai_image


class Game:
    def __init__(
        self,
        screen: Optional[pygame.Surface] = None,
        embedded: bool = False,
        initial_lang: str = "zh",
        on_back=None,
    ) -> None:
        pygame.init()
        self.embedded = embedded
        self.on_back = on_back
        self.screen = screen or pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("AI Photo Judgment Game")

        self.width, self.height = self.screen.get_size()
        self.clock = pygame.time.Clock()
        self.lang = initial_lang if initial_lang in TEXT else "zh"
        self.font_title = load_font(34, True)
        self.font_subtitle = load_font(24, True)
        self.font_normal = load_font(18)
        self.font_small = load_font(15)
        self.font_button = load_font(20, True)

        self.running = True
        self.state = "menu"
        self.questions: List[ImageQuestion] = []
        self.current_index = 0
        self.score = 0
        self.wrong_records: List[dict] = []
        self.start_ticks: Optional[int] = None
        self.end_ticks: Optional[int] = None
        self.feedback_text = ""
        self.feedback_is_correct = False
        self.feedback_start = 0
        self.error_message = ""
        self.scroll_y = 0
        self.image_cache: Dict[Tuple[Path, Tuple[int, int]], pygame.Surface] = {}

    def t(self, key: str, **kwargs) -> str:
        value = TEXT.get(self.lang, TEXT["zh"]).get(key, TEXT["zh"][key])
        return value.format(**kwargs) if kwargs else value

    def list_images(self, directory: Path) -> List[Path]:
        if not directory.exists():
            return []
        return sorted(
            [path for path in directory.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS],
            key=natural_key,
        )

    def build_questions(self) -> bool:
        ai_images = self.list_images(AI_DIR)
        non_ai_images = self.list_images(NON_AI_DIR)
        if len(ai_images) < TOTAL_ROUNDS or len(non_ai_images) < TOTAL_ROUNDS:
            self.error_message = self.t("load_error")
            return False

        random.shuffle(ai_images)
        random.shuffle(non_ai_images)
        ai_images = ai_images[:TOTAL_ROUNDS]
        non_ai_images = non_ai_images[:TOTAL_ROUNDS]

        questions: List[ImageQuestion] = []
        for index, (ai_image, non_ai_image) in enumerate(zip(ai_images, non_ai_images), start=1):
            if AI_DIR not in ai_image.parents or NON_AI_DIR not in non_ai_image.parents:
                self.error_message = self.t("load_error")
                return False

            if random.choice([True, False]):
                questions.append(ImageQuestion(index, ai_image, non_ai_image, "left"))
            else:
                questions.append(ImageQuestion(index, ai_image, non_ai_image, "right"))

        self.questions = questions
        self.error_message = ""
        return True

    def start_game(self) -> None:
        if not self.build_questions():
            return
        self.state = "playing"
        self.current_index = 0
        self.score = 0
        self.wrong_records = []
        self.start_ticks = pygame.time.get_ticks()
        self.end_ticks = None
        self.feedback_text = ""
        self.feedback_is_correct = False
        self.scroll_y = 0

    def restart(self) -> None:
        self.image_cache.clear()
        self.start_game()

    def go_back(self) -> None:
        self.running = False
        if self.on_back:
            self.on_back(self.lang)

    def elapsed_seconds(self) -> float:
        if self.start_ticks is None:
            return 0.0
        end = self.end_ticks if self.end_ticks is not None else pygame.time.get_ticks()
        return (end - self.start_ticks) / 1000

    def load_scaled_image(self, path: Path, max_size: Tuple[int, int]) -> Optional[pygame.Surface]:
        cache_key = (path, max_size)
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
        try:
            image = pygame.image.load(str(path)).convert()
        except pygame.error:
            self.error_message = self.t("load_error")
            return None
        scaled = fit_image(image, max_size)
        self.image_cache[cache_key] = scaled
        return scaled

    def answer(self, selected_side: str) -> None:
        if self.state != "playing":
            return

        question = self.questions[self.current_index]
        is_correct = selected_side == question.answer
        self.feedback_is_correct = is_correct
        self.feedback_text = self.t("correct") if is_correct else self.t("wrong")
        self.feedback_start = pygame.time.get_ticks()
        self.state = "feedback"

        if is_correct:
            self.score += 1
        else:
            self.wrong_records.append(
                {
                    "round_number": question.round_number,
                    "left_image": question.left_image,
                    "right_image": question.right_image,
                    "correct_side": question.answer,
                    "selected_side": selected_side,
                }
            )

    def advance_after_feedback(self) -> None:
        if pygame.time.get_ticks() - self.feedback_start < FEEDBACK_DURATION:
            return

        if self.current_index >= TOTAL_ROUNDS - 1:
            self.end_ticks = pygame.time.get_ticks()
            self.state = "result"
            self.scroll_y = 0
        else:
            self.current_index += 1
            self.state = "playing"

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.embedded:
                    self.go_back()
                else:
                    self.running = False
            elif event.type == pygame.MOUSEWHEEL and self.state == "result":
                self.scroll_y += event.y * 42
                self.scroll_y = min(0, self.scroll_y)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event)

    def handle_click(self, event: pygame.event.Event) -> None:
        if self.embedded and pygame.Rect(self.width - 160, 18, 128, 40).collidepoint(event.pos):
            self.go_back()
            return

        if self.state == "menu":
            start_button = Button(
                pygame.Rect(self.width // 2 - 100, 425, 200, 54),
                self.t("start"),
                self.font_button,
                GREEN,
            )
            if start_button.is_clicked(event):
                self.start_game()
        elif self.state == "playing":
            left_rect, right_rect, left_button, right_button = self.choice_rects()
            if left_rect.collidepoint(event.pos) or left_button.collidepoint(event.pos):
                self.answer("left")
            elif right_rect.collidepoint(event.pos) or right_button.collidepoint(event.pos):
                self.answer("right")
        elif self.state == "result":
            restart_button = self.restart_button_rect()
            if restart_button.collidepoint(event.pos):
                self.restart()

    def draw_header(self) -> None:
        pygame.draw.rect(self.screen, WHITE, (0, 0, self.width, 76))
        pygame.draw.line(self.screen, LINE, (0, 76), (self.width, 76), 2)
        draw_text(self.screen, self.t("title"), self.font_subtitle, BLACK, (32, 22))
        if self.embedded:
            back = Button(pygame.Rect(self.width - 160, 18, 128, 40), self.t("back"), self.font_small, AMBER)
            back.draw(self.screen)

    def choice_rects(self) -> Tuple[pygame.Rect, pygame.Rect, pygame.Rect, pygame.Rect]:
        image_w = min(500, (self.width - 150) // 2)
        image_h = min(390, self.height - 250)
        y = 185
        left_x = self.width // 2 - image_w - 35
        right_x = self.width // 2 + 35
        left_rect = pygame.Rect(left_x, y, image_w, image_h)
        right_rect = pygame.Rect(right_x, y, image_w, image_h)
        left_button = pygame.Rect(left_rect.centerx - 80, left_rect.bottom + 18, 160, 46)
        right_button = pygame.Rect(right_rect.centerx - 80, right_rect.bottom + 18, 160, 46)
        return left_rect, right_rect, left_button, right_button

    def restart_button_rect(self) -> pygame.Rect:
        return pygame.Rect(self.width - 198, 18, 150, 42)

    def draw_menu(self) -> None:
        self.screen.fill(BG)
        card = pygame.Rect(self.width // 2 - 390, 150, 780, 400)
        pygame.draw.rect(self.screen, CARD, card, border_radius=8)
        pygame.draw.rect(self.screen, LINE, card, 2, border_radius=8)

        draw_center_text(self.screen, self.t("title"), self.font_title, BLACK, (card.centerx, card.y + 95))
        draw_center_text(self.screen, self.t("subtitle"), self.font_normal, INK, (card.centerx, card.y + 158))

        if self.error_message:
            draw_center_text(self.screen, self.error_message, self.font_small, RED, (card.centerx, card.y + 250))

        start_button = Button(
            pygame.Rect(self.width // 2 - 100, 425, 200, 54),
            self.t("start"),
            self.font_button,
            GREEN,
        )
        start_button.draw(self.screen)

    def draw_image_card(self, path: Path, rect: pygame.Rect, button_rect: pygame.Rect, label: str) -> None:
        pygame.draw.rect(self.screen, CARD, rect, border_radius=8)
        pygame.draw.rect(self.screen, LINE, rect, 2, border_radius=8)
        image = self.load_scaled_image(path, (rect.width - 24, rect.height - 24))
        if image:
            image_rect = image.get_rect(center=rect.center)
            self.screen.blit(image, image_rect)

        choice_button = Button(button_rect, label, self.font_button, BLUE)
        choice_button.draw(self.screen)

    def draw_playing(self) -> None:
        self.screen.fill(BG)
        self.draw_header()
        question = self.questions[self.current_index]
        elapsed = self.elapsed_seconds()

        draw_text(
            self.screen,
            self.t("round", current=self.current_index + 1, total=TOTAL_ROUNDS),
            self.font_subtitle,
            BLUE,
            (46, 100),
        )
        draw_text(self.screen, self.t("score", score=self.score), self.font_normal, INK, (46, 138))
        draw_text(self.screen, self.t("time", seconds=elapsed), self.font_normal, MUTED, (210, 138))

        left_rect, right_rect, left_button, right_button = self.choice_rects()
        self.draw_image_card(question.left_image, left_rect, left_button, self.t("left"))
        self.draw_image_card(question.right_image, right_rect, right_button, self.t("right"))

    def draw_feedback(self) -> None:
        self.draw_playing()
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((15, 23, 42, 110))
        self.screen.blit(overlay, (0, 0))

        color = GREEN if self.feedback_is_correct else RED
        box = pygame.Rect(self.width // 2 - 210, self.height // 2 - 70, 420, 140)
        pygame.draw.rect(self.screen, SOFT_GREEN if self.feedback_is_correct else SOFT_RED, box, border_radius=8)
        pygame.draw.rect(self.screen, color, box, 4, border_radius=8)
        draw_center_text(self.screen, self.feedback_text, self.font_title, color, box.center)

    def draw_result(self) -> None:
        self.screen.fill(BG)
        self.draw_header()

        restart_button = Button(self.restart_button_rect(), self.t("restart"), self.font_small, GREEN)
        restart_button.draw(self.screen)

        top_y = 105 + self.scroll_y
        draw_text(self.screen, self.t("finished"), self.font_title, BLACK, (54, top_y))
        draw_text(
            self.screen,
            self.t("correct_count", score=self.score, total=TOTAL_ROUNDS),
            self.font_subtitle,
            BLUE,
            (54, top_y + 52),
        )
        draw_text(
            self.screen,
            self.t("clear_time", seconds=self.elapsed_seconds()),
            self.font_normal,
            INK,
            (54, top_y + 91),
        )

        y = top_y + 145
        if not self.wrong_records:
            draw_text(self.screen, self.t("perfect"), self.font_subtitle, GREEN, (54, y))
            return

        draw_text(self.screen, self.t("review"), self.font_subtitle, BLACK, (54, y))
        y += 48
        for record in self.wrong_records:
            y = self.draw_wrong_record(record, y)

    def draw_wrong_record(self, record: dict, y: int) -> int:
        row = pygame.Rect(54, y, self.width - 108, 188)
        if row.bottom < 76 or row.y > self.height:
            return y + 208

        pygame.draw.rect(self.screen, CARD, row, border_radius=8)
        pygame.draw.rect(self.screen, LINE, row, 2, border_radius=8)

        draw_text(self.screen, f"第 {record['round_number']} 關", self.font_normal, BLACK, (row.x + 22, row.y + 18))
        draw_text(self.screen, self.t("answer_is_ai"), self.font_small, MUTED, (row.x + 22, row.y + 50))

        thumb_w, thumb_h = 170, 118
        left_rect = pygame.Rect(row.x + 290, row.y + 34, thumb_w, thumb_h)
        right_rect = pygame.Rect(row.x + 510, row.y + 34, thumb_w, thumb_h)
        self.draw_review_thumb(record["left_image"], left_rect, record["correct_side"] == "left", record["selected_side"] == "left")
        self.draw_review_thumb(record["right_image"], right_rect, record["correct_side"] == "right", record["selected_side"] == "right")

        draw_center_text(self.screen, self.t("left"), self.font_small, MUTED, (left_rect.centerx, left_rect.bottom + 16))
        draw_center_text(self.screen, self.t("right"), self.font_small, MUTED, (right_rect.centerx, right_rect.bottom + 16))
        return y + 208

    def draw_review_thumb(self, path: Path, rect: pygame.Rect, is_correct: bool, is_selected: bool) -> None:
        pygame.draw.rect(self.screen, WHITE, rect, border_radius=8)
        image = self.load_scaled_image(path, (rect.width - 12, rect.height - 12))
        if image:
            self.screen.blit(image, image.get_rect(center=rect.center))

        if is_selected:
            pygame.draw.rect(self.screen, RED, rect, 5, border_radius=8)
        if is_correct:
            pygame.draw.rect(self.screen, GREEN, rect.inflate(10, 10), 5, border_radius=10)
            pygame.draw.circle(self.screen, GREEN, (rect.right - 12, rect.y + 12), 12, 4)

    def draw(self) -> None:
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "playing":
            self.draw_playing()
        elif self.state == "feedback":
            self.advance_after_feedback()
            if self.state == "feedback":
                self.draw_feedback()
            else:
                self.draw()
                return
        elif self.state == "result":
            self.draw_result()

        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)

        if not self.embedded:
            pygame.quit()
            sys.exit()


# Backward-compatible name for the existing project menu.
AIGame = Game


if __name__ == "__main__":
    Game().run()
