import pygame
from os.path import join
from random import randint, uniform

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join("images", "player.png")).convert_alpha()
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction = pygame.math.Vector2()
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.powered_up = False
        self.powered_up_time = 0

    def update(self, delta_time):
        keys = pygame.key.get_pressed()
        self.direction.x = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        self.direction.y = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * 350 * delta_time

        self.__handle_shooting()

    def activate_power_up(self):
        self.powered_up = True
        self.powered_up_time = pygame.time.get_ticks()

    def __update_laser_timer(self, cooldown):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= cooldown:
                self.can_shoot = True

    def __update_powerup_timer(self):
        if self.powered_up:
            current_time = pygame.time.get_ticks()
            if current_time - self.powered_up_time >= 5000:
                self.powered_up = False

    def  __shoot_laser(self):
        Laser((all_sprites, laser_sprites), laser_surf, self.rect.midtop)
        self.can_shoot = False
        self.laser_shoot_time = pygame.time.get_ticks()
        laser_sound.play()

    def __handle_shooting(self):
        if self.powered_up:
            if self.can_shoot:
                self.__shoot_laser()
            self.__update_laser_timer(200)
            self.__update_powerup_timer()
        else:
            recent_keys = pygame.key.get_just_pressed()
            if recent_keys[pygame.K_SPACE] and self.can_shoot:
                self.__shoot_laser()
            self.__update_laser_timer(1000)

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf, pos):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        
class Laser(pygame.sprite.Sprite):
    def __init__(self, groups, surf, pos):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)

    def update(self, delta_time):
        self.rect.centery -= 400 * delta_time
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, groups, scoreDisplay, surf, pos):
        super().__init__(groups)
        self.scoreDisplay = scoreDisplay
        self.original_surf = surf
        self.image = self.original_surf
        self.rect = self.image.get_frect(center = pos)
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(400, 650)
        self.rotation = 0
        self.rotation_speed = randint(-100, 100)

    def update(self, delta_time):
        self.rect.center += self.direction * self.speed * delta_time
        self.rotation += self.rotation_speed * delta_time
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)

        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

    def hit(self):
        scoreDisplay.score += 5
        self.kill()

class BigMeteor(pygame.sprite.Sprite):
    def __init__(self, groups, scoreDisplay, surf, pos):
        super().__init__(groups)
        self.scoreDisplay = scoreDisplay
        self.original_surf = surf
        self.image = self.original_surf
        self.rect = self.image.get_frect(center = pos)
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(75, 125)
        self.rotation = 0
        self.rotation_speed = randint(-25, 25)
        self.hit_points = 3

    def update(self, delta_time):
        self.rect.center += self.direction * self.speed * delta_time
        self.rotation += self.rotation_speed * delta_time
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)

        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

    def hit(self):
        self.hit_points -= 1
        if self.hit_points == 0:
            scoreDisplay.score += 25 
            self.kill()

            for direction in [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]: 
                SmallMeteor((all_sprites, meteor_sprites), scoreDisplay, pygame.transform.scale_by(meteor_surf, 0.5), self.rect.center, pygame.Vector2(direction[0], direction[1]))

            if randint(0, 100) < 10:
                PowerUp((all_sprites, powerup_sprites), self.rect.center)

class SmallMeteor(pygame.sprite.Sprite):
    def __init__(self, groups, scoreDisplay, surf, pos, dir):
        super().__init__(groups)
        self.scoreDisplay = scoreDisplay
        self.original_surf = surf
        self.image = self.original_surf
        self.rect = self.image.get_frect(center = pos)
        self.direction = dir
        self.speed = randint(500, 800)
        self.rotation = 0
        self.rotation_speed = randint(-150, 150)

    def update(self, delta_time):
        self.rect.center += self.direction * self.speed * delta_time
        self.rotation += self.rotation_speed * delta_time
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)

        if self.rect.top > WINDOW_HEIGHT or self.rect.bottom < 0 or self.rect.right > WINDOW_WIDTH or self.rect.left < 0:
            self.kill()

    def hit(self):
        scoreDisplay.score += 1
        self.kill()

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, groups, frames, pos):
        super().__init__(groups)
        self.image = frames[0]
        self.rect = self.image.get_frect(center = pos)
        self.frames = frames
        self.frame_index = 0

        explosion_sound.play()

    def update(self, delta_time):
        self.frame_index += 25 * delta_time
        if self.frame_index < len(self.frames): 
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

class ScoreDisplay(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = font.render("0", True, (240, 240, 240))
        self.rect = self.image.get_rect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))
        self.score = 0

    def update(self, delta_time):
        self.image = font.render(str(self.score), True, (240, 240, 240))


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, groups, pos):
        super().__init__(groups)
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.aacircle(self.image, "red", (20, 20), 20)
        self.rect = self.image.get_frect(center = pos)
        self.position = pos

    def update(self, delta_time):
        self.rect.centery += 200 * delta_time
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

def check_collisions():
    global running

    if pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask):
        running = False

    for laser in laser_sprites:
        hit_meteors = pygame.sprite.spritecollide(laser, meteor_sprites, False, pygame.sprite.collide_mask)
        if hit_meteors:
            laser.kill()
            AnimatedExplosion(all_sprites, explosion_frames, laser.rect.midtop)
            hit_meteors[0].hit()

    if pygame.sprite.spritecollide(player, powerup_sprites, True, pygame.sprite.collide_mask):
        player.activate_power_up()

# general setup
pygame.init()

display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

# imports
laser_surf = pygame.image.load(join("images", "laser.png")).convert_alpha()
star_surf = pygame.image.load(join("images", "star.png")).convert_alpha()
meteor_surf = pygame.image.load(join("images", "meteor.png")).convert_alpha()
explosion_frames = [pygame.image.load(join("images", "explosion", f"{i}.png")).convert_alpha() for i in range(21)]

font = pygame.font.Font(join("images", "Oxanium-Bold.ttf"), 40)

laser_sound = pygame.mixer.Sound(join("audio", "laser.wav"))
laser_sound.set_volume(0.75)
explosion_sound = pygame.mixer.Sound(join("audio", "explosion.wav"))
explosion_sound.set_volume(0.75)
game_music = pygame.mixer.Sound(join("audio", "game_music.wav"))
game_music.set_volume(0.2)
game_music.play(-1)

# sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
powerup_sprites = pygame.sprite.Group()

for i in range(20):
    random_pos = (randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT))
    Star(all_sprites, star_surf, random_pos)
player = Player(all_sprites)
scoreDisplay = ScoreDisplay(all_sprites)

# custom events
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 400)

score_event = pygame.event.custom_type()
pygame.time.set_timer(score_event, 1000)

# game loop
running = True
while running:
    delta_time = clock.tick(60) /  1000

    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            random_pos = (randint(100, WINDOW_WIDTH - 100), randint(-200, -100))
            if (randint(0, 100) < 10):
                BigMeteor((all_sprites, meteor_sprites), scoreDisplay, pygame.transform.scale2x(meteor_surf), random_pos)
            else:
                Meteor((all_sprites, meteor_sprites), scoreDisplay, meteor_surf, random_pos)
        if event.type == score_event:
            scoreDisplay.score += 1

    # update
    all_sprites.update(delta_time)

    # draw the game
    display_surface.blit(scoreDisplay.image, scoreDisplay.rect)
    pygame.draw.rect(display_surface, (240, 240, 240), scoreDisplay.rect.inflate(20, 10).move(0, -8), 5, 10)

    display_surface.fill("#3a2e3f")
    all_sprites.draw(display_surface)

    # collision
    check_collisions()

    pygame.display.update()

pygame.quit()