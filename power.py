import pygame, random, time
from config import WIDTH, HEIGHT

POWER_IMG = pygame.image.load("Image/power/power0.png")
POWER_IMG = pygame.transform.scale(POWER_IMG, (30, 30))

class Power(pygame.sprite.Sprite):
    def __init__(self, spawn_area):
        super().__init__()
        self.image = POWER_IMG.copy()
        self.rect = self.image.get_rect()

        # 隨機出現在玩家射擊範圍內
        self.rect.center = (
            random.randint(50, WIDTH-50),
            random.randint(200, HEIGHT-200)
        )

        # 隨機挑選效果
        self.type = random.choice([0, 1, 2])
        self.spawn_time = pygame.time.get_ticks()
        self.duration = 10000  # 10 秒消失

    def update(self):
        # 判斷時間 → 自動消失
        now = pygame.time.get_ticks()
        if now - self.spawn_time > self.duration:
            self.kill()

    def apply_effect(self, enemies):
        """被擊中後 → 對敵人生效"""
        now = pygame.time.get_ticks()
        for enemy in enemies:
            # 給每個敵人加上效果（附帶結束時間）
            if self.type == 0:  # 減速
                enemy.speedy *= 0.5
                enemy.effect_end = now + 3000
                enemy.original_speed = getattr(enemy, "original_speed", enemy.speedy * 2)
            elif self.type == 1:  # 停止
                enemy.effect_end = now + 3000
                enemy.original_speed = getattr(enemy, "original_speed", enemy.speedy)
                enemy.speedy = 0
            elif self.type == 2:  # 加速
                enemy.speedy *= 1.5
                enemy.effect_end = now + 2000
                enemy.original_speed = getattr(enemy, "original_speed", enemy.speedy / 1.5)
