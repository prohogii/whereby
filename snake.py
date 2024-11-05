import pygame
import sys
import random
import math

# Инициализация Pygame
pygame.init()

# Параметры экрана
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("DOOM на Python")

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Игрок
class Player:
    def __init__(self, pos):
        self.pos = pos
        self.size = 50
        self.last_direction = [0, 0]

    def move(self, dx, dy):
        self.pos[0] = max(0, min(WIDTH - self.size, self.pos[0] + dx))
        self.pos[1] = max(0, min(HEIGHT - self.size, self.pos[1] + dy))

# Враг
class Enemy:
    def __init__(self, pos, enemy_type, hits, enemy_id):
        self.pos = pos
        self.size = 50
        self.type = enemy_type
        self.hits = hits
        self.id = enemy_id
        self.direction = [random.choice([-1, 1]), random.choice([-1, 1])]
        self.speed = random.uniform(1, 3)

    def move(self):
        self.pos[0] += self.direction[0] * self.speed
        self.pos[1] += self.direction[1] * self.speed
        if self.pos[0] <= 0 or self.pos[0] >= WIDTH - self.size:
            self.direction[0] *= -1
        if self.pos[1] <= 0 or self.pos[1] >= HEIGHT - self.size:
            self.direction[1] *= -1

# Пуля
class Bullet:
    def __init__(self, pos, direction):
        self.pos = pos
        self.direction = direction
        self.size = 5
        self.speed = 10

    def update(self):
        self.pos[0] += self.direction[0] * self.speed
        self.pos[1] += self.direction[1] * self.speed

# Инициализация шрифта
font = pygame.font.SysFont(None, 48)

# Функция для отображения текста
def draw_text(text, color, pos):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)

# Функция для рисования человечка
def draw_pixel_person(x, y, color):
    pygame.draw.rect(screen, color, (x + 20, y + 10, 10, 30))
    pygame.draw.rect(screen, color, (x + 15, y, 20, 10))
    pygame.draw.rect(screen, color, (x, y + 10, 20, 5))
    pygame.draw.rect(screen, color, (x + 30, y + 10, 5, 5))
    pygame.draw.rect(screen, color, (x + 20, y + 40, 5, 10))
    pygame.draw.rect(screen, color, (x + 25, y + 40, 5, 10))

# Функция для спавна врага
enemy_id_counter = 0

def spawn_enemy():
    global enemy_id_counter
    while True:
        x = random.randint(0, WIDTH - 50)
        y = random.randint(0, HEIGHT - 50)
        if math.sqrt((x - player.pos[0]) ** 2 + (y - player.pos[1]) ** 2) >= 3 * player.size:
            enemy_id_counter += 1
            type_choice = random.random()
            enemy_type = 'red' if type_choice < 0.33 else 'blue' if type_choice < 0.66 else 'green'
            hits = 1 if enemy_type == 'red' else 2 if enemy_type == 'blue' else 4
            return Enemy([x, y], enemy_type, hits, enemy_id_counter)

# Проверка столкновения
def check_collision(rect1, rect2):
    return pygame.Rect(rect1).colliderect(pygame.Rect(rect2))

# Сохранение рекорда
def save_high_score(score):
    with open("high_score.txt", "w") as f:
        f.write(str(score))

# Загрузка рекорда
def load_high_score():
    try:
        with open("high_score.txt", "r") as f:
            return int(f.read())
    except (FileNotFoundError, ValueError):
        return 0

# Основной игровой цикл
player = Player([WIDTH // 2, HEIGHT // 2])
bullets = []
enemies = [spawn_enemy() for _ in range(1)]
enemy_bullets = []
enemy_bullet_time = {}
game_over = False
paused = False
enemy_count = 0
damage_multiplier = 1
score = 0
high_score = load_high_score()  # Загрузка рекорда
game_started = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key in [pygame.K_p, pygame.K_z]:
                paused = not paused
            if not paused:
                if event.key == pygame.K_RETURN and not game_started:
                    game_started = True
                if event.key == pygame.K_SPACE and game_started and not game_over:
                    if player.last_direction != [0, 0]:
                        bullets.append(Bullet([player.pos[0] + player.size // 2, player.pos[1]], player.last_direction))
                if game_over and event.key in [pygame.K_r, pygame.K_z]:
                    if score > high_score:  # Сохранение рекорда
                        save_high_score(score)
                        high_score = score  # Обновляем значение рекорда в памяти

                    player.pos = [WIDTH // 2, HEIGHT // 2]
                    bullets.clear()
                    enemies = [spawn_enemy() for _ in range(1)]
                    enemy_count = 0
                    damage_multiplier = 1
                    enemy_bullets.clear()
                    game_over = False
                    score = 0

    if not paused:
        if game_started and not game_over:
            keys = pygame.key.get_pressed()
            moved = False
            if keys[pygame.K_LEFT]:
                player.move(-5, 0)
                player.last_direction = [-1, 0]
                moved = True
            if keys[pygame.K_RIGHT]:
                player.move(5, 0)
                player.last_direction = [1, 0]
                moved = True
            if keys[pygame.K_UP]:
                player.move(0, -5)
                player.last_direction = [0, -1]
                moved = True
            if keys[pygame.K_DOWN]:
                player.move(0, 5)
                player.last_direction = [0, 1]
                moved = True

            for bullet in bullets:
                bullet.update()

            bullets = [bullet for bullet in bullets if 0 < bullet.pos[0] < WIDTH and 0 < bullet.pos[1] < HEIGHT]

            current_time = pygame.time.get_ticks()

            for enemy in enemies:
                enemy.move()

                if enemy.id not in enemy_bullet_time:
                    enemy_bullet_time[enemy.id] = current_time

                if current_time - enemy_bullet_time[enemy.id] > 1000:
                    enemy_bullet_time[enemy.id] = current_time
                    direction = [random.choice([-1, 1]), random.choice([-1, 1])]
                    enemy_bullets.append(Bullet([enemy.pos[0] + enemy.size // 2, enemy.pos[1] + enemy.size // 2], direction))

                if check_collision((player.pos[0], player.pos[1], player.size, player.size), (enemy.pos[0], enemy.pos[1], enemy.size, enemy.size)):
                    game_over = True

                for bullet in bullets:
                    if check_collision((bullet.pos[0], bullet.pos[1], bullet.size, bullet.size), (enemy.pos[0], enemy.pos[1], enemy.size, enemy.size)):
                        enemy.hits -= damage_multiplier
                        bullets.remove(bullet)
                        if enemy.hits <= 0:
                            enemy_count += 1
                            if enemy.type == 'red':
                                score += 1
                            elif enemy.type == 'blue':
                                score += 2
                            elif enemy.type == 'green':
                                score += 4
                            enemies.remove(enemy)
                            enemies.append(spawn_enemy())
                            if enemy_count % 5 == 0:
                                enemies.append(spawn_enemy())
                        break

            for enemy_bullet in enemy_bullets:
                enemy_bullet.update()

            enemy_bullets = [eb for eb in enemy_bullets if 0 < eb.pos[0] < WIDTH and 0 < eb.pos[1] < HEIGHT]

            for enemy_bullet in enemy_bullets:
                if check_collision((enemy_bullet.pos[0], enemy_bullet.pos[1], enemy_bullet.size, enemy_bullet.size), (player.pos[0], player.pos[1], player.size, player.size)):
                    game_over = True

        # Обновление экрана
        screen.fill(BLACK)

        if not game_started:
            draw_text("Press Enter to Start", WHITE, (WIDTH // 4, HEIGHT // 3))
            draw_text("Controls:", WHITE, (WIDTH // 4, HEIGHT // 2))
            draw_text("Arrow keys to move", WHITE, (WIDTH // 4, HEIGHT // 2 + 40))
            draw_text("Space to shoot", WHITE, (WIDTH // 4, HEIGHT // 2 + 80))
            draw_text("Press ESC to exit", WHITE, (WIDTH // 4, HEIGHT // 2 + 120))
        else:
            # Рисуем игрока
            draw_pixel_person(player.pos[0], player.pos[1], WHITE)

            # Рисуем пули игрока
            for bullet in bullets:
                pygame.draw.rect(screen, WHITE, (*bullet.pos, bullet.size, bullet.size))

            # Рисуем врагов
            for enemy in enemies:
                color = RED if enemy.type == 'red' else BLUE if enemy.type == 'blue' else GREEN
                draw_pixel_person(enemy.pos[0], enemy.pos[1], color)

            # Рисуем пули врагов
            for enemy_bullet in enemy_bullets:
                pygame.draw.rect(screen, RED, (*enemy_bullet.pos, enemy_bullet.size, enemy_bullet.size))

            # Отображение состояния игры
            if game_over:
                draw_text("Game Over! Press R to restart", RED, (WIDTH // 6, HEIGHT // 2))
            elif paused:
                draw_text("Paused! Press P to resume", WHITE, (WIDTH // 6, HEIGHT // 2))

            # Отображение счета и количества убийств на разных строках
            draw_text(f"Killed: {enemy_count}", WHITE, (10, 10))
            draw_text(f"Score: {score}", WHITE, (10, 60))
            draw_text(f"High Score: {high_score}", WHITE, (10, HEIGHT - 60))  # Отображение рекорда в левом нижнем углу

        pygame.display.flip()
        pygame.time.delay(30)

pygame.quit()
