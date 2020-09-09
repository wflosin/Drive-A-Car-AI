#drive_a_car_env.py
#William Losin
#2019-12-03

#inspiration from:
# https://github.com/apoddar573/Tic-Tac-Toe-Gym_Environment/blob/master/gym-tictac4/gym_tictac4/envs/tictac4_env.py

import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np
import main

class GameEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super().__init__()

        self.game = main.Game(ai_active=1,display=1)
        self.game.new()

        # self.counter = 0
        self.done = 0
        # self.add = [0,0]
        self.reward = 0

        #the number of checkpoints the car has crossed
        self.points_i = 0

        self.state = self.reset()

        low = np.array([0 for _ in range(self.game.player.num_rays+2)])
        #1024 being the width of the screen in pixels. 
        # angle in degrees, valocity in m/s
        high = np.array([1024 for _ in range(self.game.player.num_rays)] +
                        [2*self.game.player.max_wheel_angle,self.game.player.speed_limit])

        #|  num  | observation |  min  |  max  |
        #|   0   |  right ray  |   0   | WIDTH |
        #|   1   | centre ray  |   0   | WIDTH |
        #|   2   |  left  ray  |   0   | WIDTH |
        #|   3   | wheel angle |   0   | 2*max |
        #|   4   |  velocity   |   0   |  300  |

        # self.reward_range = (-100,1)
        self.action_space = spaces.Discrete(9)
        self.observation_space = spaces.Box(
            low=low, high=high, dtype='float32')

        self.seed()
                                            
    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def check(self,points_gained,action):
        #checks the rewards
        #crossed checkpoints:
        if points_gained > 0:
            self.reward += 50

        # each frame reduce the reward
        self.reward -= 0.05

        #if the car crashes into a wall
        if not self.game.playing:
            self.reward -= 20
            self.done = 1

        # #if the AI brakes
        # if action in [2,3,6]:
        #     self.reward -= 0.01

        mag_v = np.linalg.norm(self.game.player.v)
        if mag_v < 0.07:
            self.game.playing = False
            self.reward -= 20
            self.done = 1

        # self.reward -= 1/(mag_v+2) 
        # print(self.reward)
        self.game.AI_reward = self.reward

    def step(self, action):
        if self.done:
            print("Game Over!")
            # self.game.quit()
            return [self.state,self.reward,self.done, {}]

        #runs one frame of the game
        #action can be:
        # L, R, LB, RB, LA, RA, B, A, NA
        self.game.run_once(action)

        #calculates if the player crossed a checkpoint
        self.points_f = self.game.player.points
        points_gained = self.points_f - self.points_i
        #for next iteration
        self.points_i = self.points_f

        #allocates rewards for the actions
        self.check(points_gained,action)

        self.state = self.game.drive_data

        return self.state, self.reward, self.done, {}

    def reset(self):
        self.game.player.kill()
        self.game.reset()
        # self.counter = 0
        self.done = 0
        # self.add = [0, 0]
        self.reward = 0
        
        #right ray, forward ray, left ray, wheel angle, velocity
        self.state = np.array([0 for _ in range(self.game.player.num_rays+2)])
        
        self.game.episode += 1
        
        return self.state

    def render(self, mode='human', close=False):
        pass
        # print(self.state)
        # print("reward: ", self.reward)