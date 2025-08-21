import pygame, sys, random
from config import *
from player import Player
from enemy import Enemy, Boss
from bullet import Bullet
from castle import Castle
from power import Power
from view import draw_menu, draw_end_screen, draw_game_screen

# ENEMY_REWARD 對應 HP
ENEMY_REWARD = {10: 5, 20: 10, 30: 15}

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("雙人合作射擊遊戲")
        self.clock = pygame.time.Clock()
        self.running = True
        Player.shared_money = 0
        self.state = "menu"

    def new_game(self):
        self.all_sprites = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powers = pygame.sprite.Group()

        # 玩家初始化
        player1 = Player(
            WIDTH-100, HEIGHT-200,
            controls=(pygame.K_LEFT, pygame.K_RIGHT),
            initial_angle=180,
            min_angle=135,
            max_angle=225
        )
        player2 = Player(
            100, 300,
            controls=(pygame.K_a, pygame.K_d),
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
        self.state = "playing"

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.events()
            self.update()
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
                    self.new_game()

    def update(self):
        if self.state != "playing":
            return

        # 生成敵人
        if not self.boss_spawned and random.random() < 0.02:
            enemy_type = random.choice([
                {"hp": 10, "speed": 1, "type_index": 0},
                {"hp": 20, "speed": 2, "type_index": 1},
                {"hp": 30, "speed": 3, "type_index": 2}
            ])
            enemy = Enemy(hp=enemy_type["hp"], speed=enemy_type["speed"], type_index=enemy_type["type_index"])
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

        # 生成 Boss
        seconds = (pygame.time.get_ticks() - self.start_ticks) // 1000
        if seconds > 30 and not self.boss_spawned:
            self.boss = Boss()
            self.enemies.add(self.boss)
            self.all_sprites.add(self.boss)
            self.boss_spawned = True

        # 隨機生成 power (0.3% 機率)
        if random.random() < 0.003:
            power = Power(self.castle.rect)
            self.powers.add(power)
            self.all_sprites.add(power)

        # 更新玩家
        for player in self.players:
            player.update(self.bullets, self.all_sprites)

        # 更新敵人
        for enemy in self.enemies:
            enemy.update(self.castle)

        # 更新子彈
        self.bullets.update()

        # 更新 power
        self.powers.update()

        # 子彈打中敵人
        for bullet in self.bullets:
            hit_list = pygame.sprite.spritecollide(bullet, self.enemies, False)
            for enemy in hit_list:
                enemy.hp -= bullet.damage
                bullet.kill()
                if enemy.hp <= 0:
                    Player.shared_money += ENEMY_REWARD.get(getattr(enemy, "hp", 20), 10)
                    enemy.kill()

        # 子彈打中道具
        for bullet in self.bullets:
            hit_powers = pygame.sprite.spritecollide(bullet, self.powers, True)
            for power in hit_powers:
                power.apply_effect(self.enemies)
                bullet.kill()

        # 升級
        keys = pygame.key.get_pressed()
        if keys[pygame.K_m]:
            self.players.sprites()[0].upgrade()
        if keys[pygame.K_e]:
            self.players.sprites()[1].upgrade()

        # 判斷勝敗
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
                Player.shared_money
            )
        elif self.state in ["win","lose"]:
            draw_end_screen(self.screen, win=(self.state=="win"))
        pygame.display.flip()
