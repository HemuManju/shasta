import numpy as np


class FormationControl(object):
    """ Formation control primitive using region based shape control.
    Coded by: Apurvakumar Jani, Date: 18/9/2019
    """
    def __init__(self):
        # Initialise the parameters
        self.a = 10
        self.b = 10
        self.knn = 6
        self.alpha = 0.5
        self.gamma = 0.5
        self.min_dis = 4
        return None

    def calculate_vel(self, vehicle, dt, all_drones_pos, centroid_pos,
                      path_vel, vmax, formation_type):
        """Calculate the vehicle velocity depending on the position of the peer vehicles

        Parameters
        ----------
        vehicle : class instance
            A class instance of UxV agent
        dt : float
            Time step duration (in seconds) to use in next position calculation
        all_drones_pos : aarray
            An array with position of all the vehicles in the group/platoon
        centroid_pos : array
            An array specifying the centroid of the platoon
        path_vel : float
            Path velocity calculated from next position and current position
        vmax : float
            Maximum velocity of the vehicle
        formation_type : str
            Whether the formation is solid or ring

        Returns
        -------
        vehicle : class instance
            A vehicle class instance with updated position
        """

        # Get the neighboor position
        curr_pos = np.asarray(vehicle.current_pos[0:2])
        peers_pos = all_drones_pos

        # Calculate the velocity of each neighboor particle
        k = 1 / self.knn  # constant
        g_lij = (self.min_dis**2) - np.linalg.norm(
            curr_pos - peers_pos, axis=1, ord=2)
        del_g_ij = 2 * (peers_pos - curr_pos)
        P_ij = k * np.dot(
            np.maximum(0, g_lij / (self.min_dis**2))**2, del_g_ij)
        f_g_ij = np.linalg.norm(
            (curr_pos - centroid_pos[0:2]) / np.array([self.a, self.b]),
            ord=2) - 1

        # Calculate path velocity
        kl = 1  # constant
        del_f_g_ij = 1 * (curr_pos - centroid_pos[0:2])
        del_zeta_ij = (kl * max(0, f_g_ij)) * del_f_g_ij
        vel = path_vel - (self.alpha * del_zeta_ij) - (self.gamma * P_ij)

        # Calculate the speed
        speed = np.linalg.norm(vel)

        # Normalize the velocity with respect to speed
        if speed > vmax:
            vel = (vel / speed) * vmax

        # New position
        vehicle.desired_pos[0:2] = vehicle.current_pos[0:2] + (vel) * dt

        return vehicle, speed

    def execute(self, vehicles, next_pos, centroid_pos, dt, formation_type):
        """Get the position of the formation control

        Parameters
        ----------
        vehicles : list
            A list containing UAV or UGV class
        centroid_pos : array
            An array containing the x, y, and z position
        dt : float
            Time step to be used for distance calculation
        """
        vmax = vehicles[0].speed
        all_drones_pos = np.asarray(
            [vehicle.current_pos[0:2] for vehicle in vehicles])

        # Path velocity
        path = np.array([next_pos[0], next_pos[1]]) - centroid_pos[0:2]
        path_vel = (1 / dt) * path
        if np.linalg.norm(path_vel) > vmax:
            path_vel = (path_vel / np.linalg.norm(path_vel)) * vmax

        # Loop over each drone to calculate the velocity
        # NOTE: Very complicated way to implementing list comprehension
        # TODO: Need to find an efficient way to implement formation control
        vehicles, speed = map(
            list,
            zip(*[
                self.calculate_vel(vehicle, dt, all_drones_pos, centroid_pos,
                                   path_vel, vmax, formation_type)
                for vehicle in vehicles
            ]))
        if np.max(speed) < 0.0075 * len(all_drones_pos):
            formation_done = True
        else:
            formation_done = False

        return vehicles, formation_done
