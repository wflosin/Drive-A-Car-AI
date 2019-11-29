import pygame as pg
from options import TILESIZE,BLACK
from os import path

class Wall(pg.sprite.Sprite):
    """ A sandard wall. follows the grid pattern """
    def __init__(self,game,x,y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.image = pg.Surface((TILESIZE,TILESIZE))
        self.rect = self.image.get_rect()
        self.image.fill((1,1,1))

        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        
class Coin(pg.sprite.Sprite):
    """ A token showing the progress on the course. follows the grid pattern """
    def __init__(self,game,x,y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.image = pg.image.load(path.join('sprites','coin.png')).convert_alpha()
        self.rect = self.image.get_rect()

        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE   

class Checkpoint(pg.sprite.Sprite):
    """ A line showing that when passes, signifies progress on the course. """
    def __init__(self,game,x,y,w=1,h=1,colour=(0,150,0),start=False):
        if start:
            self.groups = game.all_sprites, game.starting_lines
        else:
            self.groups = game.all_sprites, game.checkpoints
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.image = pg.Surface((w*TILESIZE,h*TILESIZE))
        self.image.fill(colour)
        self.rect = self.image.get_rect()

        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE 
      