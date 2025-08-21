import pygame
import random
from config import RED, GREEN, BOSS_HP, WIDTH, HEIGHT

class Enemy(pygame.sprite.Sprite):
    def __init__(self, hp=20, speed=2, type_index=0, castle=None):
        super().__init__()
        self.hp = hp
        self.max_hp = hp
        self.speedy = speed
        self.base_speed = speed  # 原始速度
        self.type_index = type_index
        self.castle = castle  

        # 效果控制
        self.effect_end = 0
        self.original_speed = speed  

        # 生成位置：隨機在主堡範圍內
        if castle:
            self.rect = pygame.Rect(
                random.randint(castle.rect.left, castle.rect.right - 40),
                HEIGHT + 20, 40, 40
            )
        else:
            self.rect = pygame.Rect(random.randint(50, WIDTH-50), HEIGHT+20, 40, 40)

        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))

    def update(self, castle):
        # 效果檢查
        now = pygame.time.get_ticks()
        if self.effect_end and now > self.effect_end:
            self.speedy = self.original_speed
            self.effect_end = 0

        # 移動
        self.rect.y -= self.speedy
        if self.rect.bottom < castle.rect.bottom:
            castle.take_damage(5)
            self.kill()

    def draw_hp(self, surface):
        pygame.draw.rect(surface, RED, (self.rect.left, self.rect.top-8, self.rect.width, 5))
        ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, GREEN, (self.rect.left, self.rect.top-8, self.rect.width*ratio, 5))


class Boss(Enemy):
    def __init__(self):
        super().__init__(hp=BOSS_HP, speed=3, type_index=0)
        self.rect = pygame.Rect(WIDTH//2 - 75, HEIGHT-150, 150, 150)
        self.image = pygame.Surface((150, 150), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        self.last_attack = pygame.time.get_ticks()
        self.attack_delay = 500  # 0.5秒攻擊

    def update(self, castle):
        # 效果檢查
        now = pygame.time.get_ticks()
        if self.effect_end and now > self.effect_end:
            self.speedy = self.original_speed
            self.effect_end = 0

        stop_y = castle.rect.bottom + 10
        if self.rect.bottom > stop_y:
            self.rect.y -= self.speedy
        else:
            if now - self.last_attack >= self.attack_delay:
                castle.take_damage(10)
                self.last_attack = now

    def draw_hp(self, surface):
        pygame.draw.rect(surface, RED, (self.rect.left, self.rect.top-20, self.rect.width, 12))
        ratio = self.hp / BOSS_HP
        pygame.draw.rect(surface, GREEN, (self.rect.left, self.rect.top-20, self.rect.width*ratio, 12))
