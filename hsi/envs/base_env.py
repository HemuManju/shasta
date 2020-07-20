import pybullet as p
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
            self.p.configureDebugVisualizer(self.p.COV_ENABLE_GUI, 0)
            # self.p.configureDebugVisualizer(shadowMapWorldSize=100)

        # Set gravity
        self.p.setGravity(0, 0, -9.81)

        # Set parameters for simulation
        self.p.setPhysicsEngineParameter(
            fixedTimeStep=config['simulation']['time_step'] / 10,
            numSubSteps=1,
            numSolverIterations=5)

        return None

    def base_env_step(self):
        self.p.stepSimulation()

    def base_env_simulation_reset(self):
        self.p.resetSimulation()
