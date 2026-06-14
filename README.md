# Micro Game - Challenge Games

用 Pygame 實作的闖關活動遊戲集，依照 `闖關活動詳細版.pdf` 拆成 A、B 兩個獨立遊戲，並提供主選單。支援中文與日文。

## 功能特性

- 主選單可選擇不同闖關遊戲
- 所有遊戲都在同一個 Pygame 視窗內切換，不會另外開新視窗
- 遊戲內可按「回主畫面」或 `ESC` 返回主選單
- A 關：記憶體跨國製程，包含國家線索問答與世界地圖定位
- B 關：透過程式驗證結果，包含 PDF 內的示範題與 10 題正式挑戰
- 🌐 中日雙語支援（中文、日文）
- 內附完整 Noto Sans CJK 字體，避免中文/日文顯示成方框
- ⏱️ 計時功能
- 🔢 运算符数量限制挑战
- 🧠 逻辑模式关卡（if-else 编程思维）
- ⌨️ 键盘和鼠标操作支持
- 🧩 各遊戲都有自己的資料夾與 config，方便分開維護
- 🔀 可在 `games/math/config.py` 中切換 B 關是否隨機題目順序

## 安装依赖

```bash
# 安装 pygame
pip3 install pygame
```

## 运行游戏

```bash
python3 main.py
```

也可以單獨啟動個別遊戲：

```bash
python3 country_game.py
python3 math_game.py
```

## 檔案結構

- `main.py`：主選單入口
- `main_menu.py`：選擇遊戲主視窗
- `games/country/game.py`：A 關「跟著晶片環遊世界」
- `games/country/config.py`：A 關說明、國家題目、提示、地圖位置與計分規則
- `games/math/game.py`：B 關「像工程師一樣思考」
- `games/math/config.py`：B 關題庫設定
- `country_game.py`、`math_game.py`、`game_config.py`：相容舊指令的薄入口
- `ui_shared.py`：共用字體、顏色與文字工具
- `assets/fonts/NotoSansCJK-Regular.ttc`：中文與日文顯示用一般字體
- `assets/fonts/NotoSansCJK-Bold.ttc`：中文與日文顯示用粗體字體

## B 關操作

### 鼠标操作
- 点击运算符按钮（+、-、×、÷）填入表达式
- 点击操作符槽位可以修改或删除操作符

### 键盘操作
- `+` - 输入加号
- `-` - 输入减号
- `*` 或 `x` 或 `X` - 输入乘号
- `/` - 输入除号
- `Backspace` - 删除上一个操作符
- `ESC` - 退出游戏

## 游戏玩法

1. 在数字之间插入运算符，使等式的结果等于目标值
2. 根据关卡的特定规则完成挑战
3. 某些关卡有运算符使用次数限制
4. 逻辑模式关卡要求达到特定条件（如结果为奇数或小于零）

## 关卡说明

- **第 0 关**：示范关卡 (1+2×3+4=10)
- **第 1 关**：经典暖身题
- **第 2-5 关**：逐级困难的数学运算题
- **第 6-7 关**：资源限制挑战（运算符有使用次数限制）
- **第 8-9 关**：逻辑编程模式（考察特定条件而非具体数值）

## 題庫設定

A 關資料集中在 [games/country/config.py](games/country/config.py)。
B 關題目集中在 [games/math/config.py](games/math/config.py)。

可以在 `games/math/config.py` 的 `GAME_CONFIG` 裡調整：

- `randomize_levels = False`：固定題目順序
- `randomize_levels = True`：每次啟動時隨機排列正式題目，示範題固定第一關

## 計時規則

- 計時從正式挑戰開始後啟動
- 當最後一題完成時，計時會立即停止
- 完成畫面顯示的是最終耗時，不會再繼續增加

## 技术栈

- Python 3
- Pygame 库
- 支持 CJK 字符的字体

## 游戏成功条件

完成所有 10 个关卡后，游戏会显示总耗时并允许重新开始。
# micro_mini_game
