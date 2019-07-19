import pygame as pg

red_gift = pg.image.load("red.png")
red_gift = pg.transform.scale(red_gift, (32, 32))


class Gun:
    red = False
    gunLevel = 1


class RedGift(pg.sprite.Sprite):
    def __init__(self, ship_pos: list, pos=[0, 0], *groups):
        self.groups = groups[0], groups[1]
        self._layer = 1

        pg.sprite.Sprite.__init__(self, self.groups)

        self.image = red_gift
        self.rect = self.image.get_rect()
        self.radius = 16

        self.pos = pos
        self.rect.center = self.pos

        self.ship_pos = ship_pos

    def update(self, time):

        self.pos[1] += 100 * time
        self.rect.center = self.pos

        dx = self.rect.centerx - self.ship_pos[0]
        dy = self.rect.centery - self.ship_pos[1]

        if dx ** 2 <= 36 ** 2 and dy ** 2 <= 32 ** 2 and not Gun.red:
            # if gınLevel < 5 şeyler niye yazmıyooooz? çünkü gerek yok
            Gun.red = True
            Gun.gunLevel += 1
            self.kill()
        elif dx ** 2 <= 36 ** 2 and dy ** 2 <= 32 ** 2 and Gun.red:
            # if gınLevel < 5 şeyler niye yazmıyooooz? çünkü gerek yok
            Gun.gunLevel += 1
            self.kill()
        else:
            print("not collided")

        if self.rect.top > 512:
            self.kill()
