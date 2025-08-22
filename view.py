import pygame
import json
import os
from config import WIDTH, HEIGHT, WHITE, font

# 背景
BACKGROUND_IMG = pygame.image.load("Image/background/background0.jpg")
BACKGROUND_IMG = pygame.transform.scale(BACKGROUND_IMG, (WIDTH, HEIGHT))

# 主堡圖片
CASTLE_IMG = pygame.image.load("Image/castle/castle0.png")
CASTLE_IMG = pygame.transform.scale(CASTLE_IMG, (200, 200))
CASTLE_POS = (WIDTH // 2 - CASTLE_IMG.get_width() // 2, 0)

# Boss 圖片（3關各自不同，可暫時先用同圖）
BOSS_IMGS = [
    pygame.image.load("Image/boss/boss0.png"),
    pygame.image.load("Image/boss/boss0.png"),
    pygame.image.load("Image/boss/boss0.png")
]
BOSS_IMGS = [pygame.transform.scale(img, (200, 200)) for img in BOSS_IMGS]

# 敵人圖片（目前 6 種，先全部用同圖，可再替換）
ENEMY_IMGS = [
    pygame.image.load("Image/enemy/enemy0.png"),
    pygame.image.load("Image/enemy/enemy00.png"),
    pygame.image.load("Image/enemy/enemy000.png"),
    pygame.image.load("Image/enemy/enemy0.png"),
    pygame.image.load("Image/enemy/enemy00.png"),
    pygame.image.load("Image/enemy/enemy000.png"),
    pygame.image.load("Image/enemy/enemy0.png"),
    pygame.image.load("Image/enemy/enemy00.png"),
    pygame.image.load("Image/enemy/enemy000.png")
]
ENEMY_IMGS = [pygame.transform.scale(img, (40, 40)) for img in ENEMY_IMGS]

# --- 畫出路徑 ---
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

# --- 主畫面 ---
def draw_menu(screen):
    screen.blit(BACKGROUND_IMG, (0,0))
    title = font.render("Game", True, WHITE)
    prompt = font.render("Press SPACE to start.", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 50))
    screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2 + 10))

# --- 勝利/失敗畫面 ---
def draw_end_screen(screen, win=True):
    screen.blit(BACKGROUND_IMG, (0,0))
    msg = "VICTORY!" if win else "LOSE!"
    text = font.render(msg, True, WHITE)
    prompt = font.render("Press SPACE to continue.", True, WHITE)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 50))
    screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2 + 10))

# --- 遊戲主畫面 ---
def draw_game_screen(screen, all_sprites, enemies, castle, boss, money, show_path=True, level=1):
    screen.blit(BACKGROUND_IMG, (0,0))
    if show_path:
        draw_path_polyline(screen)

    # 主堡
    screen.blit(CASTLE_IMG, CASTLE_POS)
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

    # 玩家 sprite
    all_sprites.draw(screen)
    for spr in all_sprites:
        if hasattr(spr, "draw_overlay"):
            spr.draw_overlay(screen)

    # 金錢
    money_text = font.render(f"Money: {money}", True, WHITE)
    screen.blit(money_text, (10,10))

    # 關卡顯示
    level_text = font.render(f"Level {level}", True, WHITE)
    screen.blit(level_text, (10, HEIGHT-30))
