from __future__ import annotations

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
        "title": "闖關活動遊戲選單",
        "subtitle": "選擇要進行的關卡",
        "language": "語言",
        "play": "開始",
        "quit": "離開",
        "back_hint": "遊戲內可按「回主畫面」或 ESC 回到這個選單",
    },
    "ja": {
        "title": "ミッションゲーム選択",
        "subtitle": "プレイするステージを選んでください",
        "language": "言語",
        "play": "開始",
        "quit": "終了",
        "back_hint": "ゲーム内の「メニューへ」または ESC で戻れます",
    },
}


GAMES = [
    {
        "id": "country",
        "color": CYAN,
        "soft": SOFT_BLUE,
        "title": {
            "zh": "A 關：全球科技偵探",
            "ja": "A ステージ：Global Tech Detective",
        },
        "desc": {
            "zh": "閱讀情境故事、提示與思考例子，從 4 個選項中找出正確國家。",
            "ja": "ストーリー、ヒント、考え方を読んで、4択から正しい国を選びます。",
        },
    },
    {
        "id": "math",
        "color": GREEN,
        "soft": SOFT_GREEN,
        "title": {
            "zh": "B 關：像工程師一樣思考",
            "ja": "B ステージ：エンジニアのように考える",
        },
        "desc": {
            "zh": "在有限運算符號下拆解目標數，透過程式即時驗證算式是否符合條件。",
            "ja": "限られた演算記号で目標の数を分解し、プログラムで条件に合うか確認します。",
        },
    },
    {
        "id": "ai_image",
        "color": VIOLET,
        "soft": SOFT_AMBER,
        "title": {
            "zh": "C 關：AI 圖片偵探",
            "ja": "C ステージ：AI 画像探偵",
        },
        "desc": {
            "zh": "每關同時顯示 AI 與真實照片各一張，從左右兩張中選出 AI 生成圖片。",
            "ja": "AI画像と実写画像を1枚ずつ表示し、左右からAI生成画像を選びます。",
        },
    },
]


class MainMenu:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Challenge Games")
        self.clock = pygame.time.Clock()
        self.fonts = make_fonts()
        self.lang = "zh"
        self.running = True
        self.cooldown = 0
        self.active_game = None
        self.click_pos = None

    def return_to_menu(self, lang: str | None = None) -> None:
        if lang in ("zh", "ja"):
            self.lang = lang
        self.active_game = None
        pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Challenge Games")

    def run_game(self, game_id: str) -> None:
        if game_id == "country":
            from games.country.game import CountryGame

            self.active_game = CountryGame(
                screen=self.screen,
                embedded=True,
                initial_lang=self.lang,
                on_back=self.return_to_menu,
            )
        elif game_id == "math":
            from games.math.game import Game

            self.active_game = Game(
                screen_surface=self.screen,
                embedded=True,
                initial_lang=self.lang,
                on_back=self.return_to_menu,
            )
        elif game_id == "ai_image":
            from games.AI_game.main import AIGame

            self.active_game = AIGame(
                screen=self.screen,
                embedded=True,
                initial_lang=self.lang,
                on_back=self.return_to_menu,
            )

    def handle_events(self) -> None:
        self.click_pos = None
        if self.active_game is not None:
            game = self.active_game
            game.handle_events()
            if self.active_game is game and not game.running:
                lang = getattr(getattr(game, "game_state", None), "lang", None)
                lang = getattr(game, "lang", lang)
                self.return_to_menu(lang)
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.click_pos = event.pos
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_1:
                    self.run_game(GAMES[0]["id"])
                elif event.key == pygame.K_2:
                    self.run_game(GAMES[1]["id"])
                elif event.key == pygame.K_3:
                    self.run_game(GAMES[2]["id"])

    def draw_language_switcher(self) -> None:
        label = TEXT[self.lang]["language"]
        draw_text(self.screen, label, self.fonts["small"], MUTED, (SCREEN_WIDTH - 184, 24))
        mouse = pygame.mouse.get_pos()
        click = self.click_pos
        for idx, (code, text) in enumerate([("zh", "中"), ("ja", "日")]):
            rect = pygame.Rect(SCREEN_WIDTH - 112 + idx * 46, 18, 38, 34)
            selected = self.lang == code
            button(
                self.screen,
                rect,
                text,
                self.fonts["small"],
                BLUE if selected else WHITE,
                WHITE if selected else INK,
                LINE,
            )
            if click and rect.collidepoint(click) and self.cooldown <= 0:
                self.lang = code
                self.cooldown = 12

    def draw_game_card(self, game: dict, index: int, rect: pygame.Rect) -> None:
        mouse = pygame.mouse.get_pos()
        click = self.click_pos
        hovered = rect.collidepoint(mouse)
        shadow = pygame.Rect(rect.x + 4, rect.y + 5, rect.width, rect.height)
        pygame.draw.rect(self.screen, (210, 220, 235), shadow, border_radius=8)
        pygame.draw.rect(self.screen, CARD, rect, border_radius=8)
        pygame.draw.rect(self.screen, game["color"] if hovered else LINE, rect, 2, border_radius=8)

        badge = pygame.Rect(rect.x + 28, rect.y + 28, 72, 72)
        pygame.draw.rect(self.screen, game["soft"], badge, border_radius=8)
        draw_text(self.screen, f"{index + 1}", self.fonts["title"], game["color"], (badge.x + 27, badge.y + 18))

        draw_text(self.screen, tr(game["title"], self.lang), self.fonts["subtitle"], INK, (rect.x + 124, rect.y + 28))
        desc_rect = pygame.Rect(rect.x + 124, rect.y + 68, rect.width - 168, 78)
        draw_wrapped(self.screen, tr(game["desc"], self.lang), self.fonts["normal"], SLATE, desc_rect, 5, 3)

        play_rect = pygame.Rect(rect.right - 164, rect.bottom - 62, 126, 40)
        button(self.screen, play_rect, TEXT[self.lang]["play"], self.fonts["button"], game["color"])
        if click and (play_rect.collidepoint(click) or rect.collidepoint(click)) and self.cooldown <= 0:
            self.cooldown = 20
            self.run_game(game["id"])

    def draw(self) -> None:
        if self.active_game is not None:
            self.active_game.draw()
            return

        self.screen.fill(BG)
        pygame.draw.rect(self.screen, WHITE, (0, 0, SCREEN_WIDTH, 92))
        pygame.draw.line(self.screen, LINE, (0, 92), (SCREEN_WIDTH, 92), 2)
        draw_text(self.screen, TEXT[self.lang]["title"], self.fonts["title"], BLACK, (48, 22))
        draw_text(self.screen, TEXT[self.lang]["subtitle"], self.fonts["normal"], MUTED, (50, 58))
        self.draw_language_switcher()

        card_w = 900
        card_h = 150
        start_y = 122
        gap = 174
        for idx, game in enumerate(GAMES):
            rect = pygame.Rect((SCREEN_WIDTH - card_w) // 2, start_y + idx * gap, card_w, card_h)
            self.draw_game_card(game, idx, rect)
            if self.active_game is not None:
                return

        hint = TEXT[self.lang]["back_hint"]
        draw_text(self.screen, hint, self.fonts["small"], MUTED, (48, SCREEN_HEIGHT - 58))
        quit_rect = pygame.Rect(SCREEN_WIDTH - 170, SCREEN_HEIGHT - 72, 118, 42)
        button(self.screen, quit_rect, TEXT[self.lang]["quit"], self.fonts["button"], AMBER, WHITE)
        if self.click_pos and quit_rect.collidepoint(self.click_pos) and self.cooldown <= 0:
            self.running = False
        pygame.display.flip()

    def tick_cooldowns(self) -> None:
        self.cooldown -= 1
        if self.active_game is None:
            return
        if hasattr(self.active_game, "cooldown"):
            self.active_game.cooldown -= 1
        if hasattr(self.active_game, "click_cooldown"):
            self.active_game.click_cooldown -= 1

    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.draw()
            self.tick_cooldowns()
            self.clock.tick(60)
        pygame.quit()


if __name__ == "__main__":
    MainMenu().run()
