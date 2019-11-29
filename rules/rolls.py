import random

def d(sides):
    """ Create a function that returns a list of [sides] sided dice rolls """
    def roll(num,mod=0):
        """ Returns a [num] long list of random integers in the range 
                from 1 to a preset parameter
            
            paramters:
                num (int)   The number of dice rolls
                mod (int)   Any modifyers being added to each dice roll
        """

        results = [random.randint(1,sides)+mod for _ in range(num)]

        return results

    # return the function
    return roll