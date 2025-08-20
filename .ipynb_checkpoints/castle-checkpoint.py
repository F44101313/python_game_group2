import pygame
from config import RED, GREEN, CASTLE_HP, WIDTH

class Castle:
    def __init__(self):
        self.hp = CASTLE_HP
        self.max_hp = CASTLE_HP
        self.rect = pygame.Rect(WIDTH//2 - 75, 0, 150, 150)

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp < 0:
            self.hp = 0

    def draw(self, surface, font):
        # 血條在主堡上方
        pygame.draw.rect(surface, RED, (self.rect.left, self.rect.top-15, self.rect.width, 10))
        ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, GREEN, (self.rect.left, self.rect.top-15, self.rect.width*ratio, 10))
        text = font.render("Castle HP", True, (255, 255, 255))
        surface.blit(text, (self.rect.centerx - text.get_width()//2, self.rect.top-35))

    def is_destroyed(self):
        return self.hp <= 0