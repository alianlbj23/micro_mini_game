from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import Dict, List

import pygame

from ui_shared import (
    AMBER,
    BG,
    BLACK,
    BLUE,
    CARD,
    GREEN,
    INK,
    LINE,
    MUTED,
    RED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SLATE,
    SOFT_AMBER,
    SOFT_BLUE,
    WHITE,
    button,
    draw_text,
    draw_wrapped,
    make_fonts,
)


TEXT: Dict[str, Dict[str, str]] = {
    "zh": {
        "title": "AI 圖片偵探",
        "subtitle": "從左右兩張圖片中，選出 AI 生成照片。",
        "start": "開始挑戰",
        "back": "回主畫面",
        "round": "關卡",
        "score": "分數",
        "instruction": "點選你認為是 AI 生成照片的那一張。",
        "left": "左圖",
        "right": "右圖",
        "correct": "答對了！這張是 AI 生成照片。",
        "wrong": "答錯了，另一張才是 AI 生成照片。",
        "next": "下一關",
        "finish": "完成",
        "done": "挑戰完成！",
        "done_text": "你已完成 10 組 AI / 真實照片判斷。",
        "correct_count": "答對題數",
        "restart": "再玩一次",
        "loading_error": "圖片數量不足或讀取失敗，請確認 AI 與 non_AI 資料夾各有 10 張圖片。",
        "rules_1": "每一關會同時出現 2 張圖片。",
        "rules_2": "其中 1 張來自 AI 資料夾，另 1 張來自 non_AI 資料夾。",
        "rules_3": "每張圖片只會使用一次，總共 10 關。",
    },
    "ja": {
        "title": "AI 画像探偵",
        "subtitle": "左右2枚の画像から、AI生成画像を選びます。",
        "start": "チャレンジ開始",
        "back": "メニューへ",
        "round": "ステージ",
        "score": "得点",
        "instruction": "AI生成画像だと思うほうをクリックしてください。",
        "left": "左の画像",
        "right": "右の画像",
        "correct": "正解です！これはAI生成画像です。",
        "wrong": "不正解です。もう一方がAI生成画像です。",
        "next": "次のステージ",
        "finish": "完了",
        "done": "チャレンジ完了！",
        "done_text": "10組のAI画像と実写画像の判定を完了しました。",
        "correct_count": "正解数",
        "restart": "もう一度",
        "loading_error": "画像数が足りない、または読み込みに失敗しました。AI と non_AI に各10枚あるか確認してください。",
        "rules_1": "各ステージでは2枚の画像が同時に表示されます。",
        "rules_2": "1枚は AI フォルダ、もう1枚は non_AI フォルダから選ばれます。",
        "rules_3": "各画像は1回だけ使われ、全部で10ステージです。",
    },
}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
TOTAL_ROUNDS = 10
POINTS_PER_CORRECT = 100


def natural_key(path: Path) -> tuple:
    stem = path.stem
    return (0, int(stem)) if stem.isdigit() else (1, stem.lower())


def fit_image(surface: pygame.Surface, size: tuple[int, int]) -> pygame.Surface:
    target_w, target_h = size
    src_w, src_h = surface.get_size()
    scale = min(target_w / src_w, target_h / src_h)
    new_size = (max(1, int(src_w * scale)), max(1, int(src_h * scale)))
    return pygame.transform.smoothscale(surface, new_size)


class AIGame:
    def __init__(self, screen=None, embedded: bool = False, initial_lang: str = "zh", on_back=None) -> None:
        self.embedded = embedded
        self.on_back = on_back
        pygame.init()
        self.screen = screen or pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("AI Image Detective")
        self.clock = pygame.time.Clock()
        self.fonts = make_fonts()
        self.lang = initial_lang if initial_lang in TEXT else "zh"
        self.running = True
        self.phase = "start"
        self.round_index = 0
        self.score = 0
        self.correct_count = 0
        self.cooldown = 0
        self.click_pos = None
        self.rounds: List[dict] = []
        self.current_result: bool | None = None
        self.load_error: str | None = None
        self.image_cache: dict[Path, pygame.Surface] = {}
        self.prepare_rounds()

    def t(self, key: str) -> str:
        return TEXT.get(self.lang, TEXT["zh"]).get(key, TEXT["zh"][key])

    def image_dirs(self) -> tuple[Path, Path]:
        root = Path(__file__).resolve().parent / "pic"
        return root / "AI", root / "non_AI"

    def list_images(self, directory: Path) -> List[Path]:
        if not directory.exists():
            return []
        return sorted(
            [path for path in directory.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS],
            key=natural_key,
        )

    def prepare_rounds(self) -> None:
        ai_dir, non_ai_dir = self.image_dirs()
        ai_images = self.list_images(ai_dir)
        non_ai_images = self.list_images(non_ai_dir)
        if len(ai_images) < TOTAL_ROUNDS or len(non_ai_images) < TOTAL_ROUNDS:
            self.load_error = self.t("loading_error")
            return

        ai_pool = ai_images[:TOTAL_ROUNDS]
        non_ai_pool = non_ai_images[:TOTAL_ROUNDS]
        random.shuffle(ai_pool)
        random.shuffle(non_ai_pool)
        self.rounds = []
        for ai_path, non_ai_path in zip(ai_pool, non_ai_pool):
            ai_side = random.choice(["left", "right"])
            self.rounds.append(
                {
                    "ai_path": ai_path,
                    "non_ai_path": non_ai_path,
                    "left_path": ai_path if ai_side == "left" else non_ai_path,
                    "right_path": non_ai_path if ai_side == "left" else ai_path,
                    "ai_side": ai_side,
                }
            )

    def reset(self) -> None:
        lang = self.lang
        screen = self.screen
        embedded = self.embedded
        on_back = self.on_back
        self.__init__(screen=screen, embedded=embedded, initial_lang=lang, on_back=on_back)
        self.cooldown = 12

    def go_back(self) -> None:
        self.running = False
        if self.on_back:
            self.on_back(self.lang)

    def handle_events(self) -> None:
        self.click_pos = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.click_pos = event.pos
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.go_back()

    def load_image(self, path: Path, max_size: tuple[int, int]) -> pygame.Surface | None:
        cache_key = (path, max_size)
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
        try:
            image = pygame.image.load(str(path)).convert()
        except pygame.error:
            self.load_error = self.t("loading_error")
            return None
        image = fit_image(image, max_size)
        self.image_cache[cache_key] = image
        return image

    def draw_header(self) -> None:
        pygame.draw.rect(self.screen, WHITE, (0, 0, SCREEN_WIDTH, 88))
        pygame.draw.line(self.screen, LINE, (0, 88), (SCREEN_WIDTH, 88), 2)
        draw_text(self.screen, self.t("title"), self.fonts["title"], BLACK, (34, 18))
        draw_text(self.screen, self.t("subtitle"), self.fonts["normal"], MUTED, (36, 56))
        draw_text(self.screen, f"{self.t('score')} {self.score}", self.fonts["normal"], GREEN, (930, 24))

        back_rect = pygame.Rect(760, 22, 136, 38)
        button(self.screen, back_rect, self.t("back"), self.fonts["small"], AMBER, WHITE)
        if self.click_pos and back_rect.collidepoint(self.click_pos) and self.cooldown <= 0:
            self.cooldown = 12
            self.go_back()

    def draw_start(self) -> None:
        card = pygame.Rect(170, 155, 860, 455)
        pygame.draw.rect(self.screen, CARD, card, border_radius=8)
        pygame.draw.rect(self.screen, LINE, card, 2, border_radius=8)
        draw_text(self.screen, self.t("title"), self.fonts["title"], BLACK, (card.x + 48, card.y + 48))
        draw_wrapped(self.screen, self.t("rules_1"), self.fonts["normal"], INK, pygame.Rect(card.x + 52, card.y + 122, card.width - 104, 42), 5)
        draw_wrapped(self.screen, self.t("rules_2"), self.fonts["normal"], INK, pygame.Rect(card.x + 52, card.y + 172, card.width - 104, 50), 5)
        draw_wrapped(self.screen, self.t("rules_3"), self.fonts["normal"], INK, pygame.Rect(card.x + 52, card.y + 232, card.width - 104, 50), 5)
        draw_text(self.screen, f"{TOTAL_ROUNDS} rounds / {POINTS_PER_CORRECT} points", self.fonts["normal"], MUTED, (card.x + 52, card.y + 302))

        if self.load_error:
            draw_wrapped(self.screen, self.load_error, self.fonts["normal"], RED, pygame.Rect(card.x + 52, card.y + 346, card.width - 104, 60), 5)
            return

        start_rect = pygame.Rect(card.centerx - 95, card.y + 342, 190, 54)
        button(self.screen, start_rect, self.t("start"), self.fonts["button"], GREEN)
        if self.click_pos and start_rect.collidepoint(self.click_pos) and self.cooldown <= 0:
            self.phase = "question"
            self.cooldown = 12

    def draw_image_choice(self, label: str, path: Path, rect: pygame.Rect, side: str) -> None:
        mouse = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse)
        pygame.draw.rect(self.screen, SOFT_BLUE if hovered else CARD, rect, border_radius=8)
        pygame.draw.rect(self.screen, BLUE if hovered else LINE, rect, 3 if hovered else 2, border_radius=8)

        label_rect = pygame.Rect(rect.x + 18, rect.y + 16, 108, 32)
        pygame.draw.rect(self.screen, WHITE, label_rect, border_radius=8)
        pygame.draw.rect(self.screen, LINE, label_rect, 1, border_radius=8)
        draw_text(self.screen, label, self.fonts["small"], SLATE, (label_rect.x + 15, label_rect.y + 6))

        image_area = pygame.Rect(rect.x + 22, rect.y + 62, rect.width - 44, rect.height - 88)
        image = self.load_image(path, (image_area.width, image_area.height))
        if image is None:
            return
        image_rect = image.get_rect(center=image_area.center)
        self.screen.blit(image, image_rect)

        if self.click_pos and rect.collidepoint(self.click_pos) and self.cooldown <= 0:
            self.answer(side)
            self.cooldown = 12

    def current_round(self) -> dict:
        return self.rounds[self.round_index]

    def answer(self, side: str) -> None:
        is_correct = side == self.current_round()["ai_side"]
        self.current_result = is_correct
        if is_correct:
            self.correct_count += 1
            self.score += POINTS_PER_CORRECT
        self.phase = "result"

    def draw_question(self) -> None:
        current = self.current_round()
        draw_text(
            self.screen,
            f"{self.t('round')} {self.round_index + 1:02d} / {len(self.rounds):02d}",
            self.fonts["subtitle"],
            BLUE,
            (54, 116),
        )
        draw_text(self.screen, self.t("instruction"), self.fonts["normal"], INK, (54, 150))

        left_rect = pygame.Rect(60, 205, 510, 455)
        right_rect = pygame.Rect(630, 205, 510, 455)
        self.draw_image_choice(self.t("left"), current["left_path"], left_rect, "left")
        self.draw_image_choice(self.t("right"), current["right_path"], right_rect, "right")

    def draw_result(self) -> None:
        card = pygame.Rect(230, 185, 740, 400)
        pygame.draw.rect(self.screen, CARD, card, border_radius=8)
        pygame.draw.rect(self.screen, GREEN if self.current_result else RED, card, 3, border_radius=8)

        message = self.t("correct") if self.current_result else self.t("wrong")
        draw_wrapped(
            self.screen,
            message,
            self.fonts["title"],
            GREEN if self.current_result else RED,
            pygame.Rect(card.x + 46, card.y + 56, card.width - 92, 90),
            6,
        )
        draw_text(self.screen, f"{self.t('score')} {self.score}", self.fonts["subtitle"], BLUE, (card.x + 46, card.y + 170))

        is_last = self.round_index == len(self.rounds) - 1
        next_label = self.t("finish") if is_last else self.t("next")
        next_rect = pygame.Rect(card.right - 216, card.bottom - 86, 170, 50)
        button(self.screen, next_rect, next_label, self.fonts["button"], GREEN)
        if self.click_pos and next_rect.collidepoint(self.click_pos) and self.cooldown <= 0:
            if is_last:
                self.phase = "done"
            else:
                self.round_index += 1
                self.current_result = None
                self.phase = "question"
            self.cooldown = 12

    def draw_done(self) -> None:
        card = pygame.Rect(260, 190, 680, 400)
        pygame.draw.rect(self.screen, CARD, card, border_radius=8)
        pygame.draw.rect(self.screen, GREEN, card, 3, border_radius=8)
        draw_text(self.screen, self.t("done"), self.fonts["title"], GREEN, (card.x + 48, card.y + 54))
        draw_wrapped(self.screen, self.t("done_text"), self.fonts["normal"], INK, pygame.Rect(card.x + 48, card.y + 118, card.width - 96, 60), 5)
        draw_text(self.screen, f"{self.t('score')} {self.score}", self.fonts["subtitle"], BLUE, (card.x + 48, card.y + 204))
        draw_text(self.screen, f"{self.t('correct_count')} {self.correct_count} / {len(self.rounds)}", self.fonts["subtitle"], BLACK, (card.x + 48, card.y + 254))

        restart = pygame.Rect(card.x + 48, card.bottom - 82, 150, 48)
        menu = pygame.Rect(card.right - 198, card.bottom - 82, 150, 48)
        button(self.screen, restart, self.t("restart"), self.fonts["button"], GREEN)
        button(self.screen, menu, self.t("back"), self.fonts["button"], BLUE)
        if self.click_pos and restart.collidepoint(self.click_pos) and self.cooldown <= 0:
            self.reset()
        if self.click_pos and menu.collidepoint(self.click_pos) and self.cooldown <= 0:
            self.go_back()

    def draw(self) -> None:
        self.screen.fill(BG)
        self.draw_header()
        if self.phase == "start":
            self.draw_start()
        elif self.phase == "question":
            self.draw_question()
        elif self.phase == "result":
            self.draw_result()
        else:
            self.draw_done()
        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.draw()
            self.cooldown -= 1
            self.clock.tick(60)
        if not self.embedded:
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    AIGame().run()
