import pygame
from config import RED, GREEN, CASTLE_HP, WIDTH

class Castle:
    def __init__(self):
        self.hp = CASTLE_HP
        self.max_hp = CASTLE_HP
        # 和 view.py 裡的 CASTLE_IMG(200x200) 對齊
        self.rect = pygame.Rect(WIDTH // 2 - 100, 0, 200, 200)

    def take_damage(self, dmg):
        # 扣血並夾到 0 以上
        self.hp = max(0, self.hp - int(dmg))

    def draw(self, surface, font):
        """
        在城堡『右側』畫直式血條（從下往上變短），再畫文字。
        view.py 會在每幀把 self.rect.topleft 對齊 CASTLE_POS。
        """
        bar_w = 10
        bar_h = self.rect.height

        x = self.rect.right + 6         # 右邊留 6px 間距
        y = self.rect.top

        # 紅色背景條（滿血大小）
        pygame.draw.rect(surface, RED, (x, y, bar_w, bar_h))

        # 綠色目前血量（從下往上填）
        ratio = 0.0 if self.max_hp == 0 else max(0.0, min(1.0, self.hp / self.max_hp))
        fill_h = int(bar_h * ratio)
        pygame.draw.rect(surface, GREEN, (x, y + (bar_h - fill_h), bar_w, fill_h))

        # 文字（放在血條右邊）
        text = font.render(f"{self.hp}/{self.max_hp}", True, (255, 255, 255))
        surface.blit(text, (x + bar_w + 8, self.rect.centery - text.get_height() // 2))

    def is_destroyed(self):
        return self.hp <= 0
