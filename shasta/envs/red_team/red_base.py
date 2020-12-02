import yaml
from pathlib import Path
import numpy as np

from ..state_manager import StateManager
from ..action_manager import ActionManager

from ..agents.uav import UaV
from ..agents.ugv import UgV


def get_initial_positions(init_pos, r, n):
    positions = []
    t = np.linspace(0, 2 * np.pi, n)
    x = init_pos[0] + r * np.cos(t)
    y = init_pos[1] + r * np.sin(t)
    positions = np.asarray([x, y, x * 0 + 1]).T.tolist()
    return positions


class RedTeam(object):
    def __init__(self, physics_client, config):
        # Environment parameters
        self.current_time = config['simulation']['current_time']
        self.done = False
        self.config = config

        # Initialize the state and action components
        self.state_manager = StateManager(self.current_time, self.config)
        uav, ugv = self._initial_uxv_setup(physics_client)
        self.state_manager._initial_uxv(uav, ugv)  # Append the UxV
        self.action_manager = ActionManager(self.state_manager, physics_client)

    def _initial_uxv_setup(self, physics_client):
        # Read the configuration of platoons
        read_path = Path(
            __file__).parents[2] / 'config/red_team_config_baseline.yml'
        config = yaml.load(open(str(read_path)), Loader=yaml.SafeLoader)

        # Containers
        ugv, uav = [], []
        init_orient = physics_client.getQuaternionFromEuler([np.pi / 2, 0, 0])

        for i, node in enumerate(config['ugv_platoon']['initial_pos']):
            lat = self.state_manager.node_info(node)['y']
            lon = self.state_manager.node_info(node)['x']
            init_pos = np.dot([lat, lon, 1], self.state_manager.A)

            n_vehicles = config['ugv_platoon']['n_vehicles'][i]
            positions = get_initial_positions(init_pos, 10, n_vehicles)
            for j, position in enumerate(positions):
                ugv.append(
                    UgV(physics_client, position, init_orient, i, j,
                        self.config, 'red'))

        for i, node in enumerate(config['uav_platoon']['initial_pos']):
            lat = self.state_manager.node_info(node)['y']
            lon = self.state_manager.node_info(node)['x']
            init_pos = np.dot([lat, lon, 1], self.state_manager.A)

            n_vehicles = config['uav_platoon']['n_vehicles'][i]
            positions = get_initial_positions(init_pos, 10, n_vehicles)
            for j, position in enumerate(positions):
                uav.append(
                    UaV(physics_client, position, init_orient, i, j,
                        self.config, 'red'))
        return uav, ugv

    def reset(self):
        """
        Resets the position of all the robots
        """
        for vehicle in self.state_manager.uav:
            vehicle.reset()

        for vehicle in self.state_manager.ugv:
            vehicle.reset()

        done = False
        return done

    def get_attributes(self, attributes):
        return self.action_manager.get_actions(attributes)

    def execute(self):
        """Execute the actions of uav and ugv
        """
        # Execute the actions
        self.action_manager.primitive_execution()
        return None
