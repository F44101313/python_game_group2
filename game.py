import pygame, sys, random
from config import *
from player import Player
from enemy import Enemy, Boss
from bullet import Bullet
from castle import Castle
from view import draw_menu, draw_end_screen, draw_game_screen
from power import Power

# 每關可出現的敵人列表
ENEMY_POOL = {
    1: [1, 2, 3],
    2: [2, 3, 4, 5],
    3: [4, 5, 6]
}

# 對應敵人屬性
ENEMY_STATS = {
    1: {"hp":10,"speed":60,"type_index":0},
    2: {"hp":20,"speed":80,"type_index":1},
    3: {"hp":30,"speed":100,"type_index":2},
    4: {"hp":15,"speed":70,"type_index":3},
    5: {"hp":25,"speed":90,"type_index":4},
    6: {"hp":35,"speed":110,"type_index":5}
}

# ENEMY_REWARD 對應 HP → 金錢
ENEMY_REWARD = {10:5, 20:10, 30:15, 15:7, 25:12, 35:18}

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("雙人合作射擊遊戲")
        self.clock = pygame.time.Clock()
        self.running = True
        Player.shared_money = 0
        self.state = "menu"
        self.level = 1  # 初始關卡

    def new_game(self, restart_level=False):
        if not restart_level:
            self.level = 1
        self.all_sprites = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        # 玩家初始化
        player1 = Player(
            WIDTH-100, HEIGHT-200,
            controls=(pygame.K_DOWN, pygame.K_UP),
            initial_angle=180,
            min_angle=135,
            max_angle=225
        )
        player2 = Player(
            100, 300,
            controls=(pygame.K_w, pygame.K_s),
            initial_angle=0,
            min_angle=-45,
            max_angle=45
        )
        self.players.add(player1, player2)
        self.all_sprites.add(player1, player2)

        # 城堡
        self.castle = Castle()

        # Boss
        self.boss_spawned = False
        self.boss = None
        self.start_ticks = pygame.time.get_ticks()

        # 道具生成冷卻
        self.power_cd_ms = 6000
        self._next_power_at = pygame.time.get_ticks() + 2500

        self.state = "playing"

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.events()
            self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.state == "menu" and event.key == pygame.K_SPACE:
                    self.new_game()
                elif self.state in ["win", "lose"] and event.key == pygame.K_SPACE:
                    if self.state == "win":
                        # 進入下一關
                        self.level += 1
                        if self.level > 3:
                            self.level = 1
                        self.new_game(restart_level=True)
                    else:
                        # 失敗 → 重新開始該關
                        self.new_game(restart_level=True)

    def update(self, dt):
        if self.state != "playing":
            return

        # ---- 生成敵人 ----
        if not self.boss_spawned and random.random() < 0.02:
            enemy_choice = random.choice(ENEMY_POOL[self.level])
            stats = ENEMY_STATS[enemy_choice]
            enemy = Enemy(hp=stats["hp"], speed=stats["speed"], type_index=stats["type_index"])
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

        # ---- 生成 Boss ----
        seconds = (pygame.time.get_ticks() - self.start_ticks) // 1000
        if seconds > 30 and not self.boss_spawned:
            if self.level == 1:
                self.boss = Boss(hp=100, speed=55)
            elif self.level == 2:
                self.boss = Boss(hp=120, speed=60)
            else:
                self.boss = Boss(hp=150, speed=50)
            self.enemies.add(self.boss)
            self.all_sprites.add(self.boss)
            self.boss_spawned = True

        # ---- 生成 / 更新道具 ----
        now = pygame.time.get_ticks()
        if now >= self._next_power_at and not self.castle.is_destroyed():
            self.powerups.add(Power())
            self._next_power_at = now + self.power_cd_ms + random.randint(-1200, 1200)
        self.powerups.update()

        # ---- 玩家更新 ----
        keys = pygame.key.get_pressed()
        #shift_held = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        for player in self.players:
            player.update(self.bullets, self.all_sprites, dt)

        # ---- 敵人更新 ----
        for enemy in self.enemies:
            enemy.update(self.castle, dt)

        # ---- 子彈更新 ----
        self.bullets.update()

        # 子彈打到敵人
        for bullet in list(self.bullets):
            hit_list = pygame.sprite.spritecollide(bullet, self.enemies, False)
            if hit_list:
                bullet.kill()
                for enemy in hit_list:
                    enemy.hp -= bullet.damage
                    if enemy.hp <= 0:
                        Player.shared_money += ENEMY_REWARD.get(getattr(enemy, "max_hp", 20), 10)
                        enemy.kill()

        # 子彈打到道具 → 全體敵人生效
        for bullet in list(self.bullets):
            hits = pygame.sprite.spritecollide(bullet, self.powerups, dokill=True)
            if hits:
                bullet.kill()
                for pu in hits:
                    pu.apply_effect(self.enemies)

        # 升級
        if keys[pygame.K_m]:
            self.players.sprites()[0].upgrade()
        if keys[pygame.K_e]:
            self.players.sprites()[1].upgrade()

        # 勝負判斷
        if self.castle.is_destroyed():
            self.state = "lose"
        elif self.boss_spawned and self.boss not in self.enemies:
            self.state = "win"

    def draw(self):
        if self.state == "menu":
            draw_menu(self.screen)
        elif self.state == "playing":
            draw_game_screen(
                self.screen,
                self.all_sprites,
                self.enemies,
                self.castle,
                self.boss,
                Player.shared_money,
                level=self.level
            )
            # 道具畫在最上層
            self.powerups.draw(self.screen)
        elif self.state in ["win", "lose"]:
            draw_end_screen(self.screen, win=(self.state == "win"))
        pygame.display.flip()
