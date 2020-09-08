import pygame as pg
from options import TILESIZE, SCALE, DENSITY_OF_AIR, WIDTH, HEIGHT, BLACK
import numpy as np
import time,sys
# from sprite.spritesheet import Spriesheet
import os
# from cars import Cars

class Player(pg.sprite.Sprite):
    def __init__(self,game,x,y,angle,velocity=[0,0]):
        self.groups = game.all_sprites, game.players
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.points = 0
        self.laps = 0

        # initializes the sprite screen
        # self.image = pg.Surface((TILESIZE,TILESIZE))
        self.original_image = pg.image.load(os.path.join('sprites','REDCAR','CARF_sml.png')).convert_alpha()#pg.Surface((TILESIZE,TILESIZE))
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.x = x * SCALE #m
        self.rect.y = y * SCALE #m
        self.x = self.rect.x
        self.y = self.rect.y

        # valocity in m/s
        self.v = np.array(velocity,dtype="float32") #26.8224
        self.a = np.array([0,0],dtype="float32")

        self.rect.center = (x,y) #pixels
        self.angle = angle #degrees

        self.coef_fric = 0.026 #from an audi
        self.mass = 1187 #kg
        self.grav = 9.8 #m/s/s
        #self.dampen = 0.9

        # base acceleration of the vehicle
        self.base_a = 4.5 #m/s/s

        #for a 2001 Honda civic
        self.drag_coef = 0.36 #unitless
        self.area = 1.894 #m^2 

        self.wheelbase = 2.61874 #m
        self.turning_radius = 5.19684 #m radius
        self.car_width = 1.69418 #m
        self.max_wheel_angle = np.arctan(self.wheelbase / (self.turning_radius - self.car_width)) *180/np.pi
        # self.max_steering_wheel_angle = 578 # degrees
        self.max_steering_speed =  963 /2 # degrees/s   #/2 to be more realistic 
        #x degrees on the steering wheel translates to 1 degree on the wheels
        self.turning_ratio = 10.9 #:1 2019 honda civic 
        self.turning_speed = 15 #degrees/s
        self.wheel_angle = 0 #degrees

        #34.44 meter stop distance 
        #should stop in 241.08 pixels
        # stopping from 26.8224 m/s
        # around 4.6 seconds
        self.brake_factor = 40.2

        #calculates the car's max speed based on internal friction and air resistance
        self.speed_limit = np.sqrt((self.mass*(self.base_a)-(self.coef_fric*self.grav)) \
                            / (0.5*DENSITY_OF_AIR*self.area*self.drag_coef)) #m/s

        # self.ss = Spriesheet("sprites/REDCAR/CAR.png")
        # self.main_images = self.ss.load_strip((0,0,32))
        self.start = None
        self.F_net = np.array([0,0])

        #paramters to be passed to the move function
        self.accel = 0        
        self.turn = 0
        self.brake = False

        #rays traved from the centre of the car to the wall in three directions
        self.num_rays = 5
        self.ray_length = [0 for _ in range(self.num_rays)]
        self.ray_lines = [None for _ in range(self.num_rays)]

    def move(self,dt):
        #moves the car
        #print('\n')
        ###time stuff
        if not self.start:
            self.start = time.time()
        ###
        is_car_moving = (round(self.v[0],1) != 0 or round(self.v[1],1) != 0)

        ##################calculating the new force on the car#################################
        #NO DIRECTION
        if self.accel and not self.brake:
            F_accel = self.accel * self.mass * self.base_a
        else:
            F_accel = 0

        if is_car_moving:
            F_friction = self.coef_fric*self.mass*self.grav
        else:
            F_friction = 0

        if self.brake:
            F_friction *= self.brake_factor

        #uses the velocity from last frame
        F_drag = 0.5 * DENSITY_OF_AIR * (np.linalg.norm(self.v))**2 * self.drag_coef * self.area

        #the net force applied to the car.  If the car is going backwards (if the direction the car is facing 
        # is opposite of the direction of the vlocity), then flip the signs of the friction and the drag
        F_net = F_accel - (F_friction + F_drag) #* -(np.cos(np.pi*(direction == direction_v))) 
        #print("Forces: ", F_accel, F_friction, F_drag, self.F_net)
        #######################################################################################

        ####################
        #NO DIRECTION
        a = F_net/self.mass
        v_0 = self.v
        mag_v_0 = np.linalg.norm(v_0)
        mag_v = mag_v_0 + a*dt
        #s for position
        mag_s = mag_v * dt
        ####################

        #get the direction of the velocity.  If the car is still, the direction is equal
        # to the direction of the car
        # mag_v = np.linalg.norm(self.v)
        # if is_car_moving:
        #     direction_v = self.v/mag_v
        # else:
        #     direction_v = self.get_norm_vector(self.angle)

        # #print('\n',"x velocity: ",round(self.v[0],4))
        #if the car is going slow enough, set v to 0
        #print("mag velocity: ",abs(mag_v))
        if mag_v < 0.07 and is_car_moving:
            # self.v[0], self.v[1] = (0,0)
            mag_v = 0
            # end = time.time()
            # print("time diff: ",round(end-self.start,4),' seconds')
            # print("distance: ",self.x,' m')
            # pg.quit()
            # sys.exit()
        # speed test
        # if mag_v > 100/3.6:


        #print("new mag velocity: ",abs(np.linalg.norm(self.v)))

        ### calculating the angular kinematics of the car ###################################
        #turn is -1,0,or 1 which determines the direction of the turn

        #turns the steering wheel back to its position at angle 0
        amount_turned = (dt*self.max_steering_speed/self.turning_ratio) #s * degrees/s
        #print("amount_turned: ",amount_turned)
        # if the player does not turn the steering wheel
        if not self.turn and self.wheel_angle != 0:
            #turns the wheel in the opposite direction than it is already turned
            sign_wheel = np.sign(self.wheel_angle)
            self.wheel_angle += amount_turned * -sign_wheel
            #if the wheel angle crosses 0, make it 0
            if np.sign(self.wheel_angle) != sign_wheel:
                self.wheel_angle = 0
            # self.wheel_angle = 0

        #turns the wheel in the direction the player chooses
        else:
            self.wheel_angle += self.turn * amount_turned
        # if self.game.AI_ACTIVE:
        #     if not self.turn: #############
        #         self.wheel_angle = 0 ##############
        #print("turn: ",self.turn)
        #print('wheel angle: ',self.wheel_angle)

        #if the angle surpasses the maximum turn angle
        #the equation to compare to is negative exponential so that you can 
        # only turn so much when going at high speeds
        wheel_angle_based_on_velocity = (self.max_wheel_angle**(-((mag_v/109)-1)))
        if abs(self.wheel_angle) > wheel_angle_based_on_velocity:
            self.wheel_angle = wheel_angle_based_on_velocity * np.sign(self.wheel_angle)
        # if the angle is close to 0, snap it to 0
        elif abs(self.wheel_angle) < 0.01:
            self.wheel_angle = 0
        
        #if the car is moving and the wheel has an angle, update the direction of the car
        if is_car_moving and self.wheel_angle != 0:

            #the direction that the car is facing
            #print("angle: ", self.angle)
            #print("wheel angle: ", self.wheel_angle)
            # direction = self.get_norm_vector(self.angle + (self.wheel_angle/2))
            
            #turns the car - turns faster based on the velocity and the current angle of the wheel
            #this combines two equations:
            # 1. angle(radians) = s/r #with r being the turning radius based on the wheel angle
            #       s being the arc length that the car travels this frame
            # 2. wheel_angle = arctan(wheelbase / (r - car_width))
            theta_0 = self.angle
            current_turn_radius = (self.wheelbase/np.tan(self.wheel_angle*np.pi/180) + self.car_width)
            # self.angle -= (mag_v * dt * 180 / (2 * current_turn_radius))
            self.angle -= (mag_s / current_turn_radius) * 180/np.pi
            # d_theta = self.angle - theta_0

            #this angle is very important: it is the direction that the system moves the vehicle.
            # What would happen in real life:
            #  1. car is facing the initial direction
            #  2. car travels in a circular pattern
            #  3. ends up at a final angle, still tangent to the curve it followed
            # What this system does:
            #  1. car is facing the initial direction
            #  2. caclulates the final angle of the car
            #  3. takes the average of the average of the two angles
            #  4. rather tan travelling across the arc of the circle in one frame, it travels
            #       in a a stright line in the direction of the average of the two angles
            #  5. the amount traveled is compensated for due to the car not traveling across the arc
            direction = self.get_norm_vector((theta_0 + self.angle) / 2)

            #print("new angle: ", self.angle)

            #this uses a new set of coordinates
            degrees_turned = mag_s/current_turn_radius #radians
            #distance
            mag_d = 2*current_turn_radius*np.sin(degrees_turned/2) #m
            #transform into the base coordinate set
            self.x += mag_d * direction[0]
            self.y += mag_d * direction[1] 

        else:
            direction = self.get_norm_vector(self.angle)
            self.x += mag_s * direction[0]
            self.y += mag_s * direction[1]
        #print("direction: ",direction)

        #checks if the car is going backwards
        # if direction[0] != direction_v[0] or direction[1] != direction_v[1]:
        #     #print("going backwards")
        #     direction *= -1

        ######################################################################################

        ### updating the variables ############################################################
        #the total acceleration in the given direction
        self.a = a * direction
        #print("acceleration: ", self.a)
        self.F_net = F_net * direction
        # #new position of the car
        # self.x += v_0[0]*dt + 0.5*self.a[0]*dt**2
        # self.y += v_0[1]*dt + 0.5*self.a[1]*dt**2
        
        #new velocity (used for debuggings and future iterations)
        self.v = mag_v * direction
        # self.v = v_0 + self.a*dt
        #print("velocity: ", self.v)
        ########################################################################################

    def ray_trace(self):
        """
        This is used to determine the distance away from the wall the car is via ray tracing.
        Obtains the length of each of the rays which will be optimized in the neural network.
        Obtains the start and end x and y values to be used for drawing the rays for debugging.
        """
        rays = [self.get_ray_line(-self.angle + item) for item in [-80,-30,0,30,80]]
        self.ray_length = [0 for _ in range(self.num_rays)]
        self.ray_lines = [None for _ in range(self.num_rays)]

        for i,ray in enumerate(rays):
            start_x, start_y = self.rect.center
            x,y = self.rect.center
            while (0<=x<WIDTH-10) and (0<=y<HEIGHT-10):
                # print(x,y,self.game.screen.get_at((int(x),int(y))))
                try:
                    point_colour = self.game.screen.get_at((int(x),int(y)))
                except IndexError:
                    print("index error")
                    point_colour = None
                # print(x,y,point_colour)
                #makes it so there needs to be whitespace before the wall
                if point_colour == (1,1,1,255):
                    self.ray_length[i] = np.sqrt((x-start_x)**2 + (y-start_y)**2) * SCALE
                    self.ray_lines[i] = ((start_x,start_y),(x,y))
                    break
                # point_colour_0 = point_colour_f

                #increases or decreases the x value depending on which direction the ray is going
                x += ray[0] /2
                y -= ray[1] /2
                


    def get_ray_line(self,angle):
        """
        Returns a np.array object containing the rise and run values required for ray tracing
        """
        return self.get_norm_vector(angle) * TILESIZE

    def collide_with_walls(self, walls):
        """
        returns True if the car collides with a wall or the edge of the map
        """
        #make a smaller hit box so that the car does not clip corners
        sml_rect = pg.Rect(self.rect.centerx-8,self.rect.centery-8,16,16)
        if WIDTH < self.rect.x < 0 or HEIGHT < self.rect.y < 0:
            return True
        for wall in walls:
            if pg.Rect.colliderect(sml_rect,wall.rect):
                return True

    def check_cross_checkpoint(self):
        """
        returns a checkpoint if the car crosses one
        """        
        for checkpoint in self.game.checkpoints:
            if pg.sprite.collide_rect(self,checkpoint):
                checkpoint.kill()
                self.points += 1     

    def check_cross_starting_line(self):
        if pg.sprite.collide_rect(self,self.game.starting_line) \
                and len(self.game.checkpoints) == 0:

            for checkpoint in self.game.checkpoints:
                checkpoint.kill()
            self.laps += 1
            self.game.create_checkpoints()

    def get_angle(self,v):
        # #print(v)
        if v[0] == 0:
            if v[1] > 0 :
                return 90
            elif v[1] < 0:
                return 170

        angle = 0
        if v[0] < 0:
            angle = 180
        elif v[0] > 0 and v[1] < 0:
            angle = 360

        return np.arctan(v[1]/v[0])*180/np.pi + angle

    def get_norm_vector(self,angle):
        """ 
        Takes in an angle in degrees and returns a normalized vector
        of the given angle.
        """
        threshold = 0.00000001
        rad = angle *np.pi/180
        x = np.cos(rad)
        y = np.sin(rad)
        if abs(x) < threshold:
            x = 0
        if abs(y) < threshold:
            y = 0
        vector = np.array([x,y],dtype="float32")
        return vector/np.linalg.norm(vector)

    # def change_image(self):
    #     self.angle = self.angle(self.v)
    #     interval = 11.45
    #     if -interval < self.rot < interval:
    #         pass

    def update(self):
        # #print("update; x: ",self.x)
        # self.rect.x = (self.x+10) /SCALE #* TILESIZE
        # self.rect.y = (self.y+10) /SCALE

        #draws the car around the top left coordinate of the image.
        # the forces are now applied to the center of mass
        self.rect.center = (self.x/SCALE, self.y/SCALE)

        # if self.v[0] != 0 or self.v[1] != 0:
        #     self.angle = self.get_angle(self.v)

        #     self.angle -= 1 % 360 +1 # Value will reapeat after 359. This prevents angle to overflow.
        self.image = pg.transform.rotate(self.original_image, -self.angle)# + 1 % 360)
        # #print(self.angle)

        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.rect.center = (x, y)  # Put the new rect's center at old center.
        # print(self.rect)
        # print(self.rect.width/2)
        # self.rect.x = (self.x - self.rect.width/2) /SCALE #* TILESIZE
        # self.rect.y = (self.y - self.rect.height/2) /SCALE

