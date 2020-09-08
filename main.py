# Drive A Car
# version: 0.0.1
#
# William Losin
# 2019-11-23
# github.com/wflosin

import pygame as pg
import numpy as np
from options import *
from sprites import player, walls
import os,sys
# import time

class Game:
    def __init__(self,display=1,ai_active=0):
        #toggle settings
        self.DISPLAY = display
        self.TESTING = 0
        self.GRID = 0
        self.RAYS = 1
        self.NOCLIP = 0
        self.SAVEDATA = 0
        self.AI_ACTIVE = ai_active

        # initialize the game window
        # print('here')
        pg.init()

        self.screen = pg.display.set_mode((WIDTH, HEIGHT))

        if self.DISPLAY:
            pg.display.set_caption(TITLE)
            self.gamefont = pg.font.SysFont('Eras', WIDTH//57)
            self.screen.fill((WHITE))

        self.clock = pg.time.Clock()
        #send an event after 500 ms, then after every 100 ms
        # pg.key.set_repeat(500, 100)
        pg.key.set_repeat(1, 1)

        self.AI_reward = 0
        self.episode = 0

        #The background image, which smooths out walls
        self.background_image = pg.image.load(os.path.join('rules','bkgrd_map.png')).convert_alpha()


    def spawn_player(self):
        self.player = player.Player(self,440,48,0,velocity=(3,0))

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

        #move data
        self.drive_data = []
        self.time = 0

        self.playing = 1

        #initialize the starting line
        self.starting_line = walls.Checkpoint(self,61,2,h=13,colour=(150,0,0),start=True)

        # self.coin = walls.Coin(self, 10,10)

        # self.mice = pg.sprite.Group()
        # self.mouse = Sprite_Mouse_Location(game,0,0)

        #spawn the wall sprites and checkpoints
        self.load_map()
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

    def reset(self):
        #initialize the player
        self.spawn_player()

        #move data
        self.drive_data = []
        self.time = 0

        self.playing = 1
        self.create_checkpoints()

    def load_map(self):
        game_folder = os.path.dirname(__file__)
        #open and load the map data
        with open(os.path.join(game_folder, 'rules','map.txt'), 'rt') as f:
            self.map_data = [line for line in f]

    def run(self):
        # game loop
        self.playing = True
        while self.playing:
            self.run_once()

    def run_once(self,action=None):
        # self.dt = self.clock.tick(FPS) / 1000
        self.dt = 0.024#0.11#0.006
        # print(self.dt)
        self.time += self.dt

        #event loop 
        if self.AI_ACTIVE:
            self.event_drive_AI(action)
        else:
            self.event_drive()

        self.move_player()
        self.update()
        if self.DISPLAY:
            self.draw(action)

    def quit(self):
        # pg.image.save(self.screen,'background.png')
        print("quit")
        if self.SAVEDATA:
            with open('drive_data.csv','w') as f:
                headers = 'time,-45 ray,0 ray,45 ray,wheel angle,velocity\n'
                f.write(headers+str(self.drive_data).replace('[','').replace('],','\n').replace(']','').replace(', ',','))
        self.playing = 0
        
        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()

        #updates the observables
        self.drive_data = np.array(
            # self.player.ray_length[0]/WIDTH, # 0 to 1; this assumes the ray will not
            # self.player.ray_length[1]/WIDTH, # 0 to 1;  go further than the WIDTH of
            # self.player.ray_length[2]/WIDTH, # 0 to 1;  the screen
            # (self.player.wheel_angle+self.player.max_wheel_angle)/(2*self.player.max_wheel_angle), # 0 to 1
            # np.linalg.norm(self.player.v)/300]) # 0 to 1; 300 being roughly the max speed
            self.player.ray_length +
            [self.player.wheel_angle+self.player.max_wheel_angle, #so that all the mins are 0 
            np.linalg.norm(self.player.v)])

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LTGREY, (x,0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LTGREY, (0, y), (WIDTH, y))

    def draw(self,action=None):
        self.screen.fill(BKGRD)
        self.screen.blit(self.background_image,(0,0))
        if self.GRID:
            self.draw_grid()
        # self.all_sprites.draw(self.screen)
        self.walls.draw(self.screen)
        self.checkpoints.draw(self.screen)
        self.starting_lines.draw(self.screen)
        
        self.custom_message(str(self.player.points),(2,2),40,colour=WHITE)

        #traces the rays used so the car knows its own position (used for AI)
        if self.RAYS or self.AI_ACTIVE:
            self.draw_rays()
        if self.AI_ACTIVE:
            self.draw_AI_details(action)  
        self.players.draw(self.screen)
        if self.TESTING:
            self.debug()
        if self.DISPLAY:
            pg.display.flip()

    def draw_AI_details(self,action):
        self.custom_message("reward: " + str(self.AI_reward),(460,500),15,colour=(255,0,0))
        self.custom_message("action: %i"%(action),(460,520),15,colour=(255,0,0))
        self.custom_message("Episode: %s"%(self.episode),(460,540),15,colour=(255,0,0))

    def draw_rays(self):
        #requires that the walls are already drawn

        if self.SAVEDATA:
            #stores the data
            self.drive_data.append( [self.time] +
                                     self.player.ray_length +
                                     [self.player.wheel_angle,
                                     np.linalg.norm(self.player.v)] )
        
        #updates the ray information
        self.player.ray_trace()
        
        #draws the rays that were traced
        for ray in self.player.ray_lines:
            if ray:
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

    def move_player(self):
        self.player.move(self.dt)

        #checks if the player collides with a checkpoint
        self.player.check_cross_checkpoint()

        #if the player hits a wall
        if not self.NOCLIP and self.player.collide_with_walls(self.walls):
            if self.SAVEDATA:
                self.quit()
            
            #resets the car
            if not self.AI_ACTIVE:
                #NOTE: the player is killed by the AI not here
                self.player.kill()
                self.create_checkpoints()
                self.spawn_player()
            else:
                # self.quit()
                self.playing = 0

        # #if the player crosses the start/finish line
        # if self.player.check_cross_starting_line() \
        #         and (self.player.points % 22 == 0) \
        #         and (self.player.points > (20*self.player.laps)):
        #     self.player.laps += 1
        #     self.create_checkpoints()
        self.player.check_cross_starting_line()

    def event_drive_AI(self,action):
        # catches if the user closes the window
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()

        #all the possible action the AI can take
        # turn left or right
        # accelerate or brake
        if action in ['L',0]:
            self.player.accel = 0
            self.player.turn = 1
            self.player.brake = 0
        elif action in ['R',1]:
            self.player.accel = 0
            self.player.turn = -1
            self.player.brake = 0
        elif action in ['LB',2]:
            self.player.accel = 0
            self.player.turn = 1
            self.player.brake = True
        elif action in ['RB',3]:
            self.player.accel = 0
            self.player.turn = -1
            self.player.brake = True
        elif action in ['LA',4]:
            self.player.accel = 1
            self.player.turn = 1
            self.player.brake = False
        elif action in ['RA',5]:
            self.player.accel = 1
            self.player.turn = -1
            self.player.brake = False
        elif action in ['B',6]:
            self.player.accel = 0
            self.player.turn = 0
            self.player.brake = True
        elif action in ['A',7]:
            self.player.accel = 1
            self.player.turn = 0
            self.player.brake = False            
        else:
            self.player.accel = 0
            self.player.turn = 0
            self.player.brake = 0

    def event_drive(self):
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
                    self.TESTING = 1 - self.TESTING
                if event.key == pg.K_g:
                    self.GRID = 1 - self.GRID
                if event.key == pg.K_r:
                    self.RAYS = 1 - self.RAYS   
                if event.key == pg.K_n:
                    self.NOCLIP = 1 - self.NOCLIP
                    if RAYS:
                        self.RAYS = 0         
            
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

def start_game():
    game = Game()
    # game.show_start_screen()
    while True:
        game.new()
        game.run()
        # game.show_go_screen()

# create game object
if __name__ == '__main__':
    start_game()