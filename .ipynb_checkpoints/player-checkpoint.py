import pygame
import math
from bullet import Bullet
from config import GREEN, BULLET_BASE_SPEED, BULLET_BASE_DAMAGE, UPGRADE_COST, UPGRADE_SPEED_INC, UPGRADE_DAMAGE_INC

PLAYER_IMG = pygame.image.load("Image/tower/tower0.png")
PLAYER_IMG = pygame.transform.scale(PLAYER_IMG, (40, 40))

class Player(pygame.sprite.Sprite):
    shared_money = 0

    def __init__(self, x, y, controls, initial_angle, min_angle, max_angle):
        super().__init__()
        self.image = PLAYER_IMG.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.controls = controls
        self.angle = initial_angle
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 400
        self.bullet_speed = BULLET_BASE_SPEED
        self.bullet_damage = BULLET_BASE_DAMAGE
        self.angle_step = 2  # 每次按鍵旋轉角度

    def upgrade(self):
        if Player.shared_money >= UPGRADE_COST:
            Player.shared_money -= UPGRADE_COST
            self.bullet_speed += UPGRADE_SPEED_INC
            self.bullet_damage += UPGRADE_DAMAGE_INC
        else:
            print("金錢不足，無法升級")

    def update(self, bullets, all_sprites):
        keys = pygame.key.get_pressed()

        # 角度調整
        if keys[self.controls[0]]:
            self.angle += self.angle_step
            if self.angle > self.max_angle:
                self.angle = self.max_angle
        elif keys[self.controls[1]]:
            self.angle -= self.angle_step
            if self.angle < self.min_angle:
                self.angle = self.min_angle

        # 計算射擊方向向量
        rad = math.radians(self.angle)
        dx = math.cos(rad)
        dy = -math.sin(rad)  # y向下，負值為上

        # 自動射擊
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(
                self.rect.centerx,
                self.rect.centery,
                (dx, dy),
                speed=self.bullet_speed,
                damage=self.bullet_damage
            )
            bullets.add(bullet)
            all_sprites.add(bullet)