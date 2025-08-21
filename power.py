import pygame, random
from config import WIDTH, HEIGHT

POWER_IMG = pygame.image.load("Image/power/power0.png")
POWER_IMG = pygame.transform.scale(POWER_IMG, (30, 30))

class Power(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = POWER_IMG.copy()
        self.rect = self.image.get_rect()

        # 隨機出現在玩家射擊範圍內
        self.rect.center = (
            random.randint(50, WIDTH - 50),
            random.randint(200, HEIGHT - 200)
        )

        # 隨機挑選效果
        self.type = random.choice([0, 1, 2])  # 0=減速, 1=停止, 2=加速
        self.spawn_time = pygame.time.get_ticks()
        self.duration = 10000  # 10 秒消失

    def update(self):
        # 判斷時間 → 自動消失
        now = pygame.time.get_ticks()
        if now - self.spawn_time > self.duration:
            self.kill()

    def apply_effect(self, enemies):
        """被玩家打到後 → 對所有敵人生效"""
        now = pygame.time.get_ticks()
        for enemy in enemies:
            if self.type == 0:  # 減速 3 秒
                enemy.speed_factor = 0.5
                enemy._effect_end = now + 3000
            elif self.type == 1:  # 停止 3 秒
                enemy.speed_factor = 0.0
                enemy._effect_end = now + 3000
            elif self.type == 2:  # 加速 2 秒
                enemy.speed_factor = 1.5
                enemy._effect_end = now + 2000
