import pygame, sys, random
from config import *
from player import Player
from enemy import Enemy, Boss
from bullet import Bullet
from castle import Castle
from view import draw_menu, draw_end_screen, draw_game_screen, draw_story, draw_tutorial
from power import Power

ENEMY_POOL = {1:[1,2,3], 2:[4,5,6], 3:[7,8,9]}
ENEMY_STATS = {
    1: {"hp":10,"speed":100,"type_index":0},
    2: {"hp":30,"speed":80,"type_index":1},
    3: {"hp":20,"speed":90,"type_index":2},
    4: {"hp":20,"speed":120,"type_index":3},
    5: {"hp":45,"speed":90,"type_index":4},
    6: {"hp":35,"speed":110,"type_index":5},
    7: {"hp":25,"speed":130,"type_index":6},
    8: {"hp":55,"speed":90,"type_index":7},
    9: {"hp":45,"speed":120,"type_index":8}
}
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
        self.level = 1
        self.enemy_bullets = pygame.sprite.Group()
        # 玩家升級冷卻
        self._upgrade_cd_ms = 1000
        self._next_upgrade_p1 = 0
        self._next_upgrade_p2 = 0

    def new_game(self, restart_level=False):
        if not restart_level:
            self.level = 1
        self.all_sprites = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()

        player1 = Player(WIDTH-100, HEIGHT-200, (pygame.K_DOWN, pygame.K_UP), 180, 135, 225)
        player2 = Player(100, 300, (pygame.K_w, pygame.K_s), 0, -45, 45)
        self.players.add(player1, player2)
        self.all_sprites.add(player1, player2)

        self.castle = Castle()
        self.boss_spawned = False
        self.boss = None
        self.start_ticks = pygame.time.get_ticks()
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
                if self.state in ["win", "lose"]:
                    if event.key == pygame.K_SPACE:
                        if self.state == "win":
                            self.level += 1
                            if self.level > 3:
                                self.level = 1
                            self.new_game(restart_level=True)
                        else:
                            self.new_game(restart_level=True)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if self.state == "menu":
                    buttons = draw_menu(self.screen)  # 取得按鈕矩形
                    if buttons["start"].collidepoint(mx, my):
                        self.state = "story"
                    elif buttons["howto"].collidepoint(mx, my):
                        self.state = "tutoriel"
                elif self.state == "story":
                    buttons = draw_story(self.screen)
                    if buttons["go"].collidepoint(mx, my):
                        self.new_game()  # 開始第一關
                elif self.state == "tutoriel":
                    buttons = draw_tutorial(self.screen)
                    if buttons["ok"].collidepoint(mx, my):
                        self.state = "menu"

    def update(self, dt):
        if self.state != "playing":
            return

        now = pygame.time.get_ticks()
        # 生成敵人 (降低出場率)
        if not self.boss_spawned and random.random() < 0.01:
            enemy_choice = random.choice(ENEMY_POOL[self.level])
            stats = ENEMY_STATS[enemy_choice]
            enemy = Enemy(hp=stats["hp"], speed=stats["speed"], type_index=stats["type_index"])
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

        # 生成 Boss
        seconds = (now - self.start_ticks) // 1000
        if seconds > 30 and not self.boss_spawned:
            hp_map = {1:100, 2:120, 3:150}
            speed_map = {1:55, 2:60, 3:50}
            self.boss = Boss(hp=hp_map[self.level], speed=speed_map[self.level])
            self.enemies.add(self.boss)
            self.all_sprites.add(self.boss)
            self.boss_spawned = True

        # 道具
        if now >= self._next_power_at and not self.castle.is_destroyed():
            self.powerups.add(Power())
            self._next_power_at = now + self.power_cd_ms + random.randint(-1200,1200)
        self.powerups.update()

        # 玩家更新
        for player in self.players:
            player.update(self.bullets, self.all_sprites, dt)

        # 升級冷卻
        keys = pygame.key.get_pressed()
        if keys[pygame.K_m] and now >= self._next_upgrade_p1:
            self.players.sprites()[0].upgrade()
            self._next_upgrade_p1 = now + self._upgrade_cd_ms
        if keys[pygame.K_e] and now >= self._next_upgrade_p2:
            self.players.sprites()[1].upgrade()
            self._next_upgrade_p2 = now + self._upgrade_cd_ms

        # 敵人更新
        for enemy in self.enemies:
            enemy.update(self.castle, dt)
            if getattr(enemy,"type_index",-1) in [2,5,8]:
                if not hasattr(enemy, "_last_shot_time"):
                    enemy._last_shot_time = 0
                if now - enemy._last_shot_time >= 1000:
                    enemy._last_shot_time = now
                    muzzle = pygame.Vector2(enemy.rect.center)
                    castle_center = pygame.Vector2(self.castle.rect.center)
                    dirv = castle_center - muzzle
                    if dirv.length() != 0:
                        dirv = dirv.normalize()
                    bullet = Bullet(muzzle.x, muzzle.y, (dirv.x, dirv.y), speed=4, damage=2)
                    self.enemy_bullets.add(bullet)
                    self.all_sprites.add(bullet)

        # 更新子彈
        self.bullets.update()
        self.enemy_bullets.update()

        # 玩家子彈打到敵人
        for bullet in list(self.bullets):
            hit_list = pygame.sprite.spritecollide(bullet, self.enemies, False)
            if hit_list:
                bullet.kill()
                for enemy in hit_list:
                    enemy.hp -= bullet.damage
                    if enemy.hp <= 0:
                        Player.shared_money += ENEMY_REWARD.get(getattr(enemy,"max_hp",20),10)
                        enemy.kill()

        # 敵人子彈打城堡
        for bullet in list(self.enemy_bullets):
            if bullet.rect.colliderect(self.castle.rect):
                self.castle.take_damage(bullet.damage)
                bullet.kill()

        # 玩家子彈打道具
        for bullet in list(self.bullets):
            hits = pygame.sprite.spritecollide(bullet, self.powerups, dokill=True)
            if hits:
                bullet.kill()
                for pu in hits:
                    pu.apply_effect(self.enemies)

        # 勝負判斷
        if self.castle.is_destroyed():
            self.state = "lose"
        elif self.boss_spawned and self.boss not in self.enemies:
            self.state = "win"

    def draw(self):
        if self.state == "menu":
            draw_menu(self.screen)
        elif self.state == "story":
            draw_story(self.screen)
        elif self.state == "tutoriel":
            draw_tutorial(self.screen)
        elif self.state == "playing":
            draw_game_screen(
                self.screen,
                self.all_sprites,
                self.enemies,
                self.castle,
                self.boss,
                Player.shared_money,
                level=self.level,
                enemy_bullets=self.enemy_bullets,
            )
            self.powerups.draw(self.screen)
            # 顯示玩家等級
            p1, p2 = self.players.sprites()
            lv1_text = font.render(f"Player 1 lv.{p1.level}", True, WHITE)
            lv2_text = font.render(f"Player 2 lv.{p2.level}", True, WHITE)
            self.screen.blit(lv1_text, (10, 35))
            self.screen.blit(lv2_text, (10, 60))
        elif self.state in ["win", "lose"]:
            draw_end_screen(self.screen, win=(self.state == "win"))

        pygame.display.flip()
