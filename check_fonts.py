#!/usr/bin/env python3
"""检查系统中可用的字体"""

import pygame
pygame.init()

print("=" * 60)
print("检测系统中可用的字体")
print("=" * 60)

# 获取所有系统字体
all_fonts = pygame.font.get_fonts()
print(f"\n总共找到 {len(all_fonts)} 种字体\n")

# 查找 CJK 相关字体
cjk_keywords = ['heiti', 'simhei', 'microsoft', 'yahei', 'noto', 'wenquanyi', 'pingfang', 'hiragino', 'messiri']
cjk_fonts = []

print("寻找 CJK (中日韓) 字体:")
print("-" * 60)
for font in all_fonts:
    for keyword in cjk_keywords:
        if keyword.lower() in font.lower():
            cjk_fonts.append(font)
            print(f"  ✓ {font}")
            break

if not cjk_fonts:
    print("  ⚠ 未找到 CJK 字体")

print("\n" + "=" * 60)
print("测试字体加载:")
print("=" * 60)

# 测试加载
font_names = ["STHeiti", "simhei", "Microsoft YaHei", "ubuntu", "arial"]
for font_name in font_names:
    try:
        test_font = pygame.font.SysFont(font_name, 16)
        print(f"✓ 成功加载: {font_name}")
    except Exception as e:
        print(f"✗ 无法加载: {font_name} ({e})")

print("\n" + "=" * 60)
print("推荐:")
print("=" * 60)
print("如果未找到 CJK 字体，请安装:")
print("  macOS:  brew install font-wqy-zenhei")
print("  Linux:  sudo apt install fonts-wqy-zenhei")
print("  或安装 Noto Sans CJK 字体")
print("=" * 60 + "\n")
