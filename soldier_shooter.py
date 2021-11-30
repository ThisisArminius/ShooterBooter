import pygame
import os
from pygame import mixer
import random
import csv
import  button

mixer.init()
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

# set frame rate
clock = pygame.time.Clock()
FPS = 60

# define game variables
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False
level_intro = False

# define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

# Loadin music and sounds.
# Game music
pygame.mixer.music.load('audio/music2.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)

# Jump sound
jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.3)

# Gunshot sound
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.3)

# Grenade sound
grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(0.4)

enemy_dead_fx = pygame.mixer.Sound('audio/163442__under7dude__man-dying.wav')
enemy_dead_fx.set_volume(0.3)

player_death_fx = pygame.mixer.Sound('audio/death.wav')
player_death_fx.set_volume(0.9)

victory_fx = pygame.mixer.Sound('audio/V.wav')
victory_fx.set_volume(0.4)

# load images.
# Button images.
start_image = pygame.image.load('img/start_btn.png').convert_alpha()
exit_image = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_image = pygame.image.load('img/restart_btn.png').convert_alpha()
# Background images.
pine1_img = pygame.image.load('img/background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/background/sky_cloud.png').convert_alpha()

# Store tiles in a list.
image_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/tile/{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    image_list.append(img)
# bullet
bullet_img = pygame.image.load('img/icons/bulletclassis.png').convert_alpha()
bullet_img = pygame.transform.scale(bullet_img, ((bullet_img.get_width() * 0.7), (bullet_img.get_height() * 0.7)))
bullet_flash_img = pygame.image.load('img/EXTRAS/MuzzleFlash.png').convert_alpha()
stream_img = pygame.image.load('img/EXTRAS/BulletStream.png').convert_alpha()
stream_img = pygame.transform.scale(stream_img, ((stream_img.get_width() * 0.5), (stream_img.get_height())))
# Grenade image.
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()
# Item box images
health_box_image = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_image = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_image = pygame.image.load('img/icons/grenade_box.png').convert_alpha()

# Menu images.
bg_img = pygame.image.load('img/bullet_bg.jpg').convert_alpha()
bg_image = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Gameintro bg images.
bbgs = []
for i in range(1, 5):
    img = pygame.image.load(f'img/bg cut/{i}.png').convert_alpha()
    bbgs.append(pygame.transform.scale(img, (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)))


# Pickup boxes.
item_boxes = {
    'Health': health_box_image,
    'Ammo': ammo_box_image,
    'Grenade': grenade_box_image
}

# define colours
BLACK = (0, 0, 0)
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLOOD_RED = (187, 74, 73)

# define font
font = pygame.font.Font('font/AtomicAge-Regular.ttf', 16)

def reset_level():
    """a function to reset level."""
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    # Create empty tiles.
    data = []
    for i in range(ROWS):
        r = [-1] * COLS
        data.append(r)
    return data

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height() ))

class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        #create ai specific variables.
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0
        # load all images for the players
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        # update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        # reset movement variables
        screen_scroll = 0
        dx = 0
        dy = 0

        # assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        # check for collision
        for tile in world.obstacle_list:
            # check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                # if the ai has hit the wall then it will turn around.
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            # check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # check if below the ground, i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom
        # Check if going off the edges of the screen.
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or  self.rect.right + dx > SCREEN_WIDTH:
                dx = 0
        # Check for collision with water.
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        # Check for collision with finish tile..
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True
            victory_fx.play()

        # Check if fallen off the map.
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0
            self.alive = False

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        # update-scroll based on player position,
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH) or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery,
                            self.direction)
            bullet_group.add(bullet)
            # reduce ammo
            self.ammo -= 1
            shot_fx.play()
    def player_gun_effects(self):
        # add aftershot smoke.

        stream = BulletStream((self.rect.centerx + 10) + (0.2 * self.rect.size[0] * self.direction),
                              self.rect.centery + (0.04 * self.rect.size[0]),
                              self.direction)
        bullet_stream_group.add(stream)
        # Add muzzle flash effect
        flash = MuzzleFlash(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction),
                            self.rect.centery + (0.04 * self.rect.size[0]), self.direction)
        muzzle_flash_group.add(flash)
    def player_shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery,
                            self.direction)
            player_bullet_group.add(bullet)
            self.player_gun_effects()
            # reduce ammo
            self.ammo -= 1
            shot_fx.play()

    def ai(self):
        if self.alive and player.alive:
            if not self.idling and random.randint(1, 300) == 1:
                self.idling = True
                self.idling_counter = 50
                self.update_action(0)
            # Check if the ai is near the player.
            if self.vision.colliderect(player.rect):
                # Stop and face the player.
                self.update_action(0)
                # Shoot
                self.shoot()
            else:
                if not self.idling:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # Run
                    self.move_counter += 1
                    # Update ai vision as the enemy moves.
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                    if self.move_counter > TILE_SIZE:
                        enemy.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False
        # Scroll
        self.rect.x += screen_scroll
    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 100
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            elif self.action == 2:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class World:
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        # iterate through each value in level data.
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = image_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        # Water
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        #Decor
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:
                        # Create a player.
                        player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 1.5, 5, 20, 5)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16:
                        # Create enemy
                        enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.5, 2, 20, 0)
                        enemy_group.add(enemy)
                    elif tile == 17:
                        # Create ammo box
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18:
                        # Create Grenade box
                        item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19:
                        # Create Health box
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20:
                        # Create exit.
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)
        return player, health_bar


    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])

class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        # Scroll
        self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        # Scroll
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        # Scroll
        self.rect.x += screen_scroll

class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.speed = 10
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.rect.midtop = ((x + TILE_SIZE // 2), y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        # Scroll
        self.rect.x += screen_scroll
        if pygame.sprite.collide_rect(self, player):
            # Check what kind of box is picked up.
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 3
            self.kill()

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health
        # Calculate health ration.
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 19))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 15))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 15))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # move bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll
        # check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        # Check collision with level.
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        # check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, player_bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()

class MuzzleFlash(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_flash_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.counter = 0

    def update(self):
        if self.direction == -1:
            self.image = pygame.transform.flip(bullet_flash_img, True, False)
        self.counter += 1
        if self.counter == 5:
            self.kill()
            self.counter = 0

class BulletStream(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = stream_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = player.direction

    def update(self):
        if self.direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)
            # move bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll
        # Check collision with level.
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        # check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, player_bullet_group, False):
                if enemy.alive:
                    self.kill()

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.vel_y += GRAVITY
        dx = self.speed * self.direction
        dy = self.vel_y

        # check collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            # check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                # check if below the ground, i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                    # check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom



        # Update the grenade position.
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        # Countdown timer.
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)

            # do damage to anyone nearby.
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                        abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2:
                    enemy.health -= 50

            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f'img/explosion/exp{num}.png')
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
            self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        # Scroll
        self.rect.x += screen_scroll
        EXPLOSION_SPEED = 4
        # Update explosion animation.
        self.counter += 1
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]

class ScreenFade:
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0
        img = pygame.image.load(f'img/blood.png').convert_alpha()
        self.image = pygame.transform.scale(img, ((img.get_width()//10), (img.get_height()//10)))
        self.rect = self.image.get_rect()


    def fade(self):
        circle = pygame
        fade_complete = False
        self.fade_counter += self.speed

        if self.direction == 0:
            # Bullet screen fade
            screen.blit(bbgs[0], (0 - self.fade_counter, 0 - self.fade_counter, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(bbgs[1], (SCREEN_WIDTH // 2 + self.fade_counter, 0 - self.fade_counter, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(bbgs[2], (0 - self.fade_counter, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(bbgs[3], (SCREEN_WIDTH // 2 + self.fade_counter, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH//2, SCREEN_HEIGHT//2))

        if self.direction == 1:# Whole screen fade.
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.colour, (0, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))

        if self.direction == 2:# Vertical screen fade down
            screen.blit(self.image, (0, -5 + self.fade_counter))
            pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter) )
        if self.fade_counter >= 900:
            fade_complete = True


        return  fade_complete

# Create screen fades.
death_fade = ScreenFade(2, BLOOD_RED, 4)
start_fade = ScreenFade(0, BLACK, 4)
level_up_fade = ScreenFade(1, BLACK, 4)
# Create buttons.
start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 -150, start_image, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_image, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2  -50, restart_image, 1.5)

# create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
player_bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
muzzle_flash_group = pygame.sprite.Group()
bullet_stream_group = pygame.sprite.Group()

# Create empty tile list.
world_data = []
for i in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
# Load level data and create world.
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] =  int(tile)

world = World()
player, health_bar = world.process_data(world_data)


run = True
while run:
    clock.tick(FPS)

    if start_game == False:
        # draw menu.
        screen.fill(BG)
        screen.blit(bg_image, (0, 0))
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False
    else:
        # Update background
        draw_bg()
        # Draw world map
        world.draw()
        # show health
        health_bar.draw(player.health)
        # show ammo
        draw_text(f'AMMO: ', font, WHITE, 10, 25)
        for x in range(player.ammo):
            bul_img = pygame.transform.scale(bullet_img, ((bullet_img.get_width() * 1.5), (bullet_img.get_height() * 1.5)))
            screen.blit(pygame.transform.rotate(bul_img, 90), (75 + (x * 10), 33))
        # show grenades
        draw_text(f'GRENADE:', font, WHITE, 10, 45)
        for x in range(player.grenades):
            screen.blit(grenade_img, (90 + (x * 10), 50))
        #Update  and draw player
        player.update()
        player.draw()
        # Update and draw each sprite in enemy sprite group
        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        # update groups
        bullet_group.update()
        muzzle_flash_group.update()
        bullet_stream_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        player_bullet_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()


        # Draw Groups.
        player_bullet_group.draw(screen)
        bullet_group.draw(screen)
        muzzle_flash_group.draw(screen)
        bullet_stream_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)

        # Show level up intro
        if level_intro == True:
            if level_up_fade.fade():
                level_intro = False
                level_up_fade.fade_counter = 0
        # Show intro
        if start_intro == True:
            if start_fade.fade():
                start_intro = False
                start_fade.fade_counter = 0


        # update player actions
        if player.alive:
            # shoot bullets
            if shoot:
                player.player_shoot()
            # throw grenades
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction), \
                                  player.rect.top, player.direction)
                grenade_group.add(grenade)
                # reduce grenades
                player.grenades -= 1
                grenade_thrown = True
            if player.in_air:
                player.update_action(2)#2:Jump
            elif moving_left or moving_right:
                player.update_action(1)#1:Run
            else:
                player.update_action(0)#0:Idle
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            # Check if level is complete.
            if level_complete:
                level_intro = True
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level   <= MAX_LEVELS:
                    # Load leved data and create the world.
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)

        else:
            screen_scroll = 0
            if death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    level_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    # Load leved data and create the world.
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)

    for event in pygame.event.get():
        # quit game
        if event.type == pygame.QUIT:
            run = False
        # keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_e:
                grenade = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                run = False

        # keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_e:
                grenade = False
                grenade_thrown = False

    pygame.display.update()

pygame.quit()
