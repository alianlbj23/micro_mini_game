from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple

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


TEXT = {
    "zh": {
        "title": "記憶體的跨國製程：跟著晶片環遊世界",
        "phase1": "任務一：依照提示回答國家",
        "phase2": "任務二：在地圖上找出國家位置",
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


@dataclass
class Country:
    key: str
    name: Dict[str, str]
    role: Dict[str, str]
    hints: List[Dict[str, str]]
    pos: Tuple[int, int]
    color: Tuple[int, int, int]


COUNTRIES = [
    Country(
        "us",
        {"zh": "美國", "ja": "アメリカ"},
        {"zh": "總部與研發", "ja": "本社・研究開発"},
        [
            {"zh": "這裡有頂尖大學與科學家，適合發明最新記憶體技術。", "ja": "トップクラスの大学と科学者が集まり、最新技術の研究開発に強い国です。"},
            {"zh": "地圖上位於北美洲，國旗有星星與條紋。", "ja": "北アメリカにあり、星条旗で知られています。"},
        ],
        (260, 330),
        BLUE,
    ),
    Country(
        "tw",
        {"zh": "台灣", "ja": "台湾"},
        {"zh": "精密晶圓製造", "ja": "精密ウェハー製造"},
        [
            {"zh": "具備高效率且精密的半導體製造能力。", "ja": "非常に精密で効率的な半導体製造能力を持っています。"},
            {"zh": "位於東亞的島嶼，靠近日本與中國。", "ja": "東アジアの島で、日本と中国の近くにあります。"},
        ],
        (830, 395),
        GREEN,
    ),
    Country(
        "jp",
        {"zh": "日本", "ja": "日本"},
        {"zh": "核心晶片生產", "ja": "中核チップ生産"},
        [
            {"zh": "以精密製造、材料與品質控管聞名。", "ja": "精密製造、材料、品質管理で知られています。"},
            {"zh": "位於東亞，是由多個島嶼組成的國家。", "ja": "東アジアにある島国です。"},
        ],
        (875, 330),
        CYAN,
    ),
    Country(
        "sg",
        {"zh": "新加坡", "ja": "シンガポール"},
        {"zh": "國際運輸樞紐", "ja": "国際輸送ハブ"},
        [
            {"zh": "擁有絕佳國際運輸樞紐優勢。", "ja": "国際的な輸送ハブとして大きな強みがあります。"},
            {"zh": "位於東南亞，面積小但港口非常繁忙。", "ja": "東南アジアにあり、小さい国ですが港がとても発達しています。"},
        ],
        (800, 505),
        AMBER,
    ),
    Country(
        "my",
        {"zh": "馬來西亞", "ja": "マレーシア"},
        {"zh": "封裝測試技術", "ja": "パッケージング・テスト"},
        [
            {"zh": "擁有豐富的封裝測試與製造支援技術。", "ja": "パッケージング・テストや製造支援技術が豊富です。"},
            {"zh": "位於東南亞，鄰近新加坡。", "ja": "東南アジアにあり、シンガポールの近くです。"},
        ],
        (780, 520),
        VIOLET,
    ),
    Country(
        "cn",
        {"zh": "中國", "ja": "中国"},
        {"zh": "封裝技術與龐大市場", "ja": "パッケージング技術と巨大市場"},
        [
            {"zh": "具備龐大市場，也有封裝與生產支援能力。", "ja": "巨大な市場と、パッケージング・生産支援能力があります。"},
            {"zh": "位於東亞，是亞洲面積很大的國家。", "ja": "東アジアにあり、アジアでも非常に大きな国です。"},
        ],
        (800, 350),
        RED,
    ),
    Country(
        "in",
        {"zh": "印度", "ja": "インド"},
        {"zh": "工程人才與技術支援", "ja": "エンジニア人材・技術支援"},
        [
            {"zh": "有大量工程人才，可支援跨國科技製程。", "ja": "多くのエンジニア人材がいて、グローバルな技術工程を支えます。"},
            {"zh": "位於南亞，形狀像伸向印度洋的三角形。", "ja": "南アジアにあり、インド洋へ伸びる三角形のような地形です。"},
        ],
        (710, 430),
        SLATE,
    ),
]


def phase1_points(max_hints_seen: int) -> int:
    if max_hints_seen <= 1:
        return 5
    if max_hints_seen == 2:
        return 4
    return 3


def phase2_points(correct_count: int) -> int:
    if correct_count >= 6:
        return 5
    if correct_count >= 4:
        return 4
    if correct_count >= 2:
        return 3
    if correct_count == 1:
        return 2
    return 1


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
        self.phase = "quiz"
        self.index = 0
        self.hints_seen = 1
        self.max_hints_seen = 1
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
        return phase1_points(self.max_hints_seen) + phase2_points(self.map_correct_count())

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
        phase = TEXT[self.lang]["phase1"] if self.phase == "quiz" else TEXT[self.lang]["phase2"]
        if self.phase == "done":
            phase = TEXT[self.lang]["complete_title"]
        draw_text(self.screen, phase, self.fonts["normal"], MUTED, (36, 54))
        back_rect = pygame.Rect(760, 18, 122, 34)
        button(self.screen, back_rect, TEXT[self.lang]["back"], self.fonts["small"], AMBER, WHITE)
        if self.click_pos and back_rect.collidepoint(self.click_pos) and self.cooldown <= 0:
            self.cooldown = 12
            self.go_back()

        draw_text(self.screen, f"{TEXT[self.lang]['score']} {self.score()}", self.fonts["normal"], GREEN, (910, 24))
        draw_text(self.screen, f"{TEXT[self.lang]['time']} {self.elapsed()}", self.fonts["normal"], MUTED, (1010, 24))

        for idx, (code, label) in enumerate([("zh", "中"), ("ja", "日")]):
            rect = pygame.Rect(1040 + idx * 48, 52, 38, 28)
            selected = self.lang == code
            button(self.screen, rect, label, self.fonts["small"], BLUE if selected else WHITE, WHITE if selected else INK, LINE)
            if self.click_pos and rect.collidepoint(self.click_pos) and self.cooldown <= 0:
                self.lang = code
                self.cooldown = 12

    def draw_quiz(self) -> None:
        country = self.current()
        panel = pygame.Rect(44, 122, 520, 610)
        pygame.draw.rect(self.screen, CARD, panel, border_radius=8)
        pygame.draw.rect(self.screen, LINE, panel, 2, border_radius=8)
        draw_text(self.screen, f"{TEXT[self.lang]['question']} {self.index + 1}/7", self.fonts["subtitle"], INK, (panel.x + 28, panel.y + 26))
        draw_text(self.screen, tr(country.role, self.lang), self.fonts["normal"], country.color, (panel.x + 28, panel.y + 68))

        y = panel.y + 116
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
            self.max_hints_seen = max(self.max_hints_seen, self.hints_seen)
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
            pygame.draw.rect(self.screen, item.color if rect.collidepoint(mouse) else LINE, rect, 2, border_radius=8)
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
                    self.hints_seen = 1
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
            pygame.draw.circle(self.screen, country.color, (x, y), 10)
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
            bg = country.color if selected else WHITE
            button(self.screen, rect, tr(country.name, self.lang), self.fonts["button"], bg, WHITE if selected else INK, country.color)
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
            pygame.draw.circle(self.screen, country.color, pos, 16)
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
        if self.phase == "quiz":
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
