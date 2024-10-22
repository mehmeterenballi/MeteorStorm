import pygame as pg
import random
import time
import scoring
import gift

pg.init()
pg.mixer.pre_init()

mainloop = True

bulletSound = pg.mixer.Sound("lips.wav")

screen_width, screen_height = 288, 512

bg = pg.image.load("space.gif")
spaceship = pg.image.load("spaceship.png")
meteor = pg.image.load("meteor.png")

bg = pg.transform.scale(bg, (screen_width, screen_height))
spaceship = pg.transform.scale(spaceship, (40, 32))

screen = pg.display.set_mode((screen_width, screen_height))

gameTitle = "MeteorStorm"

pg.display.set_caption(gameTitle)

clock = pg.time.Clock()

all_groups = pg.sprite.LayeredUpdates()
bullet_group = pg.sprite.Group()
ship_group = pg.sprite.Group()
round_meteor_group = pg.sprite.Group()
meteor_group = pg.sprite.Group()
gift_group = pg.sprite.Group()


# def write_text(msg, font_size):
#     font = pg.font.SysFont('none', font_size)
#     text = font.render(msg, True, (255, 255, 255))
#     text.convert()
#     return text


class Ship(pg.sprite.Sprite):
    def __init__(self, screen, pos=[144, 492]):
        self.groups = ship_group, all_groups
        self._layer = 4

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
        self._layer = 4

        pg.sprite.Sprite.__init__(self, self.groups)

        self.image = pg.image.load("laser.png")
        self.image = pg.transform.scale(self.image, (10, 15))
        self.image.convert_alpha()

        self.rect = self.image.get_rect()
        self.pos = pos.copy()
        self.rect.center = pos

        self.screen_rect = screen.get_rect()

    def update(self, time):
        self.pos[1] -= 100 * time

        self.rect.center = self.pos

        if self.rect.bottom < 0:
            self.kill()


class Meteor(pg.sprite.Sprite):
    score = 0

    def __init__(self, screen):
        self.groups = all_groups, meteor_group
        self._layer = 2
        pg.sprite.Sprite.__init__(self, self.groups)

        randomScale = random.randint(15, 50)

        self.image = pg.image.load("meteor.png")
        self.image = pg.transform.scale(self.image, (randomScale * 2, randomScale * 2))
        self.image.convert_alpha()

        self.rect = self.image.get_rect()

        self.pos = [random.randint(randomScale, screen_width - randomScale), -100]
        self.rect.center = self.pos
        self.screen_rect = screen.get_rect()

    def update(self, time):

        self.pos[1] += 200 * time
        self.rect.center = self.pos

        collided_bullets = pg.sprite.spritecollide(self, bullet_group, True, pg.sprite.collide_mask)
        for c in collided_bullets:
            Meteor.score += 10
            self.kill()

        if self.rect.right > screen_width + self.rect.width:
            self.kill()


class RoundMeteor(pg.sprite.Sprite):

    def __init__(self, screen):
        self.groups = round_meteor_group, meteor_group
        self._layer = 3
        pg.sprite.Sprite.__init__(self, self.groups)

        randomScale = random.randint(15, 50)

        self.image = pg.image.load("round_meteor1.png")
        self.image = pg.transform.scale(self.image, (randomScale * 2, randomScale * 2))
        self.image.convert_alpha()

        self.image_orig = self.image.copy()

        self.rect = self.image.get_rect()

        self.pos = [random.randint(randomScale, screen_width - randomScale), -100]
        self.rect.center = self.pos
        self.screen_rect = screen.get_rect()
        self.spin = 0
        self.spin_speed = random.randint(-12, 12)
        self.last_update = pg.time.get_ticks()

        self.dx = 1
        self.rot_speed = random.randint(-200, 200) * self.dx

    def rotate(self):
        now = pg.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.spin = (self.spin + self.spin_speed) % 360
            self.image = pg.transform.rotate(self.image_orig, self.spin)
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self, time):

        self.rotate()

        self.pos[0] += self.rot_speed * self.dx * time
        self.pos[1] += 200 * time
        self.rect.center = self.pos

        # The if elif lines make round meteor bounce from edge of the screen if hits
        if self.rect.width / 2 >= self.rect.centerx:
            self.dx = self.dx * -1
        elif screen_width - self.rect.width / 2 <= self.rect.centerx:
            self.dx = self.dx * -1

        collided_bullets = pg.sprite.spritecollide(self, bullet_group, True, pg.sprite.collide_mask)
        for c in collided_bullets:
            Meteor.score += 100
            self.kill()

        if self.rect.right > screen_width + self.rect.width:
            self.kill()


bullet_frequency = 0.5
bullet_time = 0

meteor_frequency = 1 / ((Meteor.score // 10) + 1)
meteor_time = 0

round_meteor_frequency = 1 / ((Meteor.score // 10) + 1)
round_meteor_time = 0

red_gift_frequency = 5
red_gift_time = 0

ship = Ship(screen)

oldLevel = 0

backgroundy = 0

while mainloop:
    time = clock.tick()  # milliseconds
    seconds = time / 1000.0

    bullet_time += seconds
    meteor_time += seconds
    round_meteor_time += seconds / 2

    red_gift_time += seconds

    keys = pg.key.get_pressed()

    if keys[pg.K_SPACE] and bullet_time > bullet_frequency and ship.alive:
        if gift.Gun.gunLevel == 1:
            Bullet(ship.pos, screen)
        elif gift.Gun.gunLevel == 2:
            Bullet([ship.pos[0] - 12, ship.pos[1]], screen)
            Bullet([ship.pos[0] + 12, ship.pos[1]], screen)
        elif gift.Gun.gunLevel == 3:
            Bullet([ship.pos[0] - 12, ship.pos[1]], screen)
            Bullet([ship.pos[0] + 12, ship.pos[1]], screen)
            Bullet([ship.pos[0], ship.pos[1] - 7], screen)
        elif gift.Gun.gunLevel == 4:
            Bullet([ship.pos[0] - 12, ship.pos[1]], screen)
            Bullet([ship.pos[0] + 12, ship.pos[1]], screen)
            Bullet([ship.pos[0] - 20, ship.pos[1] + 15], screen)
            Bullet([ship.pos[0] + 20, ship.pos[1] + 15], screen)
            Bullet([ship.pos[0], ship.pos[1] - 7], screen)
        else:
            print("Gun level bigger than 4")
        bullet_time = 0
        bulletSound.play()

    if meteor_time > meteor_frequency:
        Meteor(screen)
        meteor_time = 0

    if Meteor.score >= 10 and round_meteor_time > round_meteor_frequency:
        RoundMeteor(screen)
        round_meteor_time = 0

    for event in pg.event.get():
        if event.type == pg.QUIT:
            mainloop = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                mainloop = False

    backgroundy += time * 100
    screen.blit(bg, (0, backgroundy))
    if backgroundy > screen_height:
        backgroundy = 0

    screen.blit(bg, (0, 0))

    scoring.score_blitting(screen, Meteor.score)

    if red_gift_time > red_gift_frequency and gift.Gun.gunLevel <= 3:
        gift.RedGift(ship.pos, [random.randint(16, 272), -16], all_groups, gift_group, ship_group)
        red_gift_time = 0

    all_groups.update(seconds)
    all_groups.draw(screen)

    if Meteor.score >= 10:
        round_meteor_group.update(seconds)
        round_meteor_group.draw(screen)

    if ship.alive is False:
        # text = write_text("You Died Score:" + str(Meteor.score * 10), 20)
        # rect = text.get_rect()
        # screen.blit(text, (screen_width / 2 - rect.width / 2, screen_height / 2 - rect.height / 2))
        ship.kill()
    # else:
        # text = write_text("Score:" + str(Meteor.score * 10), 20)
        # rect = text.get_rect()
        # screen.blit(text, (screen_width-rect.width, 10))

    pg.display.flip()

pg.quit()
