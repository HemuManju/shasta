import numpy as np

from .utils.interaction import check_perimeter, findkeys
from .utils import magicattr


class InteractionManager(object):
    def __init__(self, config):
        self.config = config
        return None

    def get_team_position(self, blue_team, red_team):
        # Get the attributes
        blue_team_attr = blue_team.get_attributes(['centroid_pos'])
        red_team_attr = red_team.get_attributes(['centroid_pos'])

        # Extract the position from dictionary
        blue_team_pos = list(findkeys(blue_team_attr, 'centroid_pos'))
        red_team_pos = list(findkeys(red_team_attr, 'centroid_pos'))
        return blue_team_pos, red_team_pos

    def _set_action(self, action, n_blue_team, n_red_team, distance):
        action['primitive'] = 'shooting'
        action['n_blue_team'] = n_blue_team
        action['n_red_team'] = n_red_team
        action['distance'] = distance
        return action

    def update_action(self, blue_action, red_action):
        # Calculate distance
        distance = np.linalg.norm(blue_action['centroid_pos'] -
                                  red_action['centroid_pos'])
        n_blue_team = len(blue_action['vehicles'])
        n_red_team = len(red_action['vehicles'])

        # Blue action
        blue_action = self._set_action(blue_action, n_blue_team, n_red_team,
                                       distance)
        red_action = self._set_action(red_action, n_blue_team, n_red_team,
                                      distance)

        return blue_action, red_action

    def set_action(self, team, key, action):
        key_str = self.action_lookup_string(key)
        magicattr.set(team, key_str, action)
        return None

    def get_action(self, team, key):
        key_str = self.action_lookup_string(key)
        action = magicattr.get(team, key_str)
        return action

    def action_lookup_string(self, key):
        vehicle_type = key.split('_')[0]
        action = 'action_manager.' + vehicle_type + '_platoons' + str(
            [key]) + '.action'
        return action

    def update_actions(self, blue_team, red_team):
        # Check the closeness (this function might change)
        blue_team_pos, red_team_pos = self.get_team_position(
            blue_team, red_team)
        with_in_perimeter = check_perimeter(blue_team_pos, red_team_pos,
                                            self.config)

        # Perform actions accordingly
        for keys in with_in_perimeter:

            blue_key = keys[0]
            red_key = keys[1]

            # Get the current action
            blue_action = self.get_action(blue_team, blue_key)
            red_action = self.get_action(red_team, red_key)

            # Update action
            blue_action, red_action = self.update_action(
                blue_action, red_action)

            # Set the new action
            self.set_action(blue_team, blue_key, blue_action)
            self.set_action(red_team, red_key, red_action)
