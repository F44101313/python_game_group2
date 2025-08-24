import pygame
import math
from bullet import Bullet
from config import (
    GREEN,
    BULLET_BASE_SPEED, BULLET_BASE_DAMAGE,
    UPGRADE_COST, UPGRADE_SPEED_INC, UPGRADE_DAMAGE_INC
)

# 塔底座圖片（固定，不旋轉）
PLAYER_IMG = pygame.image.load("Image/tower/tower0.png")
PLAYER_IMG = pygame.transform.scale(PLAYER_IMG, (40, 40))

class Player(pygame.sprite.Sprite):
    """
    固定式炮塔
    controls: (left_key, right_key)
    angle：以「向上」為 90 度；限制在 [min_angle, max_angle]
    """
    shared_money = 0  # 全體共用的金錢

    def __init__(self, x, y, controls, initial_angle, min_angle, max_angle):
        super().__init__()
        self.base_image = PLAYER_IMG.copy()
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(x, y))

        # 操作按鍵
        self.controls = controls
        # 角度初始值 & 限制範圍
        self.angle = initial_angle
        self.min_angle = min_angle
        self.max_angle = max_angle

        # 射擊屬性
        self.shoot_delay = 400  # 每發間隔 (毫秒)
        self.last_shot = pygame.time.get_ticks()
        self.bullet_speed = BULLET_BASE_SPEED
        self.bullet_damage = BULLET_BASE_DAMAGE

        # 旋轉速度（度/秒，用 dt 控制）
        self.turn_speed_deg = 180  

        # 視覺：炮管長度 & 顏色
        self.barrel_len = 46
        self.barrel_color = (80, 200, 120)

        # 火光計時器 (毫秒)
        self._flash_timer_ms = 0
        self._flash_max_ms = 60

        # 玩家等級
        self.level = 1
        self.max_level = 5

    # ---- 升級 ----
    def upgrade(self):
        if self.level >= self.max_level:
            print("已達最高等級")
            return

        if Player.shared_money >= UPGRADE_COST:
            Player.shared_money -= UPGRADE_COST
            self.bullet_speed += UPGRADE_SPEED_INC
            self.bullet_damage += UPGRADE_DAMAGE_INC
            self.level += 1
        else:
            print("金錢不足，無法升級")

    # ---- 更新 ----
    def update(self, bullets, all_sprites, dt):
        keys = pygame.key.get_pressed()

        delta_deg = self.turn_speed_deg * dt * 0.2
        if keys[self.controls[0]]:
            self.angle += delta_deg
        if keys[self.controls[1]]:
            self.angle -= delta_deg

        self.angle = max(self.min_angle, min(self.max_angle, self.angle))

        # 自動射擊
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            pos, dirv = self.muzzle_pos()
            bullet = Bullet(pos.x, pos.y, (dirv.x, dirv.y),
                            speed=self.bullet_speed,
                            damage=self.bullet_damage)
            bullets.add(bullet)
            all_sprites.add(bullet)
            self._flash_timer_ms = self._flash_max_ms

        # 火光倒數
        if self._flash_timer_ms > 0:
            self._flash_timer_ms = max(0, self._flash_timer_ms - int(dt * 1000))

    # ---- 砲口座標與方向向量 ----
    def muzzle_pos(self):
        base = pygame.Vector2(self.rect.centerx, self.rect.centery)
        rad = math.radians(self.angle)
        dirv = pygame.Vector2(math.cos(rad), -math.sin(rad))
        muzzle = base + dirv * self.barrel_len
        return muzzle, dirv

    # ---- 繪製炮管 / 瞄準線 / 火光 ----
    def draw_overlay(self, surface):
        base = pygame.Vector2(self.rect.centerx, self.rect.centery)
        muzzle, dirv = self.muzzle_pos()
        tail = base + dirv * 12

        # 炮管
        pygame.draw.line(surface, self.barrel_color, tail, muzzle, 6)

        # 瞄準線
        aim_layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        end = muzzle + dirv * 420
        pygame.draw.line(aim_layer, (255, 255, 200, 120), muzzle, end, 1)
        pygame.draw.circle(aim_layer, (255, 255, 200, 160), (int(end.x), int(end.y)), 3)
        surface.blit(aim_layer, (0, 0))

        # 火光
        if self._flash_timer_ms > 0:
            p1 = muzzle
            p2 = muzzle + dirv.rotate(28) * 12
            p3 = muzzle + dirv.rotate(-28) * 12
            pygame.draw.polygon(surface, (255, 240, 120), (p1, p2, p3))
