import time
import numpy as np

from .base_env import BaseEnv

from .blue_team.blue_base import BlueTeam

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

        return None

    def reset(self):
        for i in range(50):
            time.sleep(1 / 240)
            self.p.stepSimulation()

    def step(self, blue_actions):
        # Roll the actions
        done_rolling_actions = False
        simulation_count = 0
        start_time = time.time()
        current_time = 0
        duration = self.config['simulation']['total_time']

        # Perform action allocation for blue and red team respectively
        self.blue_team.action_manager.perform_action_allocation(
            blue_actions['uav'], blue_actions['ugv'])

        step_time = []

        # self.p.startStateLogging(loggingType=self.p.STATE_LOGGING_VIDEO_MP4,
        #                          fileName='rochester.mp4',
        #                          physicsClientId=self.p._client)

        t = time.time()
        running = True
        entered = False

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
            pos = self.blue_team.state_manager.uav[2].current_pos
            pos[2] = pos[2] + 5

            key_pos = np.dot([42.88599, -78.8755, 1],
                             self.blue_team.state_manager.A)
            key_pos[2] = pos[2]
            distance = np.linalg.norm(pos - key_pos)

            if distance < 5 and running:
                self.p.startStateLogging(
                    loggingType=self.p.STATE_LOGGING_VIDEO_MP4,
                    fileName='testing.mp4',
                    physicsClientId=self.p._client)
                entered = True
                running = False

            if entered and distance > 80:
                pos = self.blue_team.state_manager.ugv[2].current_pos
                pos[2] = pos[2] + 5

            if time.time() - t > 200:
                break
                # if running:
                #     self.p.startStateLogging(
                #         loggingType=self.p.STATE_LOGGING_VIDEO_MP4,
                #         fileName='testing.mp4',
                #         physicsClientId=self.p._client)
                #     running = False

            self.p.resetDebugVisualizerCamera(cameraDistance=10,
                                              cameraYaw=75,
                                              cameraPitch=5,
                                              cameraTargetPosition=pos)

            # self.sensors.get_camera_image([0, 0, 10], image_type='rgb')

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
