import numpy as np


class Shooting(object):
    def __init__(self):
        return None

    def shoot(self, n_team_blue, n_team_red, distance, type):
        if type == 'red':
            loc = n_team_red / n_team_blue
        else:
            loc = n_team_blue / n_team_red
        p = np.random.normal(loc / distance**2, scale=0.75)
        return p

    def shoot_original(self):
        pass
