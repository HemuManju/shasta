from scipy.spatial.distance import cdist

import numpy as np


def findkeys(node, kv):
    if isinstance(node, list):
        for i in node:
            for x in findkeys(i, kv):
                yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in findkeys(j, kv):
                yield x


def check_perimeter(blue_team_pos, red_team_pos, config):
    """This function checks if the blue team are near red teams using the centroid

        Parameters
        ----------
        red_team_pos : list
            A dictionary containing the states of the red team
        blue_team_pos : list
            A dictionary containing the states of the blue team

        Returns
        -------
        array
            A array mask containing which blue teams are near to red teams
        """
    distance = cdist(blue_team_pos, red_team_pos)
    threshold = config['experiment']['attack_distance']
    indices = np.argwhere(distance < threshold)

    with_in_perimeter = []
    for index in indices:
        blue_key = 'uav_p_' if index[0] <= 2 else 'ugv_p_'
        red_key = 'uav_p_' if index[1] <= 2 else 'ugv_p_'

        # Get the key
        blue_team_key = blue_key + str(index[0] % 3 + 1)
        red_team_key = red_key + str(index[1] % 3 + 1)

        # Update the dictionary
        with_in_perimeter.append([blue_team_key, red_team_key])
    return with_in_perimeter
