import pygame

# --- 視窗設定 ---
WIDTH, HEIGHT = 600, 800

# --- 顏色 ---
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# --- 遊戲參數 ---
PLAYER_SPEED = 5
BULLET_SPEED = -10
ENEMY_SPEED = 2
BOSS_HP = 100
CASTLE_HP = 1000

# 字型
pygame.font.init()
font = pygame.font.SysFont("Arial", 24)

# --- 金錢與升級 ---
ENEMY_REWARD = {10: 10, 20: 20, 30: 30}  # HP 對應獎金
BULLET_BASE_SPEED = 7
BULLET_BASE_DAMAGE = 5
UPGRADE_COST = 50
UPGRADE_SPEED_INC = 2
UPGRADE_DAMAGE_INC = 2