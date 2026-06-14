import random


GAME_CONFIG = {
    "randomize_levels": False,
    "operators": ["+", "-", "×", "÷"],
    "level_count": 11,
}


LEVELS = [
    {
        "numbers": [1, 2, 3, 4],
        "target": 10,
        "desc": {"zh": "", "ja": ""},
        "isDemo": True,
    },
    {
        "numbers": [3, 3, 3],
        "target": 6,
        "desc": {"zh": "經典暖身題", "ja": "定番のウォーミングアップ"},
    },
    {
        "numbers": [5, 5, 5],
        "target": 6,
        "desc": {"zh": "這題要用到除法喔", "ja": "割り算を使う問題です"},
    },
    {
        "numbers": [4, 4, 4, 4],
        "target": 24,
        "desc": {
            "zh": "湊出 24 (注意先乘除後加減，有多解)",
            "ja": "24を作る（掛け算・割り算優先、複数解あり）",
        },
    },
    {
        "numbers": [6, 8, 4, 2],
        "target": 10,
        "desc": {
            "zh": "不同數字的混合運算 (有多解)",
            "ja": "異なる数字の混合計算（複数解あり）",
        },
    },
    {
        "numbers": [5, 5, 5, 5],
        "target": 24,
        "desc": {
            "zh": "進階挑戰：這個 24 不好湊！",
            "ja": "上級チャレンジ：この24は少し難しい！",
        },
    },
    {
        "numbers": [9, 8, 6, 7],
        "target": 5,
        "desc": {
            "zh": "魔王題：善用乘法與除法的搭配",
            "ja": "ボス問題：掛け算と割り算の組み合わせを活用しよう",
        },
    },
    {
        "numbers": [9, 3, 4, 2, 5, 1],
        "target": 10,
        "desc": {
            "zh": "資源分配題：只需填入 5 個符號，每個符號最多使用 2 次！",
            "ja": "資源配分問題：5つの記号を入力、各記号は最大2回まで！",
        },
        "operatorLimits": {"+": 2, "-": 2, "×": 2, "÷": 2},
    },
    {
        "numbers": [5, 9, 3, 6, 2],
        "target": 19,
        "desc": {
            "zh": "終極挑戰：每個符號最多使用 2 次，找出能得出 19 的組合！",
            "ja": "究極の挑戦：各記号は最大2回まで、19になる組み合わせを見つけよう！",
        },
        "operatorLimits": {"+": 2, "-": 2, "×": 2, "÷": 2},
    },
    {
        "numbers": [6, 6, 6, 6],
        "targetDisplay": {"zh": "奇數", "ja": "奇数"},
        "desc": {
            "zh": "邏輯題：組出結果為奇數的算式！",
            "ja": "論理問題：結果が奇数になる式を作ろう！",
        },
        "isLogicMode": True,
        "checkResult": lambda res: res is not None and res % 2 == 1,
        "logicBlocks": [
            {
                "label": "if (result % 2 === 1)",
                "desc": {
                    "zh": "// ✓ 成功做出奇數！",
                    "ja": "// ✓ 奇数を作ることに成功しました！",
                },
                "isMatch": lambda res: res is not None and res % 2 == 1,
            },
            {
                "label": "else",
                "desc": {
                    "zh": "// ✗ 結果不是奇數",
                    "ja": "// ✗ 結果は奇数ではありません",
                },
                "isMatch": lambda res: res is not None and res % 2 != 1,
            },
        ],
    },
    {
        "numbers": [2, 3, 4, 5],
        "targetDisplay": {"zh": "< 0", "ja": "< 0"},
        "desc": {
            "zh": "終極邏輯題：符號各最多1次，想辦法讓結果小於零！",
            "ja": "究極の論理問題：各記号は最大1回、結果をゼロ未満にしよう！",
        },
        "isLogicMode": True,
        "checkResult": lambda res: res is not None and res < 0,
        "operatorLimits": {"+": 1, "-": 1, "×": 1, "÷": 1},
        "logicBlocks": [
            {
                "label": "if (result < 0)",
                "desc": {
                    "zh": "// ✓ 成功製造出負數！",
                    "ja": "// ✓ 負の数を作ることに成功しました！",
                },
                "isMatch": lambda res: res is not None and res < 0,
            },
            {
                "label": "else if (result === 0)",
                "desc": {
                    "zh": "// ✗ 結果剛好等於 0",
                    "ja": "// ✗ 結果はちょうど0です",
                },
                "isMatch": lambda res: res is not None and res == 0,
            },
            {
                "label": "else",
                "desc": {
                    "zh": "// ✗ 結果大於 0",
                    "ja": "// ✗ 結果は0より大きいです",
                },
                "isMatch": lambda res: res is not None and res > 0,
            },
        ],
    },
]


def build_level_order(randomize_levels: bool):
    """Build the playable level order while keeping the demo first."""
    playable_count = min(GAME_CONFIG["level_count"], len(LEVELS))
    order = list(range(playable_count))
    if randomize_levels and len(order) > 1:
        demo_level = order[0]
        rest = order[1:]
        random.shuffle(rest)
        order = [demo_level] + rest
    return order
