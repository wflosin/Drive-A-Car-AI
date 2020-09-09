from gym.envs.registration import register

register(
         id='drive_a_car-v0',
         entry_point='drive_a_car_gym.envs:GameEnv'
         )