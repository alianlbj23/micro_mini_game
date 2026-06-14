from __future__ import annotations

import sys
import time
from typing import Dict

import pygame

from games.country.config import GAME_TITLE, POINTS_BONUS, POINTS_NORMAL, QUESTIONS
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
    SOFT_BLUE,
    SOFT_GREEN,
    SOFT_AMBER,
    WHITE,
    button,
    draw_text,
    draw_wrapped,
    make_fonts,
)


TEXT: Dict[str, Dict[str, str]] = {
    "zh": {
        "start": "開始挑戰",
        "back": "回主畫面",
        "score": "分數",
        "mission": "Mission",
        "hint": "提示",
        "scenario": "情境故事",
        "thinking": "思考例子",
        "choices": "選擇答案",
        "correct": "答對了！",
        "wrong": "答錯了，正確答案是：",
        "knowledge": "小知識",
        "next": "下一題",
        "finish": "完成",
        "restart": "再玩一次",
        "done": "任務完成！",
        "done_text": "你已完成半導體供應鏈國家挑戰。",
        "correct_count": "答對題數",
        "time": "時間",
        "final_time": "完成時間",
        "rules_1": "每題會顯示 3 個提示，請從 4 個選項中選出正確國家。",
        "rules_2": "每題先讀情境故事、3 個提示與思考例子，再從 4 個選項中推理正確國家。",
        "rules_3": "答對一般題加 100 分，bonus 題答對加 150 分，答錯不扣分。",
        "summary": "7 題｜一般題 100 分｜bonus 題 150 分",
        "practice_label": "練習題",
        "bonus_label": "Bonus 挑戰",
        "normal_label": "科技據點調查",
        "target_country": "目標國家",
    },
    "ja": {
        "start": "チャレンジ開始",
        "back": "メニューへ",
        "score": "得点",
        "mission": "Mission",
        "hint": "ヒント",
        "scenario": "ストーリー",
        "thinking": "考え方の例",
        "choices": "答えを選ぶ",
        "correct": "正解です！",
        "wrong": "不正解です。正解は：",
        "knowledge": "豆知識",
        "next": "次の問題",
        "finish": "完了",
        "restart": "もう一度",
        "done": "ミッション完了！",
        "done_text": "半導体サプライチェーンの国クイズを完了しました。",
        "correct_count": "正解数",
        "time": "時間",
        "final_time": "クリアタイム",
        "rules_1": "各問題では3つのヒントを読み、4つの選択肢から正しい国を選びます。",
        "rules_2": "ストーリー、3つのヒント、考え方の例を読んで、正しい国を推理します。",
        "rules_3": "通常問題は100点、bonus問題は150点。不正解でも減点はありません。",
        "summary": "7問｜通常問題 100点｜bonus問題 150点",
        "practice_label": "練習問題",
        "bonus_label": "Bonus チャレンジ",
        "normal_label": "技術拠点調査",
        "target_country": "目標の国",
    },
}


class CountryGame:
    def __init__(self, screen=None, embedded: bool = False, initial_lang: str = "zh", on_back=None) -> None:
        self.embedded = embedded
        self.on_back = on_back
        pygame.init()
        self.screen = screen or pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Chip World Tour")
        self.clock = pygame.time.Clock()
        self.fonts = make_fonts()
        self.lang = initial_lang if initial_lang in TEXT else "zh"
        self.running = True
        self.phase = "start"
        self.index = 0
        self.score = 0
        self.correct_count = 0
        self.selected_choice: str | None = None
        self.is_correct = False
        self.start_time: float | None = None
        self.end_time: float | None = None
        self.cooldown = 0
        self.click_pos = None

    def t(self, key: str) -> str:
        return TEXT.get(self.lang, TEXT["zh"]).get(key, TEXT["zh"][key])

    def current_question(self) -> dict:
        return QUESTIONS[self.index]

    def question_text(self, question: dict) -> dict:
        return question["text"].get(self.lang) or question["text"]["zh"]

    def question_points(self, question: dict) -> int:
        return question.get("points") or (POINTS_BONUS if question["type"] == "bonus" else POINTS_NORMAL)

    def elapsed_seconds(self) -> int:
        if self.start_time is None:
            return 0
        end = self.end_time if self.end_time is not None else time.time()
        return int(end - self.start_time)

    def format_time(self, seconds: int) -> str:
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def question_label(self, question: dict) -> str:
        if question["type"] == "practice":
            return self.t("practice_label")
        if question["type"] == "bonus":
            return self.t("bonus_label")
        return self.t("normal_label")

    def thinking_text(self, question: dict) -> str:
        text = self.question_text(question)
        return text["thinking_example"].replace(text["answer"], self.t("target_country"))

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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.go_back()

    def draw_header(self) -> None:
        pygame.draw.rect(self.screen, WHITE, (0, 0, SCREEN_WIDTH, 88))
        pygame.draw.line(self.screen, LINE, (0, 88), (SCREEN_WIDTH, 88), 2)
        draw_text(self.screen, GAME_TITLE, self.fonts["subtitle"], BLACK, (34, 20))
        draw_text(self.screen, f"{self.t('score')} {self.score}", self.fonts["normal"], GREEN, (910, 20))
        draw_text(self.screen, f"{self.t('time')} {self.format_time(self.elapsed_seconds())}", self.fonts["normal"], MUTED, (910, 52))

        back_rect = pygame.Rect(760, 18, 122, 34)
        button(self.screen, back_rect, self.t("back"), self.fonts["small"], AMBER, WHITE)
        if self.click_pos and back_rect.collidepoint(self.click_pos) and self.cooldown <= 0:
            self.cooldown = 12
            self.go_back()

    def draw_start(self) -> None:
        card = pygame.Rect(150, 160, 900, 470)
        pygame.draw.rect(self.screen, CARD, card, border_radius=8)
        pygame.draw.rect(self.screen, LINE, card, 2, border_radius=8)

        draw_text(self.screen, GAME_TITLE, self.fonts["title"], BLACK, (card.x + 48, card.y + 54))
        draw_wrapped(self.screen, self.t("rules_1"), self.fonts["normal"], INK, pygame.Rect(card.x + 52, card.y + 130, card.width - 104, 55), 5)
        draw_wrapped(self.screen, self.t("rules_2"), self.fonts["normal"], INK, pygame.Rect(card.x + 52, card.y + 190, card.width - 104, 55), 5)
        draw_wrapped(self.screen, self.t("rules_3"), self.fonts["normal"], INK, pygame.Rect(card.x + 52, card.y + 250, card.width - 104, 55), 5)

        draw_text(self.screen, self.t("summary"), self.fonts["normal"], MUTED, (card.x + 52, card.y + 315))

        start_rect = pygame.Rect(card.centerx - 95, card.y + 350, 190, 54)
        button(self.screen, start_rect, self.t("start"), self.fonts["button"], GREEN)
        if self.click_pos and start_rect.collidepoint(self.click_pos) and self.cooldown <= 0:
            self.phase = "question"
            self.start_time = time.time()
            self.end_time = None
            self.cooldown = 12

    def draw_question(self) -> None:
        question = self.current_question()
        text = self.question_text(question)
        total = len(QUESTIONS)
        left = pygame.Rect(34, 110, 720, 650)
        right = pygame.Rect(784, 110, 370, 650)
        pygame.draw.rect(self.screen, CARD, left, border_radius=8)
        pygame.draw.rect(self.screen, LINE, left, 2, border_radius=8)
        pygame.draw.rect(self.screen, CARD, right, border_radius=8)
        pygame.draw.rect(self.screen, LINE, right, 2, border_radius=8)

        draw_text(self.screen, f"{self.t('mission')} {self.index + 1:02d} / {total:02d}", self.fonts["subtitle"], BLUE, (left.x + 32, left.y + 28))
        draw_text(self.screen, self.question_label(question), self.fonts["title"], BLACK, (left.x + 32, left.y + 66))

        scenario_rect = pygame.Rect(left.x + 32, left.y + 116, left.width - 64, 96)
        pygame.draw.rect(self.screen, SOFT_AMBER, scenario_rect, border_radius=8)
        draw_text(self.screen, self.t("scenario"), self.fonts["small"], MUTED, (scenario_rect.x + 16, scenario_rect.y + 10))
        draw_wrapped(self.screen, text["scenario"], self.fonts["small"], INK, pygame.Rect(scenario_rect.x + 16, scenario_rect.y + 34, scenario_rect.width - 32, 56), 3)

        y = left.y + 226
        for idx, hint in enumerate(text["hints"], start=1):
            hint_rect = pygame.Rect(left.x + 32, y, left.width - 64, 72)
            pygame.draw.rect(self.screen, SOFT_BLUE, hint_rect, border_radius=8)
            draw_text(self.screen, f"{self.t('hint')} {idx}", self.fonts["tiny"], MUTED, (hint_rect.x + 16, hint_rect.y + 8))
            draw_wrapped(self.screen, hint, self.fonts["small"], INK, pygame.Rect(hint_rect.x + 16, hint_rect.y + 30, hint_rect.width - 32, 34), 3)
            y += 84

        thinking_rect = pygame.Rect(left.x + 32, y + 4, left.width - 64, 116)
        pygame.draw.rect(self.screen, (232, 245, 233), thinking_rect, border_radius=8)
        draw_text(self.screen, self.t("thinking"), self.fonts["small"], MUTED, (thinking_rect.x + 16, thinking_rect.y + 10))
        draw_wrapped(self.screen, self.thinking_text(question), self.fonts["small"], INK, pygame.Rect(thinking_rect.x + 16, thinking_rect.y + 36, thinking_rect.width - 32, 70), 3)

        draw_text(self.screen, self.t("choices"), self.fonts["subtitle"], BLACK, (right.x + 28, right.y + 28))
        click = self.click_pos
        mouse = pygame.mouse.get_pos()
        for idx, choice in enumerate(text["choices"]):
            rect = pygame.Rect(right.x + 30, right.y + 96 + idx * 96, right.width - 60, 62)
            hover = rect.collidepoint(mouse)
            pygame.draw.rect(self.screen, SOFT_GREEN if hover else WHITE, rect, border_radius=8)
            pygame.draw.rect(self.screen, GREEN if hover else LINE, rect, 2, border_radius=8)
            draw_text(self.screen, choice, self.fonts["button"], INK, (rect.x + 22, rect.y + 16))
            if click and rect.collidepoint(click) and self.cooldown <= 0:
                self.answer(choice)
                self.cooldown = 12

    def answer(self, choice: str) -> None:
        question = self.current_question()
        text = self.question_text(question)
        self.selected_choice = choice
        self.is_correct = choice == text["answer"]
        if self.is_correct:
            self.correct_count += 1
            self.score += self.question_points(question)
        self.phase = "result"

    def draw_result(self) -> None:
        question = self.current_question()
        text = self.question_text(question)
        card = pygame.Rect(170, 145, 860, 520)
        pygame.draw.rect(self.screen, CARD, card, border_radius=8)
        pygame.draw.rect(self.screen, GREEN if self.is_correct else RED, card, 3, border_radius=8)

        result_text = self.t("correct") if self.is_correct else f"{self.t('wrong')}{text['answer']}"
        result_color = GREEN if self.is_correct else RED
        draw_text(self.screen, result_text, self.fonts["title"], result_color, (card.x + 48, card.y + 50))
        draw_text(self.screen, text["title"], self.fonts["subtitle"], BLACK, (card.x + 48, card.y + 112))
        draw_text(self.screen, self.t("knowledge"), self.fonts["subtitle"], BLUE, (card.x + 48, card.y + 180))
        draw_wrapped(self.screen, text["explanation"], self.fonts["normal"], INK, pygame.Rect(card.x + 48, card.y + 222, card.width - 96, 100), 6)

        points = self.question_points(question)
        points_text = f"+{points}" if self.is_correct else "+0"
        draw_text(self.screen, f"{self.t('score')} {self.score} ({points_text})", self.fonts["normal"], MUTED, (card.x + 48, card.y + 345))

        is_last = self.index == len(QUESTIONS) - 1
        next_label = self.t("finish") if is_last else self.t("next")
        next_rect = pygame.Rect(card.right - 210, card.bottom - 82, 160, 48)
        button(self.screen, next_rect, next_label, self.fonts["button"], GREEN)
        if self.click_pos and next_rect.collidepoint(self.click_pos) and self.cooldown <= 0:
            if is_last:
                self.phase = "done"
                self.end_time = time.time()
            else:
                self.index += 1
                self.selected_choice = None
                self.is_correct = False
                self.phase = "question"
            self.cooldown = 12

    def draw_done(self) -> None:
        card = pygame.Rect(260, 175, 680, 430)
        pygame.draw.rect(self.screen, CARD, card, border_radius=8)
        pygame.draw.rect(self.screen, GREEN, card, 3, border_radius=8)
        draw_text(self.screen, self.t("done"), self.fonts["title"], GREEN, (card.x + 48, card.y + 54))
        draw_wrapped(self.screen, self.t("done_text"), self.fonts["normal"], INK, pygame.Rect(card.x + 48, card.y + 118, card.width - 96, 60), 5)
        draw_text(self.screen, f"{self.t('score')} {self.score}", self.fonts["subtitle"], BLUE, (card.x + 48, card.y + 210))
        draw_text(self.screen, f"{self.t('correct_count')} {self.correct_count} / {len(QUESTIONS)}", self.fonts["subtitle"], BLACK, (card.x + 48, card.y + 260))
        draw_text(self.screen, f"{self.t('final_time')} {self.format_time(self.elapsed_seconds())}", self.fonts["subtitle"], MUTED, (card.x + 48, card.y + 310))

        restart = pygame.Rect(card.x + 48, card.bottom - 78, 150, 48)
        menu = pygame.Rect(card.right - 198, card.bottom - 78, 150, 48)
        button(self.screen, restart, self.t("restart"), self.fonts["button"], GREEN)
        button(self.screen, menu, self.t("back"), self.fonts["button"], BLUE)
        if self.click_pos and restart.collidepoint(self.click_pos) and self.cooldown <= 0:
            self.__init__(screen=self.screen, embedded=self.embedded, initial_lang=self.lang, on_back=self.on_back)
            self.cooldown = 12
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
    CountryGame().run()
