import pygame as pg
import os
import random

pg.init()
pg.mixer.pre_init()

mainloop = True

bulletSound = pg.mixer.Sound("lips.wav")

screen_width, screen_height = 288, 512

bg = pg.image.load("bg.jpg")
spaceship = pg.image.load("spaceship.png")
meteor = pg.image.load("meteor.png")

bg = pg.transform.scale(bg, (screen_width, screen_height,))
spaceship = pg.transform.scale(spaceship, (40, 32))

screen = pg.display.set_mode((screen_width, screen_height))

gameTitle = "A Game"

pg.display.set_caption(gameTitle)

clock = pg.time.Clock()

all_groups = pg.sprite.Group()
bullet_group = pg.sprite.Group()
ship_group = pg.sprite.Group()
meteor_group = pg.sprite.Group()


def write_text(msg, font_size):
    font = pg.font.SysFont('none', font_size)
    text = font.render(msg, True, (255, 255, 255))
    text.convert()
    return text


class Ship(pg.sprite.Sprite):
    def __init__(self, screen, pos=[144, 492]):
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = spaceship
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self.radius = 15
        self.image.convert_alpha()
        self.screenRect = screen.get_rect()
        self.alive = True

    def update(self, time):
        key = pg.key.get_pressed()
        dx = 0

        if key[pg.K_RIGHT]:
            dx = 700 * time
        if key[pg.K_LEFT]:
            dx = -700 * time

        self.pos[0] += dx
        self.rect.center = self.pos

        if self.screenRect.left >= self.rect.left:
            self.rect.left = self.screenRect.left

        if self.screenRect.right <= self.rect.right:
            self.rect.right = self.screenRect.right

        collided = pg.sprite.spritecollide(self, meteor_group, False, pg.sprite.collide_mask)
        for c in collided:
            self.alive = False
            break


class Bullet(pg.sprite.Sprite):
    def __init__(self, pos, screen):
        self.groups = all_groups, bullet_group
        pg.sprite.Sprite.__init__(self, self.groups)

        self.image = pg.surface.Surface((3, 8))
        self.image.fill((100, 160, 250))

        self.rect = self.image.get_rect()
        self.pos = pos.copy()
        self.rect.center = pos

        self.screen_rect = screen.get_rect()

    def update(self, time):
        self.pos[1] -= 500 * time

        self.rect.center = self.pos

        if not self.screen_rect.contains(self.rect):
            self.kill()


class Meteor(pg.sprite.Sprite):
    score = 0

    def __init__(self, screen):
        self.groups = all_groups, meteor_group

        pg.sprite.Sprite.__init__(self, self.groups)

        randomScale = random.randint(15, 50)

        self.image = pg.image.load("meteor.png")
        self.image = pg.transform.scale(self.image, (randomScale * 2, randomScale * 2))
        self.image.convert_alpha()

        self.rect = self.image.get_rect()
        self.radius = randomScale

        self.pos = [random.randint(self.radius, screen_width - self.radius), -50]
        self.rect.center = self.pos
        self.screen_rect = screen.get_rect()

    def update(self, time):

        self.pos[1] += 200 * time
        self.rect.center = self.pos

        collided_bullets = pg.sprite.spritecollide(self, bullet_group, True, pg.sprite.collide_circle)
        for c in collided_bullets:
            Meteor.score += 1
            self.kill()

        if self.rect.right > screen_width + self.rect.width:
            self.kill()


bullet_frequency = 0.5
bullet_time = 0

meteor_frequency = 1
meteor_time = 0

Ship.groups = all_groups, ship_group

ship = Ship(screen)

screen.blit(bg, (0, 0))

while mainloop:
    time = clock.tick()  # milliseconds
    seconds = time / 1000.0

    bullet_time += seconds
    meteor_time += seconds

    keys = pg.key.get_pressed()

    if keys[pg.K_SPACE] and bullet_time > bullet_frequency and ship.alive:
        Bullet(ship.pos, screen)
        bullet_time = 0
        bulletSound.play()

    if meteor_time > meteor_frequency:
        Meteor(screen)
        meteor_time = 0

    for event in pg.event.get():
        if event.type == pg.QUIT:
            mainloop = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                mainloop = False

    # all_groups.clear(screen, background) -> this line of code should be written in a custom skeleton for pygame
    # but background not defined here because of the game dependent nature of background surface(image etc.)
    all_groups.clear(screen, bg)
    all_groups.update(seconds)
    all_groups.draw(screen)

    if ship.alive is False:
        text = write_text("You Died Score:" + str(Meteor.score), 20)
        rect = text.get_rect()
        screen.blit(text, (screen_width / 2 - rect.width / 2, screen_height / 2 - rect.height / 2))
        ship.kill()

    pg.display.flip()

pg.quit()