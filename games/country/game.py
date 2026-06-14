from __future__ import annotations

import sys
import time
from typing import Dict, Tuple

import pygame

from ui_shared import (
    AMBER,
    BG,
    BLACK,
    BLUE,
    CARD,
    CYAN,
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
    SOFT_GREEN,
    VIOLET,
    WHITE,
    button,
    draw_text,
    draw_wrapped,
    make_fonts,
    tr,
)
from games.country.config import COUNTRIES, INTRO_TEXT, SCORING, Country, score_from_table

TEXT = {
    "zh": {
        "title": "記憶體的跨國製程：跟著晶片環遊世界",
        "phase1": "任務一：依照提示回答國家",
        "phase2": "任務二：在地圖上找出國家位置",
        "overview": "關卡說明",
        "scoring": "計分方式",
        "score_phase1": "任務一：依照看提示數量給分",
        "score_phase2": "任務二：依照答對國家給分",
        "start": "開始任務",
        "hint": "提示",
        "next_hint": "看下一個提示",
        "select": "選擇答案",
        "next": "下一題",
        "to_map": "前往地圖任務",
        "place": "點選地圖位置",
        "finish": "完成任務",
        "restart": "再玩一次",
        "menu": "回主選單",
        "back": "回主畫面",
        "correct": "答對了！",
        "wrong": "再想想，必要時可以多看一個提示。",
        "score": "分數",
        "time": "時間",
        "question": "題目",
        "map_help": "先選左側國家標籤，再點地圖上對應位置。",
        "complete_title": "任務完成！",
        "complete_text": "你已經完成晶片從研發、製造到封裝測試的全球路線。",
    },
    "ja": {
        "title": "メモリの国際製造：チップの世界一周",
        "phase1": "ミッション1：ヒントから国を答える",
        "phase2": "ミッション2：地図上で国の場所を見つける",
        "overview": "ステージ説明",
        "scoring": "得点方法",
        "score_phase1": "ミッション1：見たヒント数で得点",
        "score_phase2": "ミッション2：正解した国の数で得点",
        "start": "ミッション開始",
        "hint": "ヒント",
        "next_hint": "次のヒントを見る",
        "select": "答えを選ぶ",
        "next": "次の問題",
        "to_map": "地図ミッションへ",
        "place": "地図の位置をクリック",
        "finish": "完了",
        "restart": "もう一度",
        "menu": "メニューへ",
        "back": "メニューへ",
        "correct": "正解です！",
        "wrong": "もう一度考えてみましょう。必要ならヒントを見てください。",
        "score": "得点",
        "time": "時間",
        "question": "問題",
        "map_help": "左の国ラベルを選び、地図上の正しい場所をクリックします。",
        "complete_title": "ミッション完了！",
        "complete_text": "研究開発、製造、パッケージング・テストまで、チップの世界ルートを完成しました。",
    },
}


COLOR_BY_NAME = {
    "blue": BLUE,
    "green": GREEN,
    "cyan": CYAN,
    "amber": AMBER,
    "violet": VIOLET,
    "red": RED,
    "slate": SLATE,
}


def country_color(country) -> Tuple[int, int, int]:
    return COLOR_BY_NAME.get(country.color_name, SLATE)


class CountryGame:
    def __init__(self, screen=None, embedded: bool = False, initial_lang: str = "zh", on_back=None) -> None:
        self.embedded = embedded
        self.on_back = on_back
        pygame.init()
        self.screen = screen or pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Chip World Tour")
        self.clock = pygame.time.Clock()
        self.fonts = make_fonts()
        self.lang = initial_lang if initial_lang in ("zh", "ja") else "zh"
        self.running = True
        self.phase = "intro"
        self.index = 0
        self.hints_seen = 0
        self.hints_used = 0
        self.quiz_done: Dict[str, bool] = {}
        self.placed: Dict[str, Tuple[int, int]] = {}
        self.selected_country = COUNTRIES[0].key
        self.message = ""
        self.message_color = MUTED
        self.start_time = time.time()
        self.cooldown = 0
        self.click_pos = None

    def go_back(self) -> None:
        self.running = False
        if self.on_back:
            self.on_back(self.lang)

    def elapsed(self) -> str:
        seconds = int(time.time() - self.start_time)
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def score(self) -> int:
        return score_from_table("phase1", min(self.hints_used, 7)) + score_from_table("phase2", self.map_correct_count())

    def current(self) -> Country:
        return COUNTRIES[self.index]

    def handle_events(self) -> None:
        self.click_pos = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.click_pos = event.pos
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.go_back()
                elif event.key == pygame.K_TAB:
                    self.lang = "ja" if self.lang == "zh" else "zh"

    def draw_header(self) -> None:
        pygame.draw.rect(self.screen, WHITE, (0, 0, SCREEN_WIDTH, 88))
        pygame.draw.line(self.screen, LINE, (0, 88), (SCREEN_WIDTH, 88), 2)
        draw_text(self.screen, TEXT[self.lang]["title"], self.fonts["subtitle"], BLACK, (34, 20))
        if self.phase == "intro":
            phase = TEXT[self.lang]["overview"]
        elif self.phase == "quiz":
            phase = TEXT[self.lang]["phase1"]
        elif self.phase == "map":
            phase = TEXT[self.lang]["phase2"]
        else:
            phase = TEXT[self.lang]["complete_title"]
        draw_text(self.screen, phase, self.fonts["normal"], MUTED, (36, 54))
        back_rect = pygame.Rect(760, 18, 122, 34)
        button(self.screen, back_rect, TEXT[self.lang]["back"], self.fonts["small"], AMBER, WHITE)
        if self.click_pos and back_rect.collidepoint(self.click_pos) and self.cooldown <= 0:
            self.cooldown = 12
            self.go_back()

        score_text = "--" if self.phase == "intro" else str(self.score())
        draw_text(self.screen, f"{TEXT[self.lang]['score']} {score_text}", self.fonts["normal"], GREEN, (910, 24))
        draw_text(self.screen, f"{TEXT[self.lang]['time']} {self.elapsed()}", self.fonts["normal"], MUTED, (1010, 24))

        for idx, (code, label) in enumerate([("zh", "中"), ("ja", "日")]):
            rect = pygame.Rect(1040 + idx * 48, 52, 38, 28)
            selected = self.lang == code
            button(self.screen, rect, label, self.fonts["small"], BLUE if selected else WHITE, WHITE if selected else INK, LINE)
            if self.click_pos and rect.collidepoint(self.click_pos) and self.cooldown <= 0:
                self.lang = code
                self.cooldown = 12

    def draw_scoring_table(self, title: str, rows: list, rect: pygame.Rect) -> None:
        draw_text(self.screen, title, self.fonts["normal"], BLACK, (rect.x, rect.y))
        table = pygame.Rect(rect.x, rect.y + 42, rect.width, 220)
        row_h = table.height // len(rows)
        split_x = table.x + int(table.width * 0.62)
        pygame.draw.rect(self.screen, WHITE, table)
        pygame.draw.rect(self.screen, BLACK, table, 2)
        pygame.draw.line(self.screen, BLACK, (split_x, table.y), (split_x, table.bottom), 2)
        for idx, row in enumerate(rows):
            y = table.y + idx * row_h
            if idx > 0:
                pygame.draw.line(self.screen, BLACK, (table.x, y), (table.right, y), 2)
            if idx % 2 == 0:
                pygame.draw.rect(self.screen, (235, 235, 235), (table.x + 2, y + 2, split_x - table.x - 3, row_h - 3))
            draw_text(self.screen, tr(row["label"], self.lang), self.fonts["normal"], BLACK, (table.x + 16, y + 12))
            draw_text(self.screen, f"+{row['points']}", self.fonts["normal"], BLACK, (split_x + 28, y + 12))

    def draw_intro(self) -> None:
        card = pygame.Rect(80, 125, 1040, 600)
        pygame.draw.rect(self.screen, CARD, card, border_radius=8)
        pygame.draw.rect(self.screen, LINE, card, 2, border_radius=8)
        draw_text(self.screen, TEXT[self.lang]["overview"], self.fonts["title"], BLACK, (card.x + 36, card.y + 30))

        y = card.y + 88
        for line in INTRO_TEXT[self.lang]:
            y = draw_wrapped(
                self.screen,
                line,
                self.fonts["normal"],
                INK,
                pygame.Rect(card.x + 44, y, card.width - 88, 54),
                5,
            ) + 8

        draw_text(self.screen, TEXT[self.lang]["scoring"], self.fonts["title"], BLACK, (card.x + 36, card.y + 255))
        self.draw_scoring_table(
            TEXT[self.lang]["score_phase1"],
            SCORING["phase1"],
            pygame.Rect(card.x + 90, card.y + 315, 310, 270),
        )
        self.draw_scoring_table(
            TEXT[self.lang]["score_phase2"],
            SCORING["phase2"],
            pygame.Rect(card.x + 610, card.y + 315, 310, 270),
        )

        start_rect = pygame.Rect(card.right - 222, card.y + 36, 170, 46)
        button(self.screen, start_rect, TEXT[self.lang]["start"], self.fonts["button"], GREEN)
        if self.click_pos and start_rect.collidepoint(self.click_pos) and self.cooldown <= 0:
            self.phase = "quiz"
            self.start_time = time.time()
            self.cooldown = 12

    def draw_quiz(self) -> None:
        country = self.current()
        panel = pygame.Rect(44, 122, 520, 610)
        pygame.draw.rect(self.screen, CARD, panel, border_radius=8)
        pygame.draw.rect(self.screen, LINE, panel, 2, border_radius=8)
        draw_text(self.screen, f"{TEXT[self.lang]['question']} {self.index + 1}/7", self.fonts["subtitle"], INK, (panel.x + 28, panel.y + 26))
        draw_text(self.screen, tr(country.role, self.lang), self.fonts["normal"], country_color(country), (panel.x + 28, panel.y + 68))

        y = panel.y + 116
        if self.hints_seen == 0:
            empty_rect = pygame.Rect(panel.x + 28, y, panel.width - 56, 92)
            pygame.draw.rect(self.screen, SOFT_BLUE, empty_rect, border_radius=8)
            draw_wrapped(
                self.screen,
                tr({"zh": "請先依照題目推理；需要協助時再看提示。", "ja": "まず問題から推理し、必要なときにヒントを見てください。"}, self.lang),
                self.fonts["normal"],
                INK,
                pygame.Rect(empty_rect.x + 18, empty_rect.y + 24, empty_rect.width - 36, 48),
                4,
            )
            y += 110

        for idx, hint in enumerate(country.hints[: self.hints_seen]):
            hint_rect = pygame.Rect(panel.x + 28, y, panel.width - 56, 108)
            pygame.draw.rect(self.screen, SOFT_BLUE if idx == 0 else SOFT_AMBER, hint_rect, border_radius=8)
            draw_text(self.screen, f"{TEXT[self.lang]['hint']} {idx + 1}", self.fonts["small"], MUTED, (hint_rect.x + 18, hint_rect.y + 12))
            draw_wrapped(self.screen, tr(hint, self.lang), self.fonts["normal"], INK, pygame.Rect(hint_rect.x + 18, hint_rect.y + 40, hint_rect.width - 36, 58), 4)
            y += 126

        hint_btn = pygame.Rect(panel.x + 28, panel.bottom - 82, 190, 44)
        button(self.screen, hint_btn, TEXT[self.lang]["next_hint"], self.fonts["button"], AMBER if self.hints_seen < len(country.hints) else LINE)
        if self.click_pos and hint_btn.collidepoint(self.click_pos) and self.hints_seen < len(country.hints) and self.cooldown <= 0:
            self.hints_seen += 1
            self.hints_used += 1
            self.cooldown = 12

        answer_panel = pygame.Rect(604, 122, 552, 610)
        pygame.draw.rect(self.screen, CARD, answer_panel, border_radius=8)
        pygame.draw.rect(self.screen, LINE, answer_panel, 2, border_radius=8)
        draw_text(self.screen, TEXT[self.lang]["select"], self.fonts["subtitle"], INK, (answer_panel.x + 28, answer_panel.y + 26))

        mouse = pygame.mouse.get_pos()
        click = self.click_pos
        for idx, item in enumerate(COUNTRIES):
            x = answer_panel.x + 28 + (idx % 2) * 252
            y = answer_panel.y + 82 + (idx // 2) * 80
            rect = pygame.Rect(x, y, 220, 56)
            pygame.draw.rect(self.screen, SOFT_GREEN, rect, border_radius=8)
            pygame.draw.rect(self.screen, country_color(item) if rect.collidepoint(mouse) else LINE, rect, 2, border_radius=8)
            draw_text(self.screen, tr(item.name, self.lang), self.fonts["button"], INK, (rect.x + 16, rect.y + 15))
            if click and rect.collidepoint(click) and self.cooldown <= 0:
                self.cooldown = 16
                if item.key == country.key:
                    self.quiz_done[country.key] = True
                    self.message = TEXT[self.lang]["correct"]
                    self.message_color = GREEN
                else:
                    self.message = TEXT[self.lang]["wrong"]
                    self.message_color = RED

        if self.message:
            draw_text(self.screen, self.message, self.fonts["normal"], self.message_color, (answer_panel.x + 28, answer_panel.bottom - 122))

        if country.key in self.quiz_done:
            label = TEXT[self.lang]["to_map"] if self.index == len(COUNTRIES) - 1 else TEXT[self.lang]["next"]
            next_rect = pygame.Rect(answer_panel.right - 210, answer_panel.bottom - 74, 170, 46)
            button(self.screen, next_rect, label, self.fonts["button"], GREEN)
            if click and next_rect.collidepoint(click) and self.cooldown <= 0:
                self.cooldown = 16
                self.message = ""
                if self.index < len(COUNTRIES) - 1:
                    self.index += 1
                    self.hints_seen = 0
                else:
                    self.phase = "map"

    def draw_world_map(self, rect: pygame.Rect) -> None:
        pygame.draw.rect(self.screen, (226, 242, 255), rect, border_radius=8)
        pygame.draw.rect(self.screen, LINE, rect, 2, border_radius=8)
        land = (187, 247, 208)
        shapes = [
            pygame.Rect(rect.x + 120, rect.y + 120, 160, 145),
            pygame.Rect(rect.x + 255, rect.y + 250, 110, 160),
            pygame.Rect(rect.x + 450, rect.y + 130, 150, 175),
            pygame.Rect(rect.x + 600, rect.y + 135, 260, 210),
            pygame.Rect(rect.x + 665, rect.y + 330, 150, 95),
        ]
        for shape in shapes:
            pygame.draw.ellipse(self.screen, land, shape)
        for country in COUNTRIES:
            x, y = country.pos
            pygame.draw.circle(self.screen, country_color(country), (x, y), 10)
            pygame.draw.circle(self.screen, WHITE, (x, y), 10, 2)
            label = tr(country.name, self.lang)
            draw_text(self.screen, label, self.fonts["tiny"], INK, (x + 12, y - 8))

    def map_correct_count(self) -> int:
        count = 0
        country_by_key = {country.key: country for country in COUNTRIES}
        for key, pos in self.placed.items():
            target = country_by_key[key].pos
            if (pos[0] - target[0]) ** 2 + (pos[1] - target[1]) ** 2 <= 35**2:
                count += 1
        return count

    def draw_map_phase(self) -> None:
        left = pygame.Rect(42, 124, 270, 608)
        pygame.draw.rect(self.screen, CARD, left, border_radius=8)
        pygame.draw.rect(self.screen, LINE, left, 2, border_radius=8)
        draw_text(self.screen, TEXT[self.lang]["place"], self.fonts["subtitle"], INK, (left.x + 22, left.y + 22))
        draw_wrapped(self.screen, TEXT[self.lang]["map_help"], self.fonts["small"], MUTED, pygame.Rect(left.x + 22, left.y + 62, 226, 62), 4)

        mouse = pygame.mouse.get_pos()
        click = self.click_pos
        for idx, country in enumerate(COUNTRIES):
            rect = pygame.Rect(left.x + 22, left.y + 142 + idx * 58, 226, 44)
            selected = self.selected_country == country.key
            color = country_color(country)
            bg = color if selected else WHITE
            button(self.screen, rect, tr(country.name, self.lang), self.fonts["button"], bg, WHITE if selected else INK, color)
            if click and rect.collidepoint(click) and self.cooldown <= 0:
                self.selected_country = country.key
                self.cooldown = 10

        map_rect = pygame.Rect(342, 124, 814, 508)
        self.draw_world_map(map_rect)
        if click and map_rect.collidepoint(click) and self.cooldown <= 0:
            self.placed[self.selected_country] = click
            self.cooldown = 10

        for key, pos in self.placed.items():
            country = next(item for item in COUNTRIES if item.key == key)
            pygame.draw.circle(self.screen, country_color(country), pos, 16)
            pygame.draw.circle(self.screen, WHITE, pos, 16, 3)
            draw_text(self.screen, tr(country.name, self.lang), self.fonts["tiny"], INK, (pos[0] + 18, pos[1] - 8))

        result_rect = pygame.Rect(342, 650, 814, 82)
        pygame.draw.rect(self.screen, CARD, result_rect, border_radius=8)
        pygame.draw.rect(self.screen, LINE, result_rect, 2, border_radius=8)
        draw_text(self.screen, f"{TEXT[self.lang]['score']} {self.score()} / 10", self.fonts["subtitle"], GREEN, (result_rect.x + 24, result_rect.y + 24))
        draw_text(self.screen, f"{self.map_correct_count()} / 7", self.fonts["subtitle"], BLUE, (result_rect.x + 210, result_rect.y + 24))
        finish_rect = pygame.Rect(result_rect.right - 168, result_rect.y + 18, 132, 46)
        button(self.screen, finish_rect, TEXT[self.lang]["finish"], self.fonts["button"], GREEN if len(self.placed) == len(COUNTRIES) else LINE)
        if click and finish_rect.collidepoint(click) and len(self.placed) == len(COUNTRIES) and self.cooldown <= 0:
            self.phase = "done"
            self.cooldown = 16

    def draw_done(self) -> None:
        card = pygame.Rect(300, 190, 600, 380)
        pygame.draw.rect(self.screen, CARD, card, border_radius=8)
        pygame.draw.rect(self.screen, GREEN, card, 3, border_radius=8)
        draw_text(self.screen, TEXT[self.lang]["complete_title"], self.fonts["title"], GREEN, (card.x + 42, card.y + 46))
        draw_wrapped(self.screen, TEXT[self.lang]["complete_text"], self.fonts["normal"], INK, pygame.Rect(card.x + 42, card.y + 106, card.width - 84, 80), 6)
        draw_text(self.screen, f"{TEXT[self.lang]['score']} {self.score()} / 10", self.fonts["subtitle"], BLUE, (card.x + 42, card.y + 210))
        draw_text(self.screen, f"{TEXT[self.lang]['time']} {self.elapsed()}", self.fonts["subtitle"], MUTED, (card.x + 42, card.y + 250))
        restart = pygame.Rect(card.x + 42, card.bottom - 76, 150, 46)
        menu = pygame.Rect(card.right - 192, card.bottom - 76, 150, 46)
        button(self.screen, restart, TEXT[self.lang]["restart"], self.fonts["button"], GREEN)
        button(self.screen, menu, TEXT[self.lang]["menu"], self.fonts["button"], BLUE)
        click = self.click_pos
        if click and restart.collidepoint(click) and self.cooldown <= 0:
            self.__init__(
                screen=self.screen,
                embedded=self.embedded,
                initial_lang=self.lang,
                on_back=self.on_back,
            )
        if click and menu.collidepoint(click) and self.cooldown <= 0:
            self.go_back()

    def draw(self) -> None:
        self.screen.fill(BG)
        self.draw_header()
        if self.phase == "intro":
            self.draw_intro()
        elif self.phase == "quiz":
            self.draw_quiz()
        elif self.phase == "map":
            self.draw_map_phase()
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
    CountryGame().run()
