import pygame
from config import WIDTH, HEIGHT, WHITE, font

# 背景
BACKGROUND_IMG = pygame.image.load("Image/background/background0.jpg")
BACKGROUND_IMG = pygame.transform.scale(BACKGROUND_IMG, (WIDTH, HEIGHT))

# 主堡圖片，縮小為 100x100，正上方
CASTLE_IMG = pygame.image.load("Image/castle/castle0.png")
CASTLE_IMG = pygame.transform.scale(CASTLE_IMG, (200, 200))
CASTLE_POS = (WIDTH//2 - CASTLE_IMG.get_width()//2, 0)

# Boss 圖片，縮小為 80x80
BOSS_IMG = pygame.image.load("Image/boss/boss0.png")
BOSS_IMG = pygame.transform.scale(BOSS_IMG, (200, 200))

# 敵人圖片，統一縮小為 40x40
ENEMY_IMGS = [
    pygame.image.load("Image/enemy/enemy0.png"),
    pygame.image.load("Image/enemy/enemy00.png"),
    pygame.image.load("Image/enemy/enemy000.png")
]
ENEMY_IMGS = [pygame.transform.scale(img, (40, 40)) for img in ENEMY_IMGS]

# 主頁面
def draw_menu(screen):
    screen.blit(BACKGROUND_IMG, (0,0))
    title = font.render("game", True, WHITE)
    prompt = font.render("Press space to start.", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 50))
    screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2 + 10))

# 勝利/失敗畫面
def draw_end_screen(screen, win=True):
    screen.blit(BACKGROUND_IMG, (0,0))
    msg = "VICTORY!" if win else "LOSE！"
    text = font.render(msg, True, WHITE)
    prompt = font.render("Press space to restart.", True, WHITE)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 50))
    screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2 + 10))

# 遊戲主畫面
def draw_game_screen(screen, all_sprites, enemies, castle, boss, money):
    # 背景
    screen.blit(BACKGROUND_IMG, (0,0))

    # 畫主堡
    screen.blit(CASTLE_IMG, CASTLE_POS)
    castle_rect = CASTLE_IMG.get_rect(topleft=CASTLE_POS)
    castle.rect.center = castle_rect.center  # 更新城堡位置供敵人攻擊檢測
    castle.draw(screen, font)

    # 畫敵人
    for enemy in enemies:
        img = ENEMY_IMGS[getattr(enemy, "type_index", 0)]
        enemy_rect = img.get_rect(center=enemy.rect.center)
        screen.blit(img, enemy_rect)
        enemy.draw_hp(screen)

    # 畫 Boss
    if boss and boss.alive():
        boss_rect = BOSS_IMG.get_rect(center=boss.rect.center)
        screen.blit(BOSS_IMG, boss_rect)
        boss.draw_hp(screen)

    # 畫玩家及子彈
    all_sprites.draw(screen)

    # 金錢顯示
    money_text = font.render(f"Money: {money}", True, WHITE)
    screen.blit(money_text, (10, 60))