import time
import numpy as np

from .base_env import BaseEnv

from .blue_team.blue_base import BlueTeam
from .red_team.red_base import RedTeam  # noqa

from .sensors import Sensors
from .interaction_manager import InteractionManager


class EnhanceEnv(BaseEnv):
    def __init__(self, config):
        # Initialise the base environment
        super().__init__(config)
        self.config = config

        # Load the environment
        if self.config['simulation']['detailed_model']:
            path = '/'.join([
                self.config['urdf_data_path'],
                self.config['simulation']['map_to_use'],
                'environment_collision_free.urdf'
            ])
        else:
            path = '/'.join([
                self.config['urdf_data_path'],
                self.config['simulation']['map_to_use'],
                'environment_collision_free.urdf'
            ])
        self.p.loadURDF(path, [0, 0, 0],
                        self.p.getQuaternionFromEuler([np.pi / 2, 0, 0]),
                        flags=self.p.URDF_USE_MATERIAL_COLORS_FROM_MTL,
                        useFixedBase=True)

        # Initial step of blue and red team
        self._initial_team_setup()

        # Initialize interaction manager
        self.sensors = Sensors(self.p)
        self.interaction_manager = InteractionManager(config)
        return None

    def _initial_team_setup(self):
        # Blue team
        self.blue_team = BlueTeam(self.p, self.config)

        # # Red team
        # self.red_team = RedTeam(self.p, self.config)

        return None

    def reset(self):
        for i in range(50):
            time.sleep(1 / 240)
            self.p.stepSimulation()

    def step(self, blue_actions, red_actions):
        # Roll the actions
        done_rolling_actions = False
        simulation_count = 0
        start_time = time.time()
        current_time = 0
        duration = self.config['simulation']['total_time']

        # Perform action allocation for blue and red team respectively
        self.blue_team.action_manager.perform_action_allocation(
            blue_actions['uav'], blue_actions['ugv'])

        # self.red_team.action_manager.perform_action_allocation(
        #     red_actions['uav'], red_actions['ugv'])

        step_time = []

        # Run the simulation
        while not done_rolling_actions and current_time <= duration:
            simulation_count += 1
            current_time = time.time() - start_time

            # Run the blue team (these can be made parallel)
            action_time = time.time()
            done_rolling_actions = self.blue_team.execute()
            # Perform a step in simulation to update
            self.base_env_step()
            step_time.append(time.time() - action_time)

            # self.sensors.get_camera_image([0, 0, 10], image_type='rgb')

            # # Run the red team (these can be made parallel)
            # self.red_team.execute()
            # # Perform a step in simulation to update
            # self.base_env_step()

            # # Interaction Manager (this over-rides the given actions)
            # self.interaction_manager.update_actions(self.blue_team,
            #                                         self.red_team)
            # Perform a step in simulation to update
            # self.base_env_step()
        # TODO: Need to implement state, action, and reward
        return 1 / np.mean(step_time)

    def get_reward(self):
        """Update reward of all the agents
        """
        # Calculate the reward
        total_reward = self.reward.mission_reward(self.state_manager.ugv,
                                                  self.state_manager.uav,
                                                  self.config)
        for vehicle in self.state_manager.uav:
            vehicle.reward = total_reward

        for vehicle in self.state_manager.ugv:
            vehicle.reward = total_reward
        return total_reward

    def check_episode_done(self):
        done = False
        if self.current_time >= self.config['simulation']['total_time']:
            done = True
        if self.state_manager.found_goal:
            done = True
        return done
