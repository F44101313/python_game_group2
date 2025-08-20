import pygame
from config import WHITE, HEIGHT, WIDTH

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed=7, damage=5):
        super().__init__()
        self.image = pygame.Surface((6, 12))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))
        self.damage = damage

        dx, dy = direction
        length = max((dx**2 + dy**2) ** 0.5, 1)
        self.speedx = dx / length * speed
        self.speedy = dy / length * speed

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if (self.rect.bottom < 0 or self.rect.top > HEIGHT or
            self.rect.right < 0 or self.rect.left > WIDTH):
            self.kill()