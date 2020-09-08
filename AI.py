#import 
from main import Game
import gym
import drive_a_car_gym
import numpy as np
from pygame import quit as pgquit

import tensorflow as tf
from keras.models import Sequential 
from keras.layers import Dense, Activation, Flatten 
from keras.optimizers import Adam 
  
from rl.agents.dqn import DQNAgent 
from rl.policy import EpsGreedyQPolicy 
from rl.memory import SequentialMemory 

def make_model():
    environment_name = 'drive_a_car-v0'
    env = gym.make(environment_name)
    np.random.seed(0)
    env.seed(0)

    tf.compat.v1.disable_eager_execution()

    # observation = env.reset()
    # for t in range(1000):
    #     env.render()
    #     action = env.action_space.sample()
    #     print(action)
    #     observation, reward, done, info = env.step(action)
    #     print(observation, reward, done, info)
    #     if done:
    #         print("finished after {} timesteps".format(t+1))
    #         break
    #     print('\n')

    #the maximum number of actions possible
    # L, R, LB, RB, LA, RA, B, A, NA
    num_actions = env.action_space.n
    # print(env.observation_space.shape)

    agent = Sequential()
    agent.add(Flatten(input_shape =(1, ) + (env.observation_space.shape))) #new shape: (None, 5)
    agent.add(Dense(12))#, input_shape=env.observation_space.shape))
    agent.add(Activation('relu'))
    agent.add(Dense(11))#, input_shape=env.observation_space.shape))
    agent.add(Activation('relu'))
    agent.add(Dense(10))#, input_shape=env.observation_space.shape))
    agent.add(Activation('relu'))
    agent.add(Dense(num_actions))
    agent.add(Activation('linear'))

    strategy = EpsGreedyQPolicy()
    memory = SequentialMemory(limit = 50000, window_length=1)
    # print('\nHERE',agent.output.shape[1],'\n')
    dqn = DQNAgent(model = agent, nb_actions = num_actions,
                   memory= memory,
                   target_model_update = 1e-2, policy = strategy)
    dqn.compile(Adam(lr = 1e-3), metrics =['mae'])

    return dqn,env


if __name__ == "__main__":
    dqn,env = make_model()

    dqn.fit(env,
            #nb_max_start_steps=1, 
            nb_steps = 1000000, #400000, #8h 1236052
            nb_max_episode_steps = 2500, #about 1 min 
            visualize = True, 
            verbose = 1, 
            action_repetition = 1)

    # print("Fit complete. Now testing")
    # dqn.test(env, nb_episodes = 5, visualize = True)

    # pgquit()

    print("Saving the model...")
    dqn.model.save('model2.h5',include_optimizer=False)


# dqn.load_weights("model.h5")
"""
after each step, the environment returns these values:

    reward:

        each time step, negative reward
        if cross a checkpoint, reward
        if hit the wall, large negative reward

    observation:
        the observed changes in the game

        ray0
        ray1
        ray2
        wheel angle
        velocity

    done: if the car crashes into a wall

    info: ...
"""


