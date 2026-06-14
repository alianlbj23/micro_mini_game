import pygame
import sys
from typing import List, Dict, Optional, Tuple
import time
import math
from pathlib import Path

from games.math.config import GAME_CONFIG, LEVELS, build_level_order

# Initialize Pygame
pygame.init()

# 多國語言字典
TRANSLATIONS = {
    "zh": {
        "title": "透過程式驗證結果：像工程師一樣思考",
        "demoTitle": "關主操作示範",
        "demoBadge": "範例題",
        "subtitle": "結合運算思維與數學，讓等式完美成立！",
        "startBtn": "開始挑戰",
        "startRealGame": "正式開始挑戰",
        "awesome": "太厲害了！",
        "finishText": "你不僅精通數學運算，更完美克服了資源限制與邏輯挑戰！",
        "playAgain": "再玩一次",
        "backToMenu": "回主畫面",
        "level": "關卡",
        "logicMode": "if-else 版",
        "limitMode": "數量限制",
        "tracker": "邏輯追蹤器",
        "correctMsg": "✓ 算式正確！",
        "tooBigMsg": "✗ 數值太大了",
        "tooSmallMsg": "✗ 數值太小了",
        "clearBtn": "清除重來",
        "nextBtn": "下一關",
        "remain": "剩",
        "timeElapsed": "總共耗時：",
        "errorInf": "無限大(錯誤)",
    },
    "ja": {
        "title": "プログラムで結果を検証する：エンジニアのように考える",
        "demoTitle": "マスター操作デモ",
        "demoBadge": "例題",
        "subtitle": "論理的思考と数学を組み合わせて、等式を完成させよう！",
        "startBtn": "チャレンジ開始",
        "startRealGame": "本番チャレンジ開始",
        "awesome": "すばらしい！",
        "finishText": "数学の計算だけでなく、資源の制限や論理的課題も見事にクリアしました！",
        "playAgain": "もう一度プレイ",
        "backToMenu": "メニューへ",
        "level": "ステージ",
        "logicMode": "if-else 版",
        "limitMode": "回数制限",
        "tracker": "ロジックトラッカー",
        "correctMsg": "✓ 正解です！",
        "tooBigMsg": "✗ 値が大きすぎます",
        "tooSmallMsg": "✗ 値が小さすぎます",
        "clearBtn": "やり直す",
        "nextBtn": "次のステージへ",
        "remain": "残",
        "timeElapsed": "クリアタイム：",
        "errorInf": "エラー(無限大)",
    },
}

OPERATORS = GAME_CONFIG["operators"]

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# Colors
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_BG = (241, 245, 250)
COLOR_DARK_BG = (15, 23, 42)
COLOR_CARD = (255, 255, 255)
COLOR_BLUE = (59, 130, 246)
COLOR_GREEN = (34, 197, 94)
COLOR_RED = (239, 68, 68)
COLOR_SLATE_700 = (51, 65, 85)
COLOR_SLATE_600 = (71, 85, 105)
COLOR_SLATE_300 = (203, 213, 225)

# Font sizes
FONT_TITLE = 28
FONT_NORMAL = 16
FONT_BUTTON = 18
FONT_NUMBER = 40
FONT_OPERATOR = 28
FONT_TUTORIAL = 14

# Create display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Micro Game - Math Puzzle")

# Fonts - Support for CJK characters
def load_fonts():
    """Load fonts with CJK support"""
    font_dir = Path(__file__).resolve().parents[2] / "assets" / "fonts"
    local_regular = font_dir / "NotoSansCJK-Regular.ttc"
    local_bold = font_dir / "NotoSansCJK-Bold.ttc"
    if local_regular.exists():
        title_path = local_bold if local_bold.exists() else local_regular
        print(f"✓ 已加载專案字體: {local_regular}")
        return (
            pygame.font.Font(str(title_path), FONT_TITLE),
            pygame.font.Font(str(local_regular), FONT_NORMAL),
            pygame.font.Font(str(title_path), FONT_BUTTON),
            pygame.font.Font(str(local_regular), FONT_NUMBER),
            pygame.font.Font(str(local_regular), FONT_OPERATOR),
            pygame.font.Font(str(local_regular), FONT_TUTORIAL),
        )

    # macOS系统推荐字体列表（已验证可用）
    font_names = ["heititc", "heitisc", "STHeiti", "simhei", "notosanscjksc"]
    
    cjk_font = None
    for font_name in font_names:
        try:
            cjk_font = pygame.font.SysFont(font_name, FONT_NORMAL)
            print(f"✓ 已加载字体: {font_name}")
            break
        except Exception as e:
            print(f"  尝试 {font_name}... 失败")
    
    # 使用回退字体
    if cjk_font is None:
        print("使用系统默认字体")
        cjk_font = pygame.font.Font(None, FONT_NORMAL)
    
    # 为了确保所有文本显示，所有字体都用同一个CJK字体
    return cjk_font, cjk_font, cjk_font, pygame.font.Font(None, FONT_NUMBER), pygame.font.Font(None, FONT_OPERATOR), cjk_font

print("=" * 60)
print("初始化字体...")
print("=" * 60)
title_font, normal_font, button_font, number_font, operator_font, tutorial_font = load_fonts()
print("=" * 60 + "\n")


class GameState:
    def __init__(self):
        self.state = "playing"  # playing, finished, tutorial
        self.level = 0
        self.level_order = build_level_order(GAME_CONFIG["randomize_levels"])
        self.lang = "zh"
        self.slots: List[str] = []
        self.active_slot = 0
        self.status = "idle"  # idle, correct, wrong
        self.expression_result: Optional[float] = None
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.time_elapsed = 0
        self.show_tutorial = True  # Show tutorial on demo level
        self.init_level(0)

    def current_level(self):
        return LEVELS[self.level_order[self.level]]

    def init_level(self, level_index: int):
        self.level = level_index
        level = self.current_level()
        num_slots = len(level["numbers"]) - 1
        self.slots = [""] * num_slots
        self.active_slot = 0
        self.status = "idle"
        self.expression_result = None
        self.end_time = None
        if level_index == 1:
            self.start_time = time.time()

    def get_time_elapsed(self) -> int:
        effective_end_time = self.end_time if self.end_time is not None else time.time()
        return int(effective_end_time - self.start_time)

    def format_time(self, seconds: int) -> str:
        m = seconds // 60
        s = seconds % 60
        return f"{m:02d}:{s:02d}"

    def evaluate_expression(self) -> Optional[float]:
        level = self.current_level()
        expression = ""

        for i, num in enumerate(level["numbers"]):
            expression += str(num)
            if i < len(self.slots) and self.slots[i]:
                op = self.slots[i]
                if op == "×":
                    expression += " * "
                elif op == "÷":
                    expression += " / "
                else:
                    expression += f" {op} "

        try:
            result = eval(expression)
            if isinstance(result, (int, float)) and (math.isnan(result) or math.isinf(result)):
                return None
            return result
        except:
            return None

    def check_answer(self):
        result = self.evaluate_expression()
        self.expression_result = result
        
        if result is None:
            self.status = "wrong"
            return

        level = self.current_level()
        if level.get("isLogicMode"):
            if level.get("checkResult")(result):
                self.status = "correct"
                if self.level == len(self.level_order) - 1:
                    self.end_time = time.time()
            else:
                self.status = "wrong"
        else:
            target = level.get("target")
            if abs(result - target) < 0.0001:
                self.status = "correct"
                if self.level == len(self.level_order) - 1:
                    self.end_time = time.time()
            else:
                self.status = "wrong"

    def get_remaining_count(self, op: str) -> Optional[int]:
        level = self.current_level()
        if "operatorLimits" not in level:
            return None
        limit = level["operatorLimits"].get(op)
        if limit is None:
            return None
        used = self.slots.count(op)
        return limit - used

    def handle_operator(self, op: str):
        level = self.current_level()
        if self.status == "correct" and not level.get("isDemo"):
            return
        if self.active_slot == -1:
            return

        remaining = self.get_remaining_count(op)
        if remaining is not None and remaining <= 0:
            return

        self.slots[self.active_slot] = op
        
        next_empty = -1
        for i, slot in enumerate(self.slots):
            if slot == "":
                next_empty = i
                break
        
        if next_empty != -1:
            self.active_slot = next_empty
            self.status = "idle"
            self.expression_result = None
        else:
            self.active_slot = -1
            self.check_answer()

    def handle_clear(self):
        level = self.current_level()
        self.slots = [""] * (len(level["numbers"]) - 1)
        self.active_slot = 0
        self.status = "idle"
        self.expression_result = None

    def handle_next_level(self):
        if self.level + 1 < len(self.level_order):
            self.init_level(self.level + 1)
        else:
            if self.end_time is None:
                self.end_time = time.time()
            self.state = "finished"

    def restart_game(self):
        self.level_order = build_level_order(GAME_CONFIG["randomize_levels"])
        self.state = "playing"
        self.level = 0
        self.start_time = time.time()
        self.end_time = None
        self.show_tutorial = True
        self.init_level(0)

    def switch_language(self):
        self.lang = "ja" if self.lang == "zh" else "zh"


class Game:
    def __init__(self, screen_surface=None, embedded: bool = False, initial_lang: str = "zh", on_back=None):
        global screen
        if screen_surface is not None:
            screen = screen_surface
        self.embedded = embedded
        self.on_back = on_back
        self.game_state = GameState()
        if initial_lang in ("zh", "ja"):
            self.game_state.lang = initial_lang
        self.clock = pygame.time.Clock()
        self.running = True
        self.click_cooldown = 0
        self.click_pos = None

    def go_back(self):
        self.running = False
        if self.on_back:
            self.on_back(self.game_state.lang)

    def handle_events(self):
        self.click_pos = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.click_pos = event.pos
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.go_back()
                elif event.unicode in ["+", "-"]:
                    if event.unicode == "+":
                        self.game_state.handle_operator("+")
                    else:
                        self.game_state.handle_operator("-")
                elif event.unicode in ["*", "x", "X"]:
                    self.game_state.handle_operator("×")
                elif event.unicode == "/":
                    self.game_state.handle_operator("÷")
                elif event.key == pygame.K_BACKSPACE:
                    if self.game_state.active_slot != -1 and self.game_state.slots[self.game_state.active_slot]:
                        self.game_state.slots[self.game_state.active_slot] = ""
                    elif self.game_state.active_slot == -1 and self.game_state.slots:
                        self.game_state.slots[-1] = ""
                        self.game_state.active_slot = len(self.game_state.slots) - 1
                    self.game_state.status = "idle"
                    self.game_state.expression_result = None

    def draw(self):
        screen.fill(COLOR_BG)
        t = TRANSLATIONS[self.game_state.lang]

        if self.game_state.state == "finished":
            self.draw_finished_screen(t)
        elif self.game_state.show_tutorial and self.game_state.level == 0:
            self.draw_tutorial_screen(t)
        else:
            self.draw_playing_screen(t)

        # Language switcher
        self.draw_language_switcher(t)
        self.draw_back_button(t)
        pygame.display.flip()

    def draw_back_button(self, t):
        back_rect = pygame.Rect(16, 10, 120, 34)
        pygame.draw.rect(screen, COLOR_SLATE_300, back_rect, border_radius=8)
        pygame.draw.rect(screen, COLOR_SLATE_700, back_rect, 1, border_radius=8)
        back_text = normal_font.render(t["backToMenu"], True, COLOR_BLACK)
        screen.blit(back_text, back_text.get_rect(center=back_rect.center))
        if self.click_pos and back_rect.collidepoint(self.click_pos) and self.click_cooldown <= 0:
            self.click_cooldown = 10
            self.go_back()

    def draw_language_switcher(self, t):
        btn_width, btn_height = 40, 30
        x_start = SCREEN_WIDTH - 100
        y_start = 10

        # Chinese button
        zh_rect = pygame.Rect(x_start, y_start, btn_width, btn_height)
        zh_color = COLOR_BLUE if self.game_state.lang == "zh" else COLOR_WHITE
        pygame.draw.rect(screen, zh_color, zh_rect, border_radius=8)
        pygame.draw.rect(screen, COLOR_SLATE_300, zh_rect, 2, border_radius=8)
        zh_text = normal_font.render("中", True, COLOR_WHITE if self.game_state.lang == "zh" else COLOR_BLACK)
        screen.blit(zh_text, zh_text.get_rect(center=zh_rect.center))

        if self.click_pos and zh_rect.collidepoint(self.click_pos) and self.click_cooldown <= 0:
            self.game_state.lang = "zh"
            self.click_cooldown = 10

        # Japanese button
        ja_rect = pygame.Rect(x_start + btn_width + 10, y_start, btn_width, btn_height)
        ja_color = COLOR_BLUE if self.game_state.lang == "ja" else COLOR_WHITE
        pygame.draw.rect(screen, ja_color, ja_rect, border_radius=8)
        pygame.draw.rect(screen, COLOR_SLATE_300, ja_rect, 2, border_radius=8)
        ja_text = normal_font.render("日", True, COLOR_WHITE if self.game_state.lang == "ja" else COLOR_BLACK)
        screen.blit(ja_text, ja_text.get_rect(center=ja_rect.center))

        if self.click_pos and ja_rect.collidepoint(self.click_pos) and self.click_cooldown <= 0:
            self.game_state.lang = "ja"
            self.click_cooldown = 10

    def draw_finished_screen(self, t):
        # Draw finished screen
        card_width = min(450, SCREEN_WIDTH - 40)
        card_height = min(600, SCREEN_HEIGHT - 40)
        card_x = (SCREEN_WIDTH - card_width) // 2
        card_y = (SCREEN_HEIGHT - card_height) // 2

        pygame.draw.rect(screen, COLOR_CARD, (card_x, card_y, card_width, card_height), border_radius=20)
        pygame.draw.rect(screen, COLOR_GREEN, (card_x, card_y, card_width, 8), border_radius=20)
        
        # Title
        title_text = normal_font.render(t["awesome"], True, COLOR_GREEN)
        screen.blit(title_text, (card_x + 20, card_y + 30))

        # Message
        msg_surf = normal_font.render(t["finishText"], True, COLOR_SLATE_700)
        msg_rect = msg_surf.get_rect()
        msg_rect.topleft = (card_x + 20, card_y + 80)
        screen.blit(msg_surf, msg_rect)

        # Time display
        elapsed = self.game_state.get_time_elapsed()
        time_str = self.game_state.format_time(elapsed)
        time_label = normal_font.render(t["timeElapsed"], True, COLOR_SLATE_600)
        screen.blit(time_label, (card_x + 20, card_y + 160))
        time_text = normal_font.render(time_str, True, COLOR_BLUE)
        screen.blit(time_text, (card_x + 20, card_y + 190))

        # Play again button
        btn_width = card_width - 40
        btn_height = 50
        btn_x = card_x + 20
        btn_y = card_y + card_height - 80

        button_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
        pygame.draw.rect(screen, COLOR_GREEN, button_rect, border_radius=12)
        btn_text = normal_font.render(t["playAgain"], True, COLOR_WHITE)
        screen.blit(btn_text, btn_text.get_rect(center=button_rect.center))

        if self.click_pos and button_rect.collidepoint(self.click_pos) and self.click_cooldown <= 0:
            self.game_state.restart_game()
            self.click_cooldown = 10

    def draw_tutorial_screen(self, t):
        """Draw tutorial screen for demo level"""
        tutorial_texts = {
            "zh": [
                "【示範關卡教學】",
                "",
                "我們先看示範題，目標是 10。",
                "",
                "❌ 如果我先憑直覺輸入：1 + 2 + 3 - 4",
                "   算出來等於 2。我們按確認看看……",
                "   程式顯示「數值太小了」。",
                "   這代表我的計算結果比目標 10 還小，",
                "   我需要重新規劃運算符號。",
                "",
                "沒關係，我們按「清除重來」，這次換個邏輯試試看。",
                "",
                "✓ 如果我輸入：1 + 2 + 3 + 4 = 10",
                "  按下確認——太棒了，程式顯示「算式正確！」",
                "",
                "這裡的解法不只一種。",
                "我們按「清除重來」，這次我換個更複雜的邏輯組合試試看。",
                "",
                "✓ 如果我用乘法加法混合呢？",
                "  輸入 1 × 2 × 3 + 4 = 10",
                "  按照運算規則（先乘除後加減），6 + 4 等於 10。",
                "  按下確認——太棒了，程式同樣顯示「算式正確！」。",
                "",
                "數學邏輯非常靈活，這兩組不同的算式都能",
                "通往相同的答案。在接下來的正式挑戰中，",
                "只要能讓算式等於目標數，就是好方法！",
            ],
            "ja": [
                "【デモレベルチュートリアル】",
                "",
                "最初にデモ問題を見てみましょう。目標は 10 です。",
                "",
                "❌ 直感で入力してみたら：1 + 2 + 3 - 4",
                "   結果は 2 です。確認を押してみます……",
                "   プログラムは「値が小さすぎます」と表示します。",
                "   計算結果が目標の 10 より小さいということです。",
                "   演算記号を再計画する必要があります。",
                "",
                "大丈夫です。「やり直す」を押して、別のロジックを試してみます。",
                "",
                "✓ もし入力したら：1 + 2 + 3 + 4 = 10",
                "  確認を押します——素晴らしい！プログラムは「正解です！」を表示します",
                "",
                "ここには複数の解があります。",
                "もう一度「やり直す」を押して、別のロジックを試してみます。",
                "",
                "✓ もし乗法と加法を混ぜたら？",
                "  入力します 1 × 2 × 3 + 4 = 10",
                "  演算規則に従う（掛け算・割り算優先）、6 + 4 = 10。",
                "  確認を押します——素晴らしい！プログラムも「正解です！」を表示します。",
                "",
                "数学ロジックは非常に柔軟です。これら 2 つの異なる式",
                "は同じ答えに達することができます。次の正式な挑戦では、",
                "式が目標数に等しければ、それが良い方法です！",
            ]
        }

        # Get tutorial text based on language
        texts = tutorial_texts.get(self.game_state.lang, tutorial_texts["zh"])

        # Draw semi-transparent background
        bg_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        bg_surface.set_alpha(200)
        bg_surface.fill(COLOR_BG)
        screen.blit(bg_surface, (0, 0))

        # Draw tutorial card
        card_width = min(900, SCREEN_WIDTH - 40)
        card_height = SCREEN_HEIGHT - 120
        card_x = (SCREEN_WIDTH - card_width) // 2
        card_y = 50

        pygame.draw.rect(screen, COLOR_CARD, (card_x, card_y, card_width, card_height), border_radius=15)
        pygame.draw.rect(screen, COLOR_BLUE, (card_x, card_y, card_width, card_height), 3, border_radius=15)

        # Draw scrollable text
        line_height = 22
        padding_x = 30
        padding_y = 25
        max_lines_visible = (card_height - 2 * padding_y - 60) // line_height

        for idx, text in enumerate(texts):
            if idx >= max_lines_visible:
                break
            
            y = card_y + padding_y + idx * line_height
            
            # Different colors for different line types - use normal_font for all CJK text
            if text.startswith("【"):
                color = COLOR_BLUE
            elif text.startswith("❌"):
                color = COLOR_RED
            elif text.startswith("✓"):
                color = COLOR_GREEN
            else:
                color = COLOR_SLATE_700

            if text.strip():
                text_surf = normal_font.render(text, True, color)
                screen.blit(text_surf, (card_x + padding_x, y))

        # Draw "Start Challenge" button
        btn_width = 200
        btn_height = 50
        btn_x = (SCREEN_WIDTH - btn_width) // 2
        btn_y = SCREEN_HEIGHT - 80

        button_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
        pygame.draw.rect(screen, COLOR_GREEN, button_rect, border_radius=12)
        btn_text = normal_font.render(t["startRealGame"], True, COLOR_WHITE)
        screen.blit(btn_text, btn_text.get_rect(center=button_rect.center))

        if self.click_pos and button_rect.collidepoint(self.click_pos) and self.click_cooldown <= 0:
            self.game_state.show_tutorial = False
            self.click_cooldown = 10

    def draw_playing_screen(self, t):
        level = self.game_state.current_level()

        # Title and level info
        title = t["demoTitle"] if level.get("isDemo") else t["title"]
        # Use a slightly larger normal font for title
        title_surf = pygame.Surface((SCREEN_WIDTH - 40, 40))
        title_surf.fill(COLOR_BG)
        title_text = normal_font.render(title, True, COLOR_SLATE_700)
        screen.blit(title_text, (20, 20))

        # Time display
        elapsed = self.game_state.get_time_elapsed()
        if not level.get("isDemo"):
            time_str = self.game_state.format_time(elapsed)
            time_text = normal_font.render(f"{t['timeElapsed']}{time_str}", True, COLOR_SLATE_600)
            screen.blit(time_text, (SCREEN_WIDTH - 250, 20))

        # Level indicator
        if not level.get("isDemo"):
            level_str = f"{t['level']} {self.game_state.level}/{len(self.game_state.level_order)-1}"
        else:
            level_str = t["demoBadge"]
        level_text = normal_font.render(level_str, True, COLOR_BLUE)
        screen.blit(level_text, (SCREEN_WIDTH - 200, 50))

        # Expression display (numbers and operator slots)
        self.draw_expression(level, t)

        # Operator buttons
        self.draw_operator_buttons(level, t)

        # Logic tracker
        self.draw_logic_tracker(level, t)

        # Control buttons
        self.draw_control_buttons(level, t)

    def draw_expression(self, level, t):
        numbers = level["numbers"]
        num_boxes = len(numbers)
        operator_boxes = num_boxes - 1

        # Calculate layout
        box_size = 60
        spacing = 15
        total_width = (num_boxes * (box_size + spacing) +
                      operator_boxes * (box_size + spacing) +
                      100)
        
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = 120

        current_x = start_x

        # Draw numbers and operator slots
        for i in range(num_boxes):
            # Number box
            pygame.draw.rect(screen, COLOR_DARK_BG, (current_x, start_y, box_size, box_size), border_radius=8)
            num_text = number_font.render(str(numbers[i]), True, COLOR_WHITE)
            num_rect = num_text.get_rect(center=(current_x + box_size // 2, start_y + box_size // 2))
            screen.blit(num_text, num_rect)
            current_x += box_size + spacing

            # Operator slot
            if i < operator_boxes:
                op_box_rect = pygame.Rect(current_x, start_y, box_size, box_size)
                slot_color = COLOR_BLUE if (self.game_state.active_slot == i and self.game_state.status != "correct") else COLOR_SLATE_300
                pygame.draw.rect(screen, slot_color if self.game_state.slots[i] else COLOR_WHITE, op_box_rect, border_radius=8)
                pygame.draw.rect(screen, COLOR_BLUE if (self.game_state.active_slot == i and self.game_state.status != "correct") else COLOR_SLATE_300, op_box_rect, 2, border_radius=8)
                
                if self.game_state.slots[i]:
                    op_text = operator_font.render(self.game_state.slots[i], True, COLOR_BLUE)
                    op_rect = op_text.get_rect(center=(current_x + box_size // 2, start_y + box_size // 2))
                    screen.blit(op_text, op_rect)
                
                # Check if slot clicked
                if self.click_pos and op_box_rect.collidepoint(self.click_pos) and self.click_cooldown <= 0:
                    if self.game_state.slots[i]:
                        self.game_state.slots[i] = ""
                    self.game_state.active_slot = i
                    self.game_state.status = "idle"
                    self.game_state.expression_result = None
                    self.click_cooldown = 5

                current_x += box_size + spacing

        # Draw = sign
        eq_text = normal_font.render("=", True, COLOR_SLATE_300)
        screen.blit(eq_text, (current_x + 5, start_y + 20))
        current_x += 40

        # Draw result
        display_result = "?"
        if self.game_state.expression_result is not None:
            if isinstance(self.game_state.expression_result, float):
                if math.isfinite(self.game_state.expression_result):
                    if self.game_state.expression_result % 1 == 0:
                        display_result = str(int(self.game_state.expression_result))
                    else:
                        display_result = f"{self.game_state.expression_result:.2f}"
            else:
                display_result = str(self.game_state.expression_result)
        else:
            if level.get("isLogicMode") and level.get("targetDisplay"):
                display_result = level["targetDisplay"].get(self.game_state.lang, "?")
            else:
                display_result = str(level.get("target", "?"))

        result_color = COLOR_GREEN if self.game_state.status == "correct" else COLOR_SLATE_600
        pygame.draw.rect(screen, result_color if self.game_state.status == "correct" else COLOR_WHITE, 
                        (current_x, start_y, box_size, box_size), border_radius=8)
        result_text = number_font.render(display_result, True, COLOR_WHITE if self.game_state.status == "correct" else COLOR_BLACK)
        result_rect = result_text.get_rect(center=(current_x + box_size // 2, start_y + box_size // 2))
        screen.blit(result_text, result_rect)

    def draw_operator_buttons(self, level, t):
        button_width = 70
        button_height = 70
        spacing = 15
        total_width = (4 * button_width) + (3 * spacing)
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = 250

        for i, op in enumerate(OPERATORS):
            btn_x = start_x + i * (button_width + spacing)
            btn_rect = pygame.Rect(btn_x, start_y, button_width, button_height)

            remaining = self.game_state.get_remaining_count(op)
            is_limit_reached = remaining is not None and remaining <= 0
            is_disabled = (self.game_state.status == "correct" and not level.get("isDemo")) or is_limit_reached

            btn_color = COLOR_SLATE_300 if is_disabled else COLOR_BLUE
            pygame.draw.rect(screen, btn_color, btn_rect, border_radius=12)
            pygame.draw.rect(screen, btn_color, btn_rect, 2, border_radius=12)

            op_text = operator_font.render(op, True, COLOR_WHITE if is_disabled else COLOR_BLACK)
            op_rect = op_text.get_rect(center=btn_rect.center)
            screen.blit(op_text, op_rect)

            # Draw remaining count
            if remaining is not None:
                remaining_color = COLOR_RED if remaining == 0 else COLOR_BLUE
                remaining_text = normal_font.render(f"{remaining}", True, remaining_color)
                screen.blit(remaining_text, (btn_x + 5, start_y + 5))

            # Handle click
            if self.click_pos and btn_rect.collidepoint(self.click_pos) and not is_disabled and self.click_cooldown <= 0:
                self.game_state.handle_operator(op)
                self.click_cooldown = 5

    def draw_logic_tracker(self, level, t):
        tracker_x = 20
        tracker_y = 380
        tracker_width = SCREEN_WIDTH - 40
        tracker_height = 150

        pygame.draw.rect(screen, COLOR_DARK_BG, (tracker_x, tracker_y, tracker_width, tracker_height), border_radius=10)

        # Title
        title_text = normal_font.render(t['tracker'], True, COLOR_SLATE_300)
        screen.blit(title_text, (tracker_x + 15, tracker_y + 10))

        # Result display
        display_result = t["errorInf"]
        if self.game_state.expression_result is not None:
            if isinstance(self.game_state.expression_result, float):
                if math.isfinite(self.game_state.expression_result):
                    if self.game_state.expression_result % 1 == 0:
                        display_result = str(int(self.game_state.expression_result))
                    else:
                        display_result = f"{self.game_state.expression_result:.2f}"
            else:
                display_result = str(self.game_state.expression_result)

        result_line = f"let result = {display_result};"
        result_text = normal_font.render(result_line, True, (100, 200, 255))
        screen.blit(result_text, (tracker_x + 15, tracker_y + 35))

    def draw_control_buttons(self, level, t):
        button_height = 50
        button_width = 150
        spacing = 20
        start_y = SCREEN_HEIGHT - 80

        # Clear button
        clear_x = (SCREEN_WIDTH // 2) - button_width - spacing // 2
        clear_rect = pygame.Rect(clear_x, start_y, button_width, button_height)
        is_clear_enabled = self.game_state.status == "idle" or level.get("isDemo")
        clear_color = COLOR_SLATE_300 if not is_clear_enabled else COLOR_SLATE_300
        pygame.draw.rect(screen, clear_color, clear_rect, border_radius=10)
        clear_text = normal_font.render(t["clearBtn"], True, COLOR_BLACK if is_clear_enabled else COLOR_SLATE_600)
        screen.blit(clear_text, clear_text.get_rect(center=clear_rect.center))

        if self.click_pos and clear_rect.collidepoint(self.click_pos) and is_clear_enabled and self.click_cooldown <= 0:
            self.game_state.handle_clear()
            self.click_cooldown = 5

        # Next button
        next_x = (SCREEN_WIDTH // 2) + spacing // 2
        next_rect = pygame.Rect(next_x, start_y, button_width, button_height)
        is_next_enabled = level.get("isDemo") or self.game_state.status == "correct"
        pygame.draw.rect(screen, COLOR_GREEN if is_next_enabled else COLOR_SLATE_300, next_rect, border_radius=10)
        next_text = normal_font.render(t["nextBtn"], True, COLOR_WHITE if is_next_enabled else COLOR_SLATE_600)
        screen.blit(next_text, next_text.get_rect(center=next_rect.center))

        if self.click_pos and next_rect.collidepoint(self.click_pos) and is_next_enabled and self.click_cooldown <= 0:
            self.game_state.handle_next_level()
            self.click_cooldown = 5

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            self.click_cooldown -= 1
            self.clock.tick(60)

        if not self.embedded:
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
