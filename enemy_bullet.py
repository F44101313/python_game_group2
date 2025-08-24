import pygame
from config import HEIGHT, WIDTH, RED

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed=4, damage=3):
        super().__init__()
        self.image = pygame.Surface((6, 12))
        self.image.fill(RED)  #紅色區分玩家子彈
        self.rect = self.image.get_rect(center=(x, y))
        self.damage = damage

        dx, dy = direction
        length = max((dx**2 + dy**2)**0.5, 1)
        self.speedx = dx/length * speed
        self.speedy = dy/length * speed

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if (self.rect.bottom < 0 or self.rect.top > HEIGHT or
            self.rect.right < 0 or self.rect.left > WIDTH):
            self.kill()