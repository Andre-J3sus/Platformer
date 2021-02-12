import pygame
import sys

pygame.init()
pygame.display.set_caption('Platformer - by Jesus')

SIZE = WIDTH, HEIGHT = 1000, 1000  # Window size
ARENA = pygame.display.set_mode(SIZE)
TILE_SIDE = 25
starting_pos = TILE_SIDE * 2, HEIGHT - TILE_SIDE
FPS = 45
clock = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf', 28)

# Colors:
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Loading images:
heart_img = pygame.image.load("sprites/heart.png").convert_alpha()
bg_img = pygame.image.load("sprites/bg.jpg").convert_alpha()
jelly_img = pygame.image.load("sprites/jelly_enemy_left.png").convert_alpha()
ghost_img = pygame.image.load("sprites/ghost.png").convert_alpha()


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.images_right = []
        self.images_left = []
        self.index = 0  # Index of the image(related to animation)
        self.counter = 0  # Related to the walk animation cooldown
        for img in range(3):  # adding images
            img_right = pygame.image.load(f"sprites/player_right{img}.png")
            img_right = pygame.transform.scale(img_right, (24, 50))
            img_left = pygame.transform.flip(img_right, True, False)  # Flip the image to create a "walking left" image
            self.images_left.append(img_left)
            self.images_right.append(img_right)
        self.img = self.images_right[self.index]  # First image(looking right)
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.rect = pygame.Rect(self.x, self.y - self.height, self.width, self.height)
        self.dx = 8
        self.vel_y = 0  # Jump constant
        self.isJump = False  # True when starts a jump
        self.jumpCount = 1  # Max of jumps is 1 (single jump)
        self.dir = 1  # 1 when looking to the right; -1 when looking to the left
        self.health = 3
        self.xp = 0

    def draw(self):
        walk_cooldown = 5

        # Animation control
        if self.counter > walk_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images_right):
                self.index = 0
            if self.dir == 1:
                self.img = self.images_right[self.index]
            if self.dir == -1:
                self.img = self.images_left[self.index]

        # Drawing the player
        ARENA.blit(self.img, (self.x, self.y - self.height, self.width, self.height))

    def move(self, tiles, enemies):
        dx = 0
        dy = 0
        if self.img == ghost_img:  # When the player is dead
            if self.y + self.height < 0:
                sys.exit()
            else:
                dy = -5  #
        else:

            keys = pygame.key.get_pressed()

            # KEYS PRESSED
            if keys[pygame.K_LEFT] and self.x > self.dx:  # LEFT -> WALK TO THE LEFT
                dx -= self.dx
                self.dir = -1
                self.counter += 1
            if keys[pygame.K_RIGHT] and self.x + self.width + self.dx < WIDTH:  # RIGHT -> WALK TO THE RIGHT
                dx += self.dx
                self.dir = 1
                self.counter += 1
            if keys[pygame.K_SPACE] and not self.isJump and self.jumpCount > 0:  # SPACE -> JUMPS IF ISN'T JUMPING
                self.vel_y = -15
                self.isJump = True
                self.jumpCount -= 1

            # KEYS NOT PRESSED
            if not keys[pygame.K_SPACE]:  # WHEN RELEASES THE SPACE KEY -> ISN'T JUMPING
                self.isJump = False
            if not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:  # WHEN RELEASES THE LEFT/RIGHT KEYS:
                self.counter = 0  # Counter is reset
                self.index = 0  # Index is reset
                if self.dir == 1:  # If we looking to the right, the player stands still, looking to the right
                    self.img = self.images_right[self.index]
                if self.dir == -1:  # If we looking to the left, the player stands still, looking to the left
                    self.img = self.images_left[self.index]

            # "GRAVITY"
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10  # Never exceeds the value of 10 -> it does not go up infinitely
            dy += self.vel_y

            # CHECK FOR COLLISIONS
            for tile in tiles:
                # SIDE COLLISION
                if tile.rect.colliderect(pygame.Rect(self.x + dx, self.y - self.height, self.width, self.height)):
                    if tile.type == "lava":
                        self.x, self.y = starting_pos[0], starting_pos[1]
                    else:
                        dx = 0

                # TOP/BOTTOM COLLISIONS
                if tile.rect.colliderect(pygame.Rect(self.x, self.y - self.height + dy, self.width, self.height)):
                    if tile.type == "lava":
                        self.x, self.y = starting_pos[0], starting_pos[1]
                        self.health -= 1
                    else:
                        if self.vel_y < 0:  # Top collision if it's jumping
                            dy = tile.rect.bottom - self.y + self.height
                            self.vel_y = 0
                        elif self.vel_y >= 0:  # Bottom collision if it's falling
                            dy = tile.rect.top - self.y
                            self.jumpCount = 1

            for enemy in enemies:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                # SIDES COLLISION
                if enemy_rect.colliderect(pygame.Rect(self.x + dx, self.y - self.height, self.width, self.height)):
                    self.health -= 1
                    dx = 0
                    self.x, self.y = starting_pos[0], starting_pos[1]

                # BOTTOM COLLISION
                if enemy_rect.colliderect(pygame.Rect(self.x, self.y - self.height + dy, self.width, self.height)):
                    if self.vel_y >= 0:  # Bottom collision if it's falling
                        dy = enemy_rect.top - self.y
                        self.vel_y = -15
                        self.jumpCount = 1
                        enemy.health -= 1
                        self.xp += 5

            # Collision with the "roof"
            if self.y - self.height + dy < 0:
                dy = 0 - self.y + self.height

        # UPDATING COORDINATES
        self.x += dx
        self.y += dy


class Tile:
    def __init__(self, x, y, type_of_tile):
        self.x = x
        self.y = y
        self.type = type_of_tile
        img = pygame.image.load("sprites/{}.png".format(self.type)).convert_alpha()
        self.img = pygame.transform.scale(img, (25, 25))
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.rect = pygame.Rect(self.x, self.y, TILE_SIDE, TILE_SIDE)

    def draw_tile(self):
        ARENA.blit(self.img, (self.x, self.y, self.width, self.height))


class Enemy:
    def __init__(self, x, y, health):
        self.img_left = pygame.transform.scale(jelly_img, (28, 24))
        self.img_right = pygame.transform.flip(self.img_left, True, False)
        self.rect = self.img_right.get_rect()
        self.x = x
        self.y = y
        self.dx = 2
        self.dir = -1
        self.width = jelly_img.get_width()
        self.height = jelly_img.get_height()
        self.move_counter = 0
        self.health = health

    def draw(self):
        if self.dir == 1:
            img = self.img_right
        else:
            img = self.img_left

        ARENA.blit(img, (self.x, self.y + 4))

    def move(self, tiles):
        dx = 0
        dy = 0

        dx -= self.dx
        self.move_counter += 1
        if self.move_counter > 25:  # Move 3 blocks and change direction
            self.dir = -self.dir
            self.dx = -self.dx
            self.move_counter *= -1

        # CHECK FOR COLLISIONS
        for tile in tiles:
            # SIDE COLLISION
            if tile.rect.colliderect(pygame.Rect(self.x + dx, self.y, self.width, self.height)):

                self.move_counter = -25

                if tile.type == "lava":
                    self.x, self.y = starting_pos[0], starting_pos[1]
                else:
                    dx = 0
                    self.dx = -self.dx
                    self.dir = -self.dir

            # TOP/BOTTOM COLLISIONS
            if tile.rect.colliderect(pygame.Rect(self.x, self.y - self.height + dy, self.width, self.height)):
                # Bottom collision if it's falling
                dy = tile.rect.top - self.y + self.height

        # UPDATING COORDINATES
        self.x += dx
        self.y += dy


def draw_game(player, tiles, enemies):
    ARENA.blit(bg_img, (0, 0))
    player.draw()

    for tile in tiles:
        tile.draw_tile()

    for enemy in enemies:
        enemy.draw()

    heart = pygame.transform.scale(heart_img, (31, 30))
    for life in range(player.health):
        ARENA.blit(heart, (TILE_SIDE + life * (heart.get_width() + 5), 950))

    text = font.render(f'XP: {player.xp}', True, WHITE)
    ARENA.blit(text, (2 * TILE_SIDE + 3 * (heart.get_width() + 5), 950))

    pygame.display.update()


def update_game(player, tiles, enemies):
    player.move(tiles, enemies)
    if player.health <= 0:
        player.img = ghost_img

    for enemy in enemies:
        enemy.move(tiles)
        if enemy.health <= 0:
            enemies.remove(enemy)


def get_tiles_from_map(map1):
    file = open(str(map1), "r")
    tiles = []
    lines = file.readlines()

    for line in range(0, len(lines)):
        for col in range(0, len(lines[line])):
            if lines[line][col] == "G":
                tiles.append(Tile(col * TILE_SIDE, line * TILE_SIDE, "grass"))
            if lines[line][col] == "D":
                tiles.append(Tile(col * TILE_SIDE, line * TILE_SIDE, "dirt"))
            if lines[line][col] == "F":
                tiles.append(Tile(col * TILE_SIDE, line * TILE_SIDE, "platform"))
            if lines[line][col] == "L":
                tiles.append(Tile(col * TILE_SIDE, line * TILE_SIDE, "lava"))

    return tiles


def get_enemies_from_map(map1):
    file = open(str(map1), "r")
    enemies = []
    lines = file.readlines()

    for line in range(0, len(lines)):
        for col in range(0, len(lines[line])):
            if lines[line][col] == "B":
                enemies.append(Enemy(col * TILE_SIDE, line * TILE_SIDE, 1))

    return enemies


def main():
    running = True

    player = Player(starting_pos[0], starting_pos[1])
    tiles = get_tiles_from_map("map.txt")
    enemies = get_enemies_from_map("map.txt")

    while running:
        clock.tick(FPS)

        update_game(player, tiles, enemies)

        draw_game(player, tiles, enemies)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()


main()
