import pygame

pygame.init()

# Game constants:
SIZE = WIDTH, HEIGHT = 1000, 1000  # Window size
ARENA = pygame.display.set_mode(SIZE)
TILE_SIDE = 25
starting_pos = TILE_SIDE * 2, HEIGHT - TILE_SIDE
MENU = True
WIN = False
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
play_button_img = pygame.image.load("sprites/play.PNG").convert_alpha()
exit_button_img = pygame.image.load("sprites/exit.PNG").convert_alpha()
game_name_img = pygame.image.load("sprites/name.png").convert_alpha()
grass_img = pygame.image.load("sprites/grass.png").convert_alpha()
dirt_img = pygame.image.load("sprites/dirt.png").convert_alpha()
platform_img = pygame.image.load("sprites/platform.png").convert_alpha()
lava_img = pygame.image.load("sprites/lava.png").convert_alpha()
door_img = pygame.image.load("sprites/door.png").convert_alpha()

# Window caption and icon
pygame.display.set_caption('Attack in the Garden - by Jesus')
pygame.display.set_icon(jelly_img)


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.images_right = []
        self.images_left = []
        self.index = 0  # Index of the image(related to animation)
        self.counter = 0  # Related to the walk animation cooldown
        for img in range(3):  # adding images
            img_right = pygame.image.load(f"sprites/player_right{img}.png").convert_alpha()
            img_right = pygame.transform.scale(img_right, (24, 50)).convert_alpha()
            # Flip the image to create a "walking left" image
            img_left = pygame.transform.flip(img_right, True, False).convert_alpha()
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

    def move(self, tiles, entities):
        global WIN, MENU
        dx = 0
        dy = 0
        if self.img == ghost_img:  # When the player is dead
            if self.y + self.height < 0:
                return True
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
                        self.health -= 1
                        if self.health > 0:
                            self.x, self.y = starting_pos[0], starting_pos[1]
                    else:
                        dx = 0

                # TOP/BOTTOM COLLISIONS
                if tile.rect.colliderect(pygame.Rect(self.x, self.y - self.height + dy, self.width, self.height)):
                    if tile.type == "lava":
                        self.health -= 1
                        if self.health > 0:
                            self.x, self.y = starting_pos[0], starting_pos[1]
                    else:
                        if self.vel_y < 0:  # Top collision if it's jumping
                            dy = tile.rect.bottom - self.y + self.height
                            self.vel_y = 0
                        elif self.vel_y >= 0:  # Bottom collision if it's falling
                            dy = tile.rect.top - self.y
                            self.jumpCount = 1

            for entity in entities:
                enemy_rect = pygame.Rect(entity.x, entity.y, entity.width, entity.height)
                # SIDES COLLISION
                if enemy_rect.colliderect(pygame.Rect(self.x + dx, self.y - self.height, self.width, self.height)):
                    if entity.type == "jelly":
                        self.health -= 1
                        dx = 0
                        if self.health > 0:
                            self.x, self.y = starting_pos[0], starting_pos[1]
                    elif entity.type == "heart":
                        entities.remove(entity)
                        self.health += entity.health
                        entity.health -= 1
                    elif entity.type == "door":
                        WIN = True
                        MENU = True

                # BOTTOM COLLISION
                if enemy_rect.colliderect(pygame.Rect(self.x, self.y - self.height + dy, self.width, self.height)):
                    if self.vel_y >= 0:  # Bottom collision if it's falling
                        if entity.type == "jelly":
                            dy = enemy_rect.top - self.y
                            self.vel_y = -15
                            self.jumpCount = 1
                            entity.health -= 1
                            self.xp += 5
                        elif entity.type == "heart":
                            self.health += 1
                            entity.health -= 1
                        elif entity.type == "door":
                            WIN = True
                            MENU = True

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
        img = None
        if self.type == "dirt":
            img = dirt_img
        elif self.type == "grass":
            img = grass_img
        elif self.type == "platform":
            img = platform_img
        elif self.type == "lava":
            img = lava_img
        self.img = pygame.transform.scale(img, (25, 25)).convert_alpha()
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.rect = pygame.Rect(self.x, self.y, TILE_SIDE, TILE_SIDE)

    def draw_tile(self): ARENA.blit(self.img, (self.x, self.y, self.width, self.height))


class Entity:
    def __init__(self, x, y, health, type_of_entity):
        img = jelly_img
        if type_of_entity == "jelly":
            img = jelly_img
        elif type_of_entity == "heart":
            img = heart_img
        elif type_of_entity == "door":
            img = door_img
        if img != door_img:
            self.img_left = pygame.transform.scale(img, (28, 24))
            self.img_right = pygame.transform.flip(self.img_left, True, False).convert_alpha()
        else:  # If it's a door
            self.img_left = self.img_right = img
        self.rect = self.img_right.get_rect()
        self.x = x
        self.y = y
        self.dx = 2
        self.dir = -1
        self.width = jelly_img.get_width()
        self.height = jelly_img.get_height()
        self.move_counter = 0
        self.health = health
        self.type = type_of_entity

    def draw(self):
        if self.dir == 1:
            img = self.img_right
        else:
            img = self.img_left

        if self.type == "door":
            ARENA.blit(img, (self.x, self.y - 5))
        else:
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


class Button:
    def __init__(self, x, y, txt):
        self.x = x
        self.y = y
        self.img = txt
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.rect = pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)

    def draw(self):
        x = self.x - self.width // 2
        y = self.y - self.height // 2
        ARENA.blit(self.img, (x, y))


def check_button_click(button):
    pos = pygame.mouse.get_pos()
    if button.rect.collidepoint(pos):
        return True
    else:
        return False


def draw_game(player, tiles, entities, buttons):
    ARENA.blit(bg_img, (0, 0))
    if MENU:
        for button in buttons:
            button.draw()
        ARENA.blit(game_name_img, (WIDTH/2 - game_name_img.get_width()/2, HEIGHT / 6))

        if WIN:
            win_message = font.render(f'YOU WIN THE GAME! TOTAL OF XP: {player.xp}', True, BLACK)
            ARENA.blit(win_message, (WIDTH // 5, HEIGHT // 2))

    else:
        player.draw()

        for tile in tiles:
            tile.draw_tile()

        for entity in entities:
            entity.draw()

        heart = pygame.transform.scale(heart_img, (31, 30))

        for life in range(player.health):
            ARENA.blit(heart, (TILE_SIDE + life * (heart.get_width() + 5), 950))

        text = font.render(f'XP: {player.xp}', True, WHITE)
        ARENA.blit(text, (2 * TILE_SIDE + 10 * (heart.get_width() + 5), 950))

    pygame.display.update()


def update_game(player, tiles, entities):
    global MENU
    if not MENU:
        player.move(tiles, entities)
        if player.health <= 0:
            player.img = ghost_img

            # When the player ghost leaves the screen -> back to the menu
            if player.y + player.height < 0:
                MENU = True

        for entity in entities:
            if entity.type == "jelly":
                entity.move(tiles)
            if entity.health <= 0:
                entities.remove(entity)


def get_map_from_file(map1):
    file = open(str(map1), "r")
    tiles = []
    entities = []
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
            if lines[line][col] == "B":
                entities.append(Entity(col * TILE_SIDE, line * TILE_SIDE, 1, "jelly"))
            if lines[line][col] == "H":
                entities.append(Entity(col * TILE_SIDE, line * TILE_SIDE, 1, "heart"))
            if lines[line][col] == "W":
                entities.append(Entity(col * TILE_SIDE, line * TILE_SIDE, 10000, "door"))

    return tiles, entities


def starting_game():
    global WIN
    WIN = False
    return Player(starting_pos[0], starting_pos[1]), get_map_from_file("map.txt")[0], get_map_from_file("map.txt")[1]


def main():
    global MENU
    running = True

    game = player, tiles, entities = starting_game()
    buttons = [Button(WIDTH // 4, 2*HEIGHT // 3, play_button_img), Button(3*WIDTH // 4, 2*HEIGHT // 3, exit_button_img)]

    while running:
        clock.tick(FPS)

        update_game(player, tiles, entities)

        draw_game(player, tiles, entities, buttons)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif MENU and event.type == pygame.MOUSEBUTTONDOWN:
                if check_button_click(buttons[1]):  # Click the EXIT button
                    running = False
                else:
                    if check_button_click(buttons[0]):  # Click the PLAY button
                        MENU = False
                    if not MENU and game != starting_game():
                        game = player, tiles, entities = starting_game()  # Restart the Game

    pygame.quit()


main()
