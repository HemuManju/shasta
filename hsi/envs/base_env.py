import math

import numpy as np

import pybullet as p
import pybullet_data
from pybullet_utils import bullet_client


class BaseEnv(object):
    def __init__(self, config):
        self.config = config
        # Usage mode
        if config['simulation']['headless']:
            self.p = bullet_client.BulletClient(connection_mode=p.DIRECT)
        else:
            self.p = bullet_client.BulletClient(connection_mode=p.GUI)
            self.p.resetDebugVisualizerCamera(cameraDistance=150,
                                              cameraYaw=0,
                                              cameraPitch=-89.999,
                                              cameraTargetPosition=[0, 80, 0])
        # Set gravity
        self.p.setGravity(0, 0, -9.81)
        self.p.setAdditionalSearchPath(pybullet_data.getDataPath())  # optional

        # Set parameters for simulation
        self.p.setPhysicsEngineParameter(
            fixedTimeStep=config['simulation']['time_step'] / 10,
            numSubSteps=1,
            numSolverIterations=5)
        # self.p.setRealTimeSimulation(1)

        self.p.configureDebugVisualizer(self.p.COV_ENABLE_GUI, 0)

        # Setup ground
        plane = self.p.loadURDF("plane.urdf", [0, 0, 0],
                                self.p.getQuaternionFromEuler(
                                    [0, 0, math.pi / 2]),
                                useFixedBase=True,
                                globalScaling=20)
        self.p.changeVisualShape(plane, -1)
        return None

    def base_env_get_camera_image(self):
        """Get the camera image of the scene

        Returns
        -------
        tuple
            Three arrays corresponding to rgb, depth, and segmentation image.
        """
        upAxisIndex = 2
        camDistance = 500
        pixelWidth = 350
        pixelHeight = 700
        camTargetPos = [0, 80, 0]

        far = camDistance
        near = -far
        view_matrix = self.p.computeViewMatrixFromYawPitchRoll(
            camTargetPos, camDistance, 0, 90, 0, upAxisIndex)
        projection_matrix = self.p.computeProjectionMatrix(
            -90, 60, 150, -150, near, far)
        # Get depth values using the OpenGL renderer
        width, height, rgbImg, depthImg, segImg = self.p.getCameraImage(
            pixelWidth,
            pixelHeight,
            view_matrix,
            projection_matrix,
            renderer=self.p.ER_BULLET_HARDWARE_OPENGL)
        return rgbImg, depthImg, segImg

    def base_env_get_initial_position(self, agent, n_agents):
        grid = np.arange(n_agents).reshape(n_agents // 5, 5)
        pos_xy = np.where(grid == agent)
        return [pos_xy[0][0] * 20 + 10, pos_xy[1][0] * 20]

    def base_env_step(self):
        self.p.stepSimulation()

    def base_env_simulation_reset(self):
        self.p.resetSimulation()
