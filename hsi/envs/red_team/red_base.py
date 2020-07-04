import yaml
from pathlib import Path
import numpy as np

from .primitive_manager import PrimitiveManager

from ..state_manager import StateManager
from ..action_manager import ActionManager

from ..agents import UaV, UgV


def get_initial_positions(init_pos, r, n):
    positions = []
    t = np.linspace(0, 2 * np.pi, n)
    x = init_pos[0] + r * np.cos(t)
    y = init_pos[1] + r * np.sin(t)
    positions = np.asarray([x, y, x * 0 + 5]).T.tolist()
    return positions


class RedTeam(object):
    def __init__(self, p, config):
        # Environment parameters
        self.current_time = config['simulation']['current_time']
        self.done = False
        self.config = config

        # Initialize the state and action components
        self.state_manager = StateManager(self.current_time, self.config)
        uav, ugv = self._initial_uxv_setup(p)
        self.state_manager._initial_uxv(uav, ugv)  # Append the UxV
        self.action_manager = ActionManager(self.state_manager, PrimitiveManager)

    def _initial_uxv_setup(self, p):
        # Read the configuration of platoons
        read_path = Path(__file__).parents[1] / 'red_team_config.yml'
        config = yaml.load(open(str(read_path)), Loader=yaml.SafeLoader)

        # Containers
        ugv, uav = [], []
        init_orient = p.getQuaternionFromEuler([np.pi / 2, 0, 0])

        for i, node in enumerate(config['ugv_platoon']['initial_nodes_pos']):
            init_pos = self.state_manager.node_info(node)['position']
            n_vehicles = config['ugv_platoon']['n_vehicles'][i]
            positions = get_initial_positions(init_pos, 4, n_vehicles)
            for j, position in enumerate(positions):
                ugv.append(
                    UgV(p, position, init_orient, j, self.config, 'red'))

        for i, node in enumerate(config['uav_platoon']['initial_nodes_pos']):
            init_pos = self.state_manager.node_info(node)['position']
            n_vehicles = config['uav_platoon']['n_vehicles'][i]
            positions = get_initial_positions(init_pos, 4, n_vehicles)
            for j, position in enumerate(positions):
                uav.append(
                    UaV(p, position, init_orient, j, self.config, 'red'))
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
        return self.action_manager.platoon_attributes(attributes)

    def execute(self):
        """Execute the actions of uav and ugv
        """
        # Execute the actions
        self.action_manager.primitive_execution()
        return None
