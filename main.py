import pygame as pg
import numpy as np
from options import *
from sprites import player, cars, walls
import os,sys
import time

class Game:
    def __init__(self):
        # initialize the game window
        
        pg.init()
        # pg.mixer.init()
        
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)

        self.clock = pg.time.Clock()
        #send an event after 500 ms, then after every 100 ms
        # pg.key.set_repeat(500, 100)
        pg.key.set_repeat(1, 1)

        self.gamefont = pg.font.SysFont('Eras', WIDTH//57)
        self.screen.fill((WHITE))

    def spawn_player(self):
        self.player = player.Player(self,440,48,0)

    def new(self):
        # initialize all the variables and do all the setup for the new game
        self.all_sprites = pg.sprite.Group()
        #sprite group of for all the cars
        self.vehicles = pg.sprite.Group()
        #sprite sgroup for characters of of their cars
        self.players = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.checkpoints = pg.sprite.Group()
        self.starting_lines = pg.sprite.Group()

        #initialize the player
        self.spawn_player()

        #initialize the starting line
        self.starting_line = walls.Checkpoint(self,61,2,h=13,colour=(150,0,0),start=True)

        # self.coin = walls.Coin(self, 10,10)

        # self.mice = pg.sprite.Group()
        # self.mouse = Sprite_Mouse_Location(game,0,0)

        #spawn the wall sprites and checkpoints
        self.load_data()
        for row, tiles in enumerate(self.map_data):
            for col, tile in enumerate(tiles):
                if tile == 'X':
                    walls.Wall(self, col, row)

        self.create_checkpoints()
           
    def create_checkpoints(self):
        for row, tiles in enumerate(self.map_data):
            for col, tile in enumerate(tiles):
                #vertical checkpoints
                if tile == 'v':
                    row_count = 1
                    while row_count < HEIGHT/TILESIZE:
                        if self.map_data[row+row_count][col] == 'V':
                            walls.Checkpoint(self, col, row, h=(row_count+1))
                            break
                        row_count += 1
                # #horizontal checkpoints
                if tile == 'h':
                    col_count = 1
                    while col_count < HEIGHT/TILESIZE:
                        if tiles[col+col_count] == 'H':
                            walls.Checkpoint(self, col, row, w=(col_count+1))
                            break
                        col_count += 1  

    def load_data(self):
        game_folder = os.path.dirname(__file__)
        with open(os.path.join(game_folder, 'rules','map.txt'), 'rt') as f:
            self.map_data = [line for line in f]

    def run(self):
        # game loop
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.event_drive()
            self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LTGREY, (x,0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LTGREY, (0, y), (WIDTH, y))

    def draw(self):
        self.screen.fill(BKGRD)
        if GRID:
            self.draw_grid()
        # self.all_sprites.draw(self.screen)
        self.walls.draw(self.screen)
        self.checkpoints.draw(self.screen)
        self.starting_lines.draw(self.screen)
        self.players.draw(self.screen)


        self.custom_message(str(self.player.points),(2,2),40)

        #traces the rays used so the car knows its own position (used for AI)
        if RAYS:
            self.draw_rays()
        
        if TESTING:
            self.debug()
        pg.display.flip()

    def draw_rays(self):
        self.player.ray_trace()
        #draws the rays that were traced
        for ray in self.player.ray_lines:
            # print(ray[0], ray[1])
            pg.draw.line(self.screen, (0,0,255), ray[0], ray[1] )

    def debug(self):
        #draws the velocity vector from the center of the car
        pg.draw.line(self.screen, (255,0,0),(self.player.rect.center[0],self.player.rect.center[1]),(self.player.rect.center[0]+self.player.v[0],self.player.rect.center[1]+self.player.v[1]))
        self.message("x (in metres): "+str(self.player.x),(100,64))
        self.message("y (in metres): "+str(self.player.y),(100,80))
        self.message("velocity (m/s):"+str(round(np.linalg.norm(self.player.v),4))+', '+str(round(self.player.v[0],4))+', '+str(round(self.player.v[1],4)),(100,96))
        self.message("velocity (km/h):"+str(round(np.linalg.norm(self.player.v)*3.6,4))+', '+str(round(self.player.v[0]*3.6,4))+', '+str(round(self.player.v[1]*3.6,4)),(100,112))
        self.message("acceleration (m/s/s):"+str(round(self.player.a[0],4))+', '+str(round(self.player.a[1],4)),(100,128)) 
        self.message("net force: "+str(self.player.F_net), (100,144))
        #draws the force vector from the center of the car
        pg.draw.line(self.screen, (0,255,0),(self.player.rect.center[0],self.player.rect.center[1]),(self.player.rect.center[0]+self.player.F_net[0]/500,self.player.rect.center[1]+self.player.F_net[1]/500))
        self.message("angle: "+str(self.player.angle),(100,160))
        self.message("wheel angle: "+str(self.player.wheel_angle),(100,176))

    def event_drive(self):
        global TESTING,GRID,RAYS,NOCLIP
        # catches and handles all events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_UP:
                    self.player.accel = 1
                elif event.key == pg.K_DOWN:
                    self.player.accel = -1
                if event.key == pg.K_LEFT:
                    self.player.turn = 1
                elif event.key == pg.K_RIGHT:
                    self.player.turn = -1
                if event.key == pg.K_SPACE:
                    self.player.brake = True

                # #create map
                # if event.key == pg.K_m:
                #     mapp = np.zeros((HEIGHT//TILESIZE,WIDTH//TILESIZE),dtype="int")
                #     for wall in self.walls:
                #         x = wall.rect.x // TILESIZE
                #         y = wall.rect.y // TILESIZE
                #         mapp[y][x] = 1
                #     with open('map.txt','w') as f:
                #         f.write( np.array2string(mapp,separator='',threshold=10000000000000).replace("[","").replace("]","").replace(' ','').replace('0','.').replace('1','X') )
                #     self.quit()

                   
            if event.type == pg.KEYUP:
                # keys = pg.key.get_pressed()
                if event.key in [pg.K_UP,pg.K_DOWN]:
                    self.player.accel = 0
                if event.key in [pg.K_LEFT,pg.K_RIGHT]:
                    self.player.turn = 0
                if event.key == pg.K_SPACE:
                    self.player.brake = False                
                if event.key == pg.K_d:
                    TESTING = 1 - TESTING
                if event.key == pg.K_g:
                    GRID = 1 - GRID
                if event.key == pg.K_r:
                    RAYS = 1 - RAYS   
                if event.key == pg.K_n:
                    NOCLIP = 1 - NOCLIP
                    if RAYS:
                        RAYS = 0         
            
            # #draw walls
            # if event.type == pg.MOUSEBUTTONUP:
            #     self.mouse.pressed = False
            # elif event.type == pg.MOUSEBUTTONDOWN or self.mouse.pressed:
            #     self.mouse.pressed = True
            #     mouse_pos = pg.mouse.get_pos()
            #     x = mouse_pos[0]//TILESIZE
            #     y = mouse_pos[1]//TILESIZE
            #     collide = False
            #     for wall in self.walls:
            #         collide = pg.sprite.collide_rect(wall,self.mouse)
            #     if not collide:
            #         walls.Wall(self, x, y)


        self.player.move(self.dt)

        #checks if the player collides with a checkpoint
        self.player.check_cross_checkpoint(self.checkpoints)

        if not NOCLIP and self.player.collide_with_walls(self.walls):
            self.player.kill()
            self.create_checkpoints()
            self.spawn_player()

        if self.player.check_cross_starting_line() \
                and (self.player.points % 20 == 0) \
                and (self.player.points > (20*self.player.laps)):
            self.player.laps += 1
            self.create_checkpoints()

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        pass

    def message(self,message,pos):
        text = self.gamefont.render(message,0,RED)
        self.screen.blit(text, pos)

    def custom_message(self,message,pos,size,colour=BLACK):
        text = pg.font.SysFont('Eras', size).render(message,0,colour)
        self.screen.blit(text, pos)        

# class Sprite_Mouse_Location(pg.sprite.Sprite):
#     def __init__(self,game,x,y):
#         self.groups = game.all_sprites, game.mice
#         pg.sprite.Sprite.__init__(self, self.groups)
#         self.game = game

#         self.image = pg.Surface((1,1))

#         self.rect = pg.Rect(x,y,1,1)

#         self.pressed = False

#     def update(self):
#         self.rect.x, self.rect.y = pg.mouse.get_pos()


# create game object
game = Game()
game.show_start_screen()
while True:
    game.new()
    game.run()
    game.show_go_screen()