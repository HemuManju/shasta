import numpy as np
from numpy import genfromtxt


class StateManager():
    def __init__(self, current_time, config):
        super(StateManager, self).__init__()
        # Need to specify some parameters

        self.current_time = current_time
        self.config = config
        self.found_goal = False

        # Initial setup
        self._initial_mission_setup()
        self._initial_nodes_setup()
        self._initial_buildings_setup()
        self._initial_target_setup()
        return None

    def _initial_uxv(self, uav, ugv):
        self.uav = uav
        self.ugv = ugv
        return None

    def _initial_mission_setup(self):
        """Perform initial setup such as progress, reward, grid map etc.
        """
        self.grid_map = np.load(self.config['map_save_path'] +
                                'occupancy_map.npy')
        self.goal = self.config['simulation']['goal_node']
        self.progress_reward = self.config['reward']['progress_reward']
        self.indoor_reward = 2 * self.progress_reward
        self.n_keep_in_pareto = self.config['state']['n_keep_in_pareto']
        return None

    def _initial_nodes_setup(self):
        """Performs initial nodes setup
        """
        # Nodes setup
        self.nodes = []
        path = self.config['map_data_path'] + 'nodes.csv'
        position_data = genfromtxt(path, delimiter=',')
        for i in range(self.config['simulation']['n_nodes']):
            info = {}
            info['position'] = [
                position_data[i][1] * 1.125, position_data[i][0] / 1.125
            ]
            info['importance'] = 0
            self.nodes.append(info)
        return None

    def _initial_buildings_setup(self):
        """Perfrom initial building setup.
        """
        # Buildings setup (probably we might need to read it from a file)
        self.buildings = []
        path = self.config['map_data_path'] + 'buildings.csv'
        data = genfromtxt(path, delimiter=',')
        for i in range(self.config['simulation']['n_buildings']):
            info = {}
            info['target_id'] = data[i][0]

            # Node info (a building is also a node)
            node_info = self.node_info(int(info['target_id']))
            info['position'] = node_info['position']
            info['area'] = data[i][1]
            info['perimeter'] = data[i][2]
            info['n_floors'] = data[i][3]
            self.buildings.append(info)
        return None

    def _initial_target_setup(self):
        """Performs target setup with properties such as goal probability,
        goal progress etc.
        """
        # Targets
        self.target = []
        n_targets = self.config['simulation']['n_targets']
        for target in self.config['simulation']['target_building_id']:
            info = {}
            info['target_id'] = target
            info['probability_goals'] = 1 / n_targets
            info['progress_goals'] = 0
            info['probability_goals_indoor'] = 1 / n_targets
            info['progress_goals_indoor'] = 0
            info['defence_perimeter'] = 0

            building_info = self.building_info(target)
            info['position'] = building_info['position']
            info['perimeter'] = building_info['perimeter']
            info['area'] = building_info['area']
            info['n_floors'] = building_info['n_floors']
            info['n_defence_perimeter'] = building_info['perimeter'] / (
                self.config['ugv']['defense_radius'] * 2)

            self.target.append(info)

    def node_info(self, id):
        """Get the information about a node.

            Parameters
            ----------
            id : int
                Node ID

            Returns
            -------
            dict
                A dictionary containing all the information about the node.
            """
        return self.nodes[id]

    def building_info(self, id):
        """Get the information about a building such as perimeter,
            position, number of floors.

            Parameters
            ----------
            id : int
                Building ID

            Returns
            -------
            dict
                A dictionary containing all the information about the building.
            """
        for building in self.buildings:
            if building['target_id'] == id:
                return building

    def target_info(self, id):
        """Get the information about the target.

        Parameters
        ----------
        id : int
            Target ID

        Returns
        -------
        dict
            A dictionary containing all the information about the target.
        """
        for target in self.target:
            if target['target_id'] == id:
                return target

    def check_vehicle_type(self, vehicle):
        """Check the vehicle type

        Parameters
        ----------
        vehicle : instance
            An instance of vehicle class UAV or UGV

        Returns
        -------
        string/None
            Return vehicle type if the vehicle is idle
        """
        if (not vehicle.idle) and vehicle.type == 'uav':
            return 'uav'
        elif (not vehicle.idle) and vehicle.type == 'ugv':
            return 'ugv'
        else:
            return None

    def check_closeness(self, vehicle, target):
        target_pos = target['position']
        vehicle_pos = vehicle.current_pos
        dist = np.linalg.norm(
            np.asarray(vehicle_pos[0:2]) - np.asarray(target_pos))
        if vehicle.type == 'uav':
            return dist <= self.config['uav']['search_dist']
        elif vehicle.type == 'ugv':
            return dist <= self.config['ugv']['defense_radius']
        else:
            return None

    def outdoor_progress(self, vehicle, target):
        req_progress = target['n_floors'] * target['perimeter']
        progesse_rate = vehicle.search_speed / req_progress
        progress_goals = self.config['simulation']['time_step'] * progesse_rate
        return progress_goals

    def indoor_progress(self, vehicle, target):
        req_progress = target['n_floors'] * target['area']
        progesse_rate = vehicle.search_speed / req_progress
        progress_goals = self.config['simulation']['time_step'] * progesse_rate
        return progress_goals

    def outdoor_target_progress_update(self, vehicles):  # noqa
        for target in self.target:
            progress_goals = 0
            for vehicle in vehicles:
                if self.check_vehicle_type(vehicle) == 'uav':
                    if self.check_closeness(vehicle, target):
                        progress_goals += self.outdoor_progress(
                            vehicle, target)
            if progress_goals > 1:
                progress_goals = 1
            target[
                'progress_goals'] = target['progress_goals'] + progress_goals
            if target['progress_goals'] > 1:
                target['progress_goals'] = 1

        sum_progress = 0
        self.found_goal = False
        for j, target in enumerate(self.target):
            if target['target_id'] == self.config['simulation'][
                    'goal_node']:  # found the goal
                if target['progress_goals'] >= np.random.rand():
                    # if it finds it in out of building indoor search
                    # target is guaranteed
                    for i in range(len(self.target)):
                        if i == j:
                            self.target[i]['probability_goals'] = 1
                            self.target[i]['probability_goals_indoor'] = 1
                            self.target[i]['probability_goals_outdoor'] = 1
                        else:
                            self.target[i]['probability_goals'] = 0
                            self.target[i]['probability_goals_indoor'] = 0
                            self.target[i]['probability_goals_outdoor'] = 0
                    self.found_goal = True
                    break
            sum_progress += self.target[j]['progress_goals']

        if not self.found_goal:
            for target in self.target:
                target['probability_goals_outdoor'] = (
                    1 - target['progress_goals']) / (
                        len(self.target) - sum_progress
                    )  # 1- progress is probability of each of them
                target['probability_goals'] = (
                    target['probability_goals_outdoor'] +
                    target['probability_goals_indoor']) / 2
        return None

    def indoor_target_progress_update(self, vehicles):  # noqa
        for target in self.target:
            progress_goals = 0
            vehicle_count = 0

            for vehicle in vehicles:
                if self.check_vehicle_type(vehicle) == 'ugv':
                    if self.check_closeness(vehicle, target):
                        vehicle_count += 1
                        if target['n_defence_perimeter'] < vehicle_count:
                            progress_goals += self.indoor_progress(
                                vehicle, target)
            if progress_goals > 1:
                progress_goals = 1
            target[
                'progress_goals'] = target['progress_goals'] + progress_goals
            if target['progress_goals'] > 1:
                target['progress_goals'] = 1

        sum_progress = 0
        self.found_goal = False
        for j, target in enumerate(self.target):
            if target['target_id'] == self.config['simulation'][
                    'goal_node']:  # found the goal
                if target['progress_goals'] >= np.random.rand():
                    # if it finds it in out of building indoor search
                    # target is guaranteed
                    for i in range(len(self.target)):
                        if i == j:
                            self.target[i]['probability_goals'] = 1
                            self.target[i]['probability_goals_indoor'] = 1
                            self.target[i]['probability_goals_outdoor'] = 1
                        else:
                            self.target[i]['probability_goals'] = 0
                            self.target[i]['probability_goals_indoor'] = 0
                            self.target[i]['probability_goals_outdoor'] = 0
                    self.found_goal = True
                    break
            sum_progress += self.target[j]['progress_goals']

        if not self.found_goal:
            for target in self.target:
                target['probability_goals_outdoor'] = (
                    1 - target['progress_goals']) / (
                        len(self.target) - sum_progress
                    )  # 1- progress is probability of each of them

        return None

    def update_progress(self):
        """Update all the probability
        """
        self.indoor_target_progress_update(self.ugv)
        self.outdoor_target_progress_update(self.uav)
        done = False
        if self.target[1]['probability_goals_outdoor'] == 0:
            done = True

        return done
