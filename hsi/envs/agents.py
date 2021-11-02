import numpy as np
from .sensors import Sensors


class UgV(object):
    """This the base class for single UGV robot
    """
    def __init__(self, physics_client, init_pos, init_orientation, platoon_id,
                 robot_id, config, team_type):
        self.physics_client = physics_client

        # Properties UGV
        self.vehicle_id = robot_id
        self.platoon_id = platoon_id
        self.init_pos = init_pos
        self.current_pos = init_pos
        self.updated_pos = init_pos
        self.init_orientation = init_orientation
        self.idle = True
        self.ammo = 100
        self.battery = 100
        self.functional = True
        self.speed = config['ugv']['speed']
        self.search_speed = config['ugv']['search_speed']
        self.type = 'ugv'

        # Config
        self.config = config

        # Simulation parameters
        self.reward = 0

        # Add sensor class
        self.sensors = Sensors(physics_client)
        self._initial_setup(team_type)
        return None

    def _initial_setup(self, team_type):
        """Initial step of objects and constraints
        """
        # Load the environment
        if self.config['simulation']['collision_free']:
            path = '/'.join([
                self.config['urdf_data_path'], 'vehicles',
                'ground_vehicle_collision_free.urdf'
            ])
        else:
            path = '/'.join([
                self.config['urdf_data_path'], 'vehicles',
                'ground_vehicle.urdf'
            ])
        self.object = self.physics_client.loadURDF(path, self.init_pos,
                                                   self.init_orientation)
        if team_type == 'blue':  # Change the color
            self.physics_client.changeVisualShape(self.object,
                                                  -1,
                                                  rgbaColor=[0, 0, 1, 1])

        self.constraint = self.physics_client.createConstraint(
            self.object, -1, -1, -1, self.physics_client.JOINT_FIXED,
            [0, 0, 0], [0, 0, 0], self.init_pos)

        # Camera parameters
        self.projectionMatrix = self.physics_client.computeProjectionMatrixFOV(
            fov=45.0, aspect=1.0, nearVal=0.1, farVal=50.0)
        self.image_size = [128, 128]
        return None

    def get_image(self, image_type):
        """Get the camera image of the agent

        Parameters
        ----------
        image_type : str
            Specifying what kind of image to return

        Returns
        -------
        array
            A numpy array containing the image of specified image type
        """
        # Get position
        pos, _ = self.get_pos_and_orientation()
        image = self.sensors.get_camera_image(pos, image_type)
        return image

    def reset(self):
        """Moves the robot back to its initial position
        """
        self.physics_client.changeConstraint(self.constraint, self.init_pos)
        self.current_pos = self.init_pos
        self.updated_pos = self.init_pos
        return None

    def get_pos_and_orientation(self):
        """
        Returns the position and orientation (as Yaw angle) of the robot.
        """
        pos, rot = self.physics_client.getBasePositionAndOrientation(
            self.object)
        euler = self.physics_client.getEulerFromQuaternion(rot)
        return np.array(pos), euler[2]

    def get_info(self):
        """Returns the information about the UGV

        Returns
        -------
        dict
            A dictionary containing all the information
        """
        return self.__dict__

    def set_position(self, position):
        """This function moves the vehicles to given position

        Parameters
        ----------
        position : array
            The position to which the vehicle should be moved.
        """
        self.current_pos, _ = self.get_pos_and_orientation()
        position[2] = 0.5  # Near ground
        self.physics_client.changeConstraint(self.constraint, position)
        return None

    def remove_self(self):
        self.physics_client.removeBody(self.object)


class UaV(object):
    """This the base class for single UGV robot
    """
    def __init__(self, physics_client, init_pos, init_orientation, platoon_id,
                 robot_id, config, team_type):
        self.physics_client = physics_client

        # Properties UGV
        self.vehicle_id = robot_id
        self.platoon_id = platoon_id
        self.init_pos = init_pos
        self.current_pos = init_pos
        self.updated_pos = init_pos
        self.init_orientation = init_orientation
        self.idle = True
        self.ammo = 100
        self.battery = 100
        self.functional = True
        self.speed = config['uav']['speed']
        self.search_speed = config['uav']['search_speed']
        self.type = 'uav'

        # Config
        self.config = config
        # Simulation parameters
        self.reward = 0

        self.sensors = Sensors(physics_client)
        self._initial_setup(team_type)
        return None

    def _initial_setup(self, team_type):
        """Initial step of objects and constraints
        """
        # Load the environment
        if self.config['simulation']['collision_free']:
            path = '/'.join([
                self.config['urdf_data_path'], 'vehicles',
                'arial_vehicle_collision_free.urdf'
            ])
        else:
            path = '/'.join([
                self.config['urdf_data_path'], 'vehicles', 'arial_vehicle.urdf'
            ])

        self.object = self.physics_client.loadURDF(path, self.init_pos,
                                                   self.init_orientation)
        if team_type == 'blue':  # Change the color
            self.physics_client.changeVisualShape(self.object,
                                                  -1,
                                                  rgbaColor=[0, 0, 1, 1])

        self.constraint = self.physics_client.createConstraint(
            self.object, -1, -1, -1, self.physics_client.JOINT_FIXED,
            [0, 0, 0], [0, 0, 0], self.init_pos)

        # Camera parameters
        self.projectionMatrix = self.physics_client.computeProjectionMatrixFOV(
            fov=45.0, aspect=1.0, nearVal=0.1, farVal=50.0)
        self.image_size = [256, 256]
        return None

    def get_image(self, image_type):
        """Get the camera image of the agent

        Parameters
        ----------
        image_type : str
            Specifying what kind of image to return

        Returns
        -------
        array
            A numpy array containing the image of specified image type
        """
        # Get position
        pos, _ = self.get_pos_and_orientation()
        image = self.sensors.get_camera_image(pos, image_type)
        return image

    def reset(self):
        """Moves the robot back to its initial position
        """
        self.physics_client.changeConstraint(self.constraint, self.init_pos)
        self.current_pos = self.init_pos
        self.updated_pos = self.init_pos
        return None

    def get_pos_and_orientation(self):
        """Returns the position and orientation (as Yaw angle) of the robot.
        """
        pos, rot = self.physics_client.getBasePositionAndOrientation(
            self.object)
        euler = self.physics_client.getEulerFromQuaternion(rot)
        return np.array(pos), euler[2]

    def get_info(self):
        """Returns the information about the UGV

        Returns
        -------
        dict
            A dictionary containing all the information
        """
        return self.__dict__

    def set_position(self, position):
        """This function moves the vehicles to given position

        Parameters
        ----------
        position : array
            The position to which the vehicle should be moved.
        """
        self.current_pos, _ = self.get_pos_and_orientation()
        position[2] = 10.0
        self.physics_client.changeConstraint(self.constraint, position)
        return None

    def remove_self(self):
        self.physics_client.removeBody(self.object)
