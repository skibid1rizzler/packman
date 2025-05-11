import pygame
import random

pygame.init()

# Розміри вікна, підлаштовані під розмір фону
WIDTH, HEIGHT = 610, 378
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("packman")
clock = pygame.time.Clock()

PURPLE = (128, 0, 128)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE = (50, 50, 200)
GREEN = (0, 200, 50)
BLACK = (0, 0, 0)

MENU = "menu"
GAME = "game"
VICTORY = "victory"
RULES = "rules"
DEATH = "death"
game_state = MENU

# Заміни шлях до зображення фону
menu_background = pygame.transform.scale(pygame.image.load("menu_background.png"), (WIDTH, HEIGHT))
game_background = pygame.transform.scale(pygame.image.load("game_background.png"), (WIDTH, HEIGHT))

# Прогрес-бар змінні
progress = 0
progress_max = 100
progress_timer = 0


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.direction = 1

    def update(self, keys):
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.direction = -1
        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.direction = 1
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_s]:
            self.rect.y += self.speed

        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(HEIGHT - self.rect.height, self.rect.y))

        if self.health <= 0:
            global game_state
            game_state = DEATH

    def attack(self):
        attack_rect = pygame.Rect(self.rect.x + (self.direction * 40), self.rect.y - 10, 50, 30)
        for enemy in enemies:
            if attack_rect.colliderect(enemy.rect):
                enemy.take_damage(30)

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, self.rect, border_radius=5)
        health_bar = pygame.Rect(10, 10, 200 * (self.health / self.max_health), 20)
        pygame.draw.rect(surface, GREEN, health_bar)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, is_boss=False):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = random.uniform(1.5, 2.5)
        self.health = 50 if not is_boss else 150
        self.is_boss = is_boss

    def update(self, player):
        dx = player.rect.x - self.rect.x
        dy = player.rect.y - self.rect.y
        dist = max(1, (dx**2 + dy**2) ** 0.5)
        self.rect.x += dx / dist * self.speed
        self.rect.y += dy / dist * self.speed
        if self.rect.colliderect(player.rect):
            player.health -= 0.3

        for other in enemies:
            if other != self:
                dx_enemy = other.rect.x - self.rect.x
                dy_enemy = other.rect.y - self.rect.y
                dist_enemy = max(1, (dx_enemy**2 + dy_enemy**2) ** 0.5)
                if dist_enemy < 50:
                    self.rect.x -= dx_enemy / dist_enemy * 2
                    self.rect.y -= dy_enemy / dist_enemy * 2

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            if self.is_boss:
                global game_state
                game_state = VICTORY
            enemies.remove(self)

    def draw(self, surface):
        pygame.draw.rect(surface, RED, self.rect)


def spawn_enemy():
    x = random.randint(50, WIDTH - 50)
    y = random.randint(50, HEIGHT - 50)
    enemies.append(Enemy(x, y))


class Button:
    def __init__(self, text, x, y, width, height, callback):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.callback = callback

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=5)
        text_surf = pygame.font.Font(None, 24).render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()


def start_game():
    global game_state, player, enemies, progress, progress_timer
    game_state = GAME
    progress = 0
    progress_timer = 0
    player = Player()
    # Зменшуємо кількість ворогів
    enemies = [Enemy(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)) for _ in range(2)]  # 2 вороги замість 3
    enemies.append(Enemy(WIDTH // 2, 50, is_boss=True))  # Бос залишається

def spawn_enemy():
    # Зменшуємо кількість ворогів, які з'являються
    if len(enemies) < 5:  # Обмежуємо кількість ворогів до 5
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 50)
        enemies.append(Enemy(x, y))


def show_rules():
    global game_state
    game_state = RULES


def toggle_fullscreen():
    global screen, WIDTH, HEIGHT
    if pygame.display.get_window_size() == (WIDTH, HEIGHT):
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))


def quit_fullscreen():
    global screen, WIDTH, HEIGHT
    screen = pygame.display.set_mode((WIDTH, HEIGHT))


def show_victory():
    global game_state
    game_state = VICTORY


buttons = [
    Button("Почати Гру", WIDTH // 2 - 80, 160, 160, 40, start_game),
    Button("Правила", WIDTH // 2 - 80, 210, 160, 40, show_rules),
    Button("Fullscreen", WIDTH // 2 - 80, 260, 160, 40, toggle_fullscreen),
    Button("Quit Fullscreen", WIDTH // 2 - 80, 310, 160, 40, quit_fullscreen)
]

# Основний цикл гри
running = True
while running:
    screen.fill(PURPLE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_state == MENU:
            for button in buttons:
                button.handle_event(event)
        if game_state == RULES and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            game_state = MENU

    if game_state == MENU:
        screen.blit(menu_background, (0, 0))  # Використовуємо фонове зображення для меню
        for button in buttons:
            button.draw(screen)
    elif game_state == DEATH:
        screen.fill(PURPLE)
        text = pygame.font.Font(None, 64).render("WASTED", True, RED)
        screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
        pygame.time.delay(2000)
        game_state = MENU
    elif game_state == VICTORY:
        screen.fill(PURPLE)
        text = pygame.font.Font(None, 64).render("MISSION COMPLETE", True, GREEN)
        screen.blit(text, (WIDTH // 2 - 200, HEIGHT // 2 - 50))
        pygame.time.delay(2000)
        game_state = MENU
    elif game_state == RULES:
        screen.fill(PURPLE)
        font = pygame.font.Font(None, 36)
        rule_text = [
            "1. Use WASD to move.",
            "2. Survive and defeat enemies.",
            "3. Complete the progress bar to win.",
            "Press ESC to return to the menu."
        ]
        for i, line in enumerate(rule_text):
            text = font.render(line, True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 100 + i * 40))

    elif game_state == GAME:
        screen.blit(game_background, (0, 0))  # Використовуємо фонове зображення для гри

        # Оновлюємо об'єкти гри
        keys = pygame.key.get_pressed()
        player.update(keys)
        for enemy in enemies:
            enemy.update(player)
        if pygame.mouse.get_pressed()[0]:  # Якщо натискається кнопка миші
            player.attack()

        # Оновлюємо прогрес
        progress_timer += 1
        if progress_timer % 30 == 0:
            progress += 1
            spawn_enemy()

        # Малюємо об'єкти гри
        player.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)

        pygame.draw.rect(screen, WHITE, (10, 40, 200, 20), 2)
        progress_bar = pygame.Rect(10, 40, 200 * (progress / progress_max), 20)
        pygame.draw.rect(screen, GREEN, progress_bar)

        if progress >= progress_max:
            game_state = VICTORY

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
                    
