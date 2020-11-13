import numpy as np

from ..sensors import Sensors


class UaV(object):
    """This the base class for single UGV robot
    """
    def __init__(self, physics_client, init_pos, init_orientation, platoon_id,
                 robot_id, config, team_type):

        # Physics client
        self.physics_client = physics_client

        # Platoon properties
        self.vehicle_id = robot_id
        self.platoon_id = platoon_id

        # Properties UAV
        self.init_pos = init_pos
        self.init_orientation = init_orientation
        self.current_pos = init_pos
        self.desired_pos = init_pos

        # Extra parameters
        self.idle = True
        self.ammo = 100
        self.battery = 100
        self.functional = True
        self.speed = config['uav']['speed']
        self.search_speed = config['uav']['search_speed']

        # Config
        self.config = config

        # Sensors
        self.sensors = Sensors(physics_client)

        # Initial setup
        self._initial_setup(team_type)
        return None

    def _initial_setup(self, team_type):
        """Initial step of objects and constraints
        """
        # Load the mesh
        if self.config['simulation']['detailed_model']:
            path = '/'.join(
                ['data/assets', 'vehicles', 'arial_vehicle_detailed.urdf'])
        else:
            path = '/'.join(
                ['data/assets', 'vehicles', 'arial_vehicle_abstract.urdf'])
        self.object = self.physics_client.loadURDF(
            path,
            self.init_pos,
            self.init_orientation,
            flags=self.physics_client.URDF_USE_MATERIAL_COLORS_FROM_MTL)

        # Constraint
        self.constraint = self.physics_client.createConstraint(
            self.object, -1, -1, -1, self.physics_client.JOINT_FIXED,
            [0, 0, 0], [0, 0, 0], self.init_pos, self.init_orientation)

        # Change color depending on team type
        # if team_type == 'blue':  # Change the color
        #     self.physics_client.changeVisualShape(self.object,
        #                                           -1,
        #                                           rgbaColor=[0, 0, 1, 1])
        return None

    def get_pos_and_orientation(self):
        """Returns the position and orientation (as Yaw angle) of the robot.
        """
        pos, rot = self.physics_client.getBasePositionAndOrientation(
            self.object)
        euler = self.physics_client.getEulerFromQuaternion(rot)
        return np.array(pos), euler

    def reset(self):
        """Moves the robot back to its initial position
        """
        self.physics_client.changeConstraint(self.constraint, self.init_pos)
        self.current_pos = self.init_pos
        self.desired_pos = self.init_pos
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
        for i in range(4):
            self.physics_client.setJointMotorControl2(
                self.object,
                i,
                self.physics_client.VELOCITY_CONTROL,
                targetVelocity=100,
                force=20)

        self.current_pos, _ = self.get_pos_and_orientation()
        position[2] = 10.0
        self.physics_client.changeConstraint(self.constraint, position)
        return None

    def remove_self(self):
        self.physics_client.removeBody(self.object)
