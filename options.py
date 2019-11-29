# class Options:
TITLE = "Car Wars"

WIDTH = 1024 # 16 * 64 or 32 * 32 or 64 * 16 etc
HEIGHT = 768

FPS = 60

# 0 for False; 1 for True
TESTING = 0
GRID = 0
RAYS = 1
NOCLIP = 0

#colours
BLACK = (0,0,0)
WHITE = (255,255,255)
LTGREY = (200,200,200)
RED = (255,0,0)
BKGRD = WHITE

#tiles
TILESIZE = 8 # powers of 2
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

# one meter per 7 pixels
SCALE = 1/7

#
DENSITY_OF_AIR = 1.225 #kg/m3