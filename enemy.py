import pygame
import json
from config import RED, GREEN, BOSS_HP

# ---- 路線快取：只讀一次 path.json ----
with open("path.json", "r", encoding="utf-8") as f:
    _path = json.load(f)
PATH_POINTS = [pygame.Vector2(x, y) for (x, y) in _path["points"]]  # 敵人行進路徑的節點
REACH_RADIUS = _path.get("reach_radius", 12)  # 抵達下一個路點的容忍半徑


# ====================================================================
# 敵人基礎類
# ====================================================================
class Enemy(pygame.sprite.Sprite):
    def __init__(self, hp=20, speed=80, type_index=0, castle=None):
        """
        hp: 血量
        speed: 每秒移動的像素（基礎速度）
        type_index: 敵人外觀/類型索引
        castle: 要攻擊的城堡
        """
        super().__init__()
        self.hp = hp
        self.max_hp = hp
        self.base_speed = float(speed)   # 基礎速度，不會變
        self.speed_factor = 1.0          # 道具效果倍率（0 = 停止，0.5 = 減速一半，1.5 = 加速…）
        self._effect_end = 0             # 效果到期時間（毫秒）
        self.type_index = type_index
        self.castle = castle

        # 敵人的外觀 & 碰撞框
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect()

        # 路徑移動狀態
        self.pos = PATH_POINTS[0].copy()   # 從路徑起點開始
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.path_i = 1                    # 下一個要走的節點 index
        self.phase = "path"                # "path" → "to_castle" → "siege"

        # 攻擊參數
        self.siege_interval = 700          # 攻擊間隔（毫秒）
        self._last_swing = 0               # 上次攻擊時間
        self.contact_damage = 5            # 攻擊力

    # --------------------------------------------------------
    def current_speed(self):
        """計算目前的有效移動速度（受道具影響）"""
        return self.base_speed * max(0.0, self.speed_factor)

    def update(self, castle, dt):
        """每幀更新狀態"""
        # 檢查道具效果是否到期 → 重置速度倍率
        if self._effect_end and pygame.time.get_ticks() > self._effect_end:
            self.speed_factor = 1.0
            self._effect_end = 0

        # 根據不同階段做不同動作
        if self.phase == "path":
            self._follow_path_or_switch(dt)       # 沿著路徑走
        elif self.phase == "to_castle":
            self._move_towards_castle(castle, dt) # 直線往城堡走
        else:  # "siege"
            self._do_siege(castle)                # 攻擊城堡

        # 更新位置
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    # --------------------------------------------------------
    def _follow_path_or_switch(self, dt):
        """依序走過 PATH_POINTS，走完就切到攻城模式"""
        if self.path_i >= len(PATH_POINTS):
            self.phase = "to_castle"
            return

        target = PATH_POINTS[self.path_i]
        vec = target - self.pos
        dist = vec.length()

        # 抵達節點 → 換下一個
        if dist <= REACH_RADIUS:
            self.path_i += 1
            if self.path_i >= len(PATH_POINTS):
                self.phase = "to_castle"
            return

        # 還沒到 → 往目標前進
        spd = self.current_speed()
        if dist != 0 and spd > 0:
            self.pos += vec.normalize() * (spd * dt)

    # --------------------------------------------------------
    def _move_towards_castle(self, castle, dt):
        """直線朝城堡移動"""
        if not castle:
            return
        if self.rect.colliderect(castle.rect):  # 碰到城堡
            self.phase = "siege"
            return

        c = pygame.Vector2(castle.rect.centerx, castle.rect.centery)
        vec = c - self.pos
        spd = self.current_speed()
        if vec.length() != 0 and spd > 0:
            self.pos += vec.normalize() * (spd * dt)

        self.rect.center = (int(self.pos.x), int(self.pos.y))
        if self.rect.colliderect(castle.rect):
            self.phase = "siege"

    # --------------------------------------------------------
    def _do_siege(self, castle):
        """持續攻擊城堡"""
        if not castle:
            return
        now = pygame.time.get_ticks()
        if now - self._last_swing >= self.siege_interval:
            self._last_swing = now
            castle.take_damage(self.contact_damage)

    # --------------------------------------------------------
    def draw_hp(self, surface):
        """繪製頭頂血條"""
        pygame.draw.rect(surface, RED, (self.rect.left, self.rect.top - 8, self.rect.width, 5))
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, GREEN, (self.rect.left, self.rect.top - 8, self.rect.width * ratio, 5))


# ====================================================================
# Boss 類（繼承 Enemy）
# ====================================================================
class Boss(Enemy):
    def __init__(self, hp=BOSS_HP, speed=55):
        super().__init__(hp=hp, speed=speed, type_index=0)
        self.image = pygame.Surface((150, 150), pygame.SRCALPHA)  # Boss 比較大
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        self.siege_interval = 500   # 攻擊更快
        self.contact_damage = 10    # 攻擊更痛

    def update(self, castle, dt):
        super().update(castle, dt)  # 直接用 Enemy 的邏輯

    def draw_hp(self, surface):
        """Boss 的血條比較大，放在頭上更高一點"""
        pygame.draw.rect(surface, RED, (self.rect.left, self.rect.top - 20, self.rect.width, 12))
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, GREEN, (self.rect.left, self.rect.top - 20, self.rect.width * ratio, 12))
