import pygame, os

# 預先載入爆炸圖
EXPLODE_FRAMES = [pygame.image.load(f"Image/animation/explode{i}.png") for i in range(1, 10)]
EXPLODE_FRAMES = [pygame.transform.scale(img, (50, 50)) for img in EXPLODE_FRAMES]  # 調整大小

class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos, size=50, duration=400):
        super().__init__()
        self.frames = [pygame.transform.scale(img, (size, size)) for img in EXPLODE_FRAMES]
        self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=pos)
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.frame_time = duration / len(self.frames)

    def update(self):
        now = pygame.time.get_ticks()
        elapsed = now - self.start_time
        self.index = int(elapsed / self.frame_time)
        if self.index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[self.index]