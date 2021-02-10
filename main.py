import pygame
import sys

pygame.init()
pygame.display.set_caption('Platformer - by Jesus')

SIZE = WIDTH, HEIGHT = 1000, 1000  # Window size
ARENA = pygame.display.set_mode(SIZE)
TILE_SIDE = 25
FPS = 80
clock = pygame.time.Clock()

# Colors:
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


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
        self.jumpCount = 2  # Max of jumps is 2 (double jump)
        self.dir = 1  # 1 when looking to the right; -1 when looking to the left

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

    def move(self, tiles):
        dx = 0
        dy = 0
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
            if tile.rect.colliderect(
                    pygame.Rect(self.x + dx, self.y - self.height, self.width, self.height)):
                dx = 0

            # TOP/BOTTOM COLLISIONS
            if tile.rect.colliderect(pygame.Rect(self.x, self.y - self.height + dy, self.width, self.height)):
                if self.vel_y < 0:  # Top collision if it's jumping
                    dy = tile.rect.bottom - self.y + self.height
                    self.vel_y = 0
                elif self.vel_y >= 0:  # Bottom collision if it's falling
                    dy = tile.rect.top - self.y
                    self.jumpCount = 2

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


def draw_game(player, tiles):
    ARENA.blit(pygame.image.load("sprites/bg.jpg").convert_alpha(), (0, 0))
    player.draw()

    for tile in tiles:
        tile.draw_tile()

    pygame.display.update()


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

    return tiles


def main():
    running = True

    player = Player(TILE_SIDE*2, HEIGHT - TILE_SIDE)
    tiles = get_tiles_from_map("map.txt")

    while running:
        clock.tick(FPS)
        draw_game(player, tiles)

        player.move(tiles)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()


main()
