from AI import make_model

if __name__ == "__main__":
    dqn,env = make_model()

    dqn.load_weights("model.h5")

    dqn.test(env, nb_episodes = 5, visualize = True)
