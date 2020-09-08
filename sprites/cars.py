import pygame as pg
from options import TILESIZE

# parent class of all cars
class Car(pg.sprite.Sprite):
    def __init__(self,game,x,y,direction=0,speed=0,accel=0):
        self.groups = game.all_sprites, game.vehicles
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        # initializes the sprite screen
        self.image = pg.Surface((TILESIZE,TILESIZE))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y

        self.direction = 0 #in degrees
        self.speed = 0
        self.accel = 0

    def move(self, dx=0, dy=0):
        self.x += dx
        self.y += dy

    def update(self):
        self.rect.x = self.x #* TILESIZE
        self.rect.y = self.y

