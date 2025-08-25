import pygame
import json
import os
from config import WIDTH, HEIGHT, WHITE, font, title_font, YELLOW, title_font_small

# 背景
BACKGROUND_IMG = pygame.image.load("Image/background/background0.jpg")
BACKGROUND_IMG = pygame.transform.scale(BACKGROUND_IMG, (WIDTH, HEIGHT))

# 城堡圖片（每關可分開設定）
CASTLE_IMGS = [
    pygame.image.load("Image/castle/castle1.png"),  # 關卡1
    pygame.image.load("Image/castle/castle2.png"),  # 關卡2
    pygame.image.load("Image/castle/castle3.png")   # 關卡3
]
CASTLE_IMGS = [pygame.transform.scale(img, (200, 200)) for img in CASTLE_IMGS]
CASTLE_POS = (WIDTH // 2 - 100, 0)

# Boss 圖片
BOSS_IMGS = [
    pygame.image.load("Image/boss/boss1.png"),
    pygame.image.load("Image/boss/boss2.png"),
    pygame.image.load("Image/boss/boss3.png")
]
BOSS_IMGS = [pygame.transform.scale(img, (200, 200)) for img in BOSS_IMGS]

# 敵人圖片
ENEMY_IMGS = [
    pygame.image.load(f"Image/enemy/enemy{i}-{j}.png") for i in range(1,4) for j in range(1,4)
]
ENEMY_IMGS = [pygame.transform.scale(img, (40, 40)) for img in ENEMY_IMGS]

# 中文文字渲染函式
def render_chinese_text_surface(text, font, color, spacing=0):
    chars = list(text)
    images = [font.render(ch, True, color) for ch in chars]
    total_width = sum(img.get_width() for img in images) + spacing * (len(images)-1)
    height = max(img.get_height() for img in images)
    surface = pygame.Surface((total_width, height), pygame.SRCALPHA)
    x = 0
    for img in images:
        surface.blit(img, (x, 0))
        x += img.get_width() + spacing
    return surface

# 路徑線
def draw_path_polyline(screen):
    if not os.path.exists("path.json"):
        return
    with open("path.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    pts = [pygame.Vector2(p[0], p[1]) for p in data["points"]]
    if len(pts) < 2:
        return
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    pygame.draw.lines(overlay, (255, 255, 255, 120), False, pts, 6)
    for p in pts:
        pygame.draw.rect(overlay, (255, 255, 255, 200), (int(p.x)-4, int(p.y)-4, 8, 8))
    screen.blit(overlay, (0,0))

# 按鈕
def draw_button(screen, rect, text, font, text_color=WHITE, hover_color=YELLOW, bg_color=(100,100,100)):
    mouse_pos = pygame.mouse.get_pos()
    render_color = hover_color if rect.collidepoint(mouse_pos) else text_color
    pygame.draw.rect(screen, bg_color, rect, border_radius=8)
    text_surface = font.render(text, True, render_color)
    screen.blit(text_surface, (rect.centerx - text_surface.get_width()//2,
                               rect.centery - text_surface.get_height()//2))

# 主選單
def draw_menu(screen):
    screen.blit(BACKGROUND_IMG, (0,0))
    title = render_chinese_text_surface("《時空城防：台南異象》", title_font, WHITE, spacing=4)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 100))

    start_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 20, 200, 50)
    howto_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)
    draw_button(screen, start_rect, "START", font)
    draw_button(screen, howto_rect, "how to play", font)

    return {"start": start_rect, "howto": howto_rect}

# 勝利/失敗畫面
def draw_end_screen(screen, win=True, level=1, final_level=3):
    screen.blit(BACKGROUND_IMG, (0,0))
    if win:
        if level < final_level:
            msg = "VICTORY!"
            prompt = "Press SPACE to next level"
        else:
            msg = "THE WORLD IS SAVED !!!"
            prompt = "Press SPACE to title"
    else:
        msg = "LOSE!"
        prompt = "Press SPACE to continue."

    text = font.render(msg, True, WHITE)
    prompt_text = font.render(prompt, True, WHITE)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 50))
    screen.blit(prompt_text, (WIDTH//2 - prompt_text.get_width()//2, HEIGHT//2 + 10))

# 劇情
def draw_story(screen):
    screen.blit(BACKGROUND_IMG, (0,0))
    story_text0 = title_font_small.render("STORY", True, WHITE)
    screen.blit(story_text0, (WIDTH//2 - story_text0.get_width()//2, HEIGHT//4 - 90))

    lines = [
        "在不久的未來，台南古城因為神秘的能量波動",
        "而陷入了時間的混亂。",
        "不同時期的時空裂縫逐一開啟，讓來自荷蘭時期、明鄭時期",
        "等各種歷史階段的敵人穿越而來，意圖佔領古城。",
        "玩家將化身為守護者，肩負起保衛古城的使命，",
        "利用手中的力量抵禦一波波入侵。",
        "隨著戰鬥推進，玩家不僅要擊退敵人，還能逐步解鎖",
        "不同時代的故事片段，體驗守護台南歷史文化的榮耀與挑戰。"
    ]
    start_y = HEIGHT//4 - 30
    line_spacing = 30
    for i, line in enumerate(lines):
        text_surface = render_chinese_text_surface(line, font, WHITE, spacing=4)
        screen.blit(text_surface, (WIDTH//2 - text_surface.get_width()//2, start_y + i*line_spacing))

    go_rect = pygame.Rect(WIDTH//2 - 60, start_y + len(lines)*line_spacing + 20, 120, 40)
    draw_button(screen, go_rect, "GO!!!", font)
    return {"go": go_rect}

# 教學
def draw_tutorial(screen):
    screen.blit(BACKGROUND_IMG, (0, 0))
    start_y = HEIGHT//4
    line_spacing = 30
    side_margin = 40
    lines = [
        "P1：",
        "UP、DOWN：調整守護塔射擊方向",
        "M：升級武器(可以造成更高傷害及提升速度)",
        " ",
        "P2：",
        "W、S：調整守護塔射擊方向",
        "E：升級武器(可以造成更高傷害及提升速度)"
    ]
    for i, line in enumerate(lines):
        text_surface = render_chinese_text_surface(line, font, WHITE, spacing=4)
        screen.blit(text_surface, (side_margin, start_y + i*line_spacing))

    ok_rect = pygame.Rect(WIDTH//2 - 60, HEIGHT//2 + 50, 120, 40)
    draw_button(screen, ok_rect, "OK", font)
    return {"ok": ok_rect}    

# 遊戲主畫面
def draw_game_screen(screen, all_sprites, enemies, castle, boss, money, show_path=True, level=1, enemy_bullets=None):
    screen.blit(BACKGROUND_IMG, (0,0))
    if show_path:
        draw_path_polyline(screen)

    # 城堡
    castle_img = CASTLE_IMGS[level-1] if level-1 < len(CASTLE_IMGS) else CASTLE_IMGS[0]
    screen.blit(castle_img, CASTLE_POS)
    castle.rect.topleft = CASTLE_POS
    castle.draw(screen, font)

    # 敵人
    for enemy in enemies:
        img = ENEMY_IMGS[getattr(enemy, "type_index", 0)]
        enemy_rect = img.get_rect(center=enemy.rect.center)
        screen.blit(img, enemy_rect)
        if hasattr(enemy, "draw_hp"):
            enemy.draw_hp(screen)

    # Boss
    if boss and boss.alive():
        boss_img = BOSS_IMGS[level-1]
        boss_rect = boss_img.get_rect(center=boss.rect.center)
        screen.blit(boss_img, boss_rect)
        if hasattr(boss, "draw_hp"):
            boss.draw_hp(screen)

    # 玩家
    all_sprites.draw(screen)
    for spr in all_sprites:
        if hasattr(spr, "draw_overlay"):
            spr.draw_overlay(screen)

    # 敵人子彈
    if enemy_bullets:
        for b in enemy_bullets:
            pygame.draw.rect(screen, (255, 0, 0), b.rect)
            pygame.draw.line(screen, (255, 100, 100),
                             (b.rect.centerx, b.rect.centery),
                             (b.rect.centerx - b.speedx*2, b.rect.centery - b.speedy*2), 2)

    # 金錢
    money_text = font.render(f"Money: {money}", True, WHITE)
    screen.blit(money_text, (10,10))

    # 關卡
    level_text = font.render(f"Level {level}", True, WHITE)
    screen.blit(level_text, (10, HEIGHT-30))
