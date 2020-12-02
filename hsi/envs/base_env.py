import pybullet as p
from pybullet_utils import bullet_client as bc


class BaseEnv(object):
    def __init__(self, config):
        self.config = config
        # Usage mode
        if config['simulation']['headless']:
            self.p = bc.BulletClient(connection_mode=p.DIRECT)
        else:
            options = '--background_color_red=0.85 --background_color_green=0.85 --background_color_blue=0.85'  # noqa
            self.p = bc.BulletClient(connection_mode=p.GUI, options=options)
            self.p.resetDebugVisualizerCamera(cameraDistance=150,
                                              cameraYaw=0,
                                              cameraPitch=-89.999,
                                              cameraTargetPosition=[0, 30, 0])

            # self.p.getCameraImage(1200, 1200)
            self.p.configureDebugVisualizer(self.p.COV_ENABLE_GUI, 0)
            # self.p.configureDebugVisualizer(shadowMapWorldSize=10)
            # self.p.configureDebugVisualizer(lightPosition=[0, 0, 500])

        # Set gravity
        self.p.setGravity(0, 0, -9.81)

        # Set parameters for simulation
        self.p.setPhysicsEngineParameter(
            fixedTimeStep=config['simulation']['time_step'] / 10,
            numSubSteps=1,
            numSolverIterations=5)
        return None

    def base_env_step(self):

        # self.p.getCameraImage(1200, 1200)
        self.p.stepSimulation()

    def base_env_simulation_reset(self):
        self.p.resetSimulation()
