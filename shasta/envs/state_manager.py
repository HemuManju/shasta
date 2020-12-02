from pathlib import Path

import numpy as np
import osmnx as ox
import pandas as pd
import networkx as nx


class StateManager():
    def __init__(self, current_time, config):
        super(StateManager, self).__init__()
        # Need to specify some parameters
        self.current_time = current_time
        self.config = config
        self.found_goal = False

        # Initial setup
        self._affine_transformation_and_graph()
        self._initial_mission_setup()
        # self._initial_buildings_setup()
        # self._initial_target_setup()

        return None

    def _initial_uxv(self, uav, ugv):
        self.uav = uav
        self.ugv = ugv
        return None

    def _initial_mission_setup(self):
        """Perform initial setup such as progress, reward, grid map etc.
        """
        self.goal = self.config['simulation']['goal_node']
        self.progress_reward = self.config['reward']['progress_reward']
        self.indoor_reward = 2 * self.progress_reward
        self.n_keep_in_pareto = self.config['state']['n_keep_in_pareto']
        return None

    def _affine_transformation_and_graph(self):
        """Performs initial conversion of the lat lon to cartesian
        """
        # Graph
        read_path = '/'.join([
            self.config['urdf_data_path'],
            self.config['simulation']['map_to_use'], 'map.osm'
        ])
        G = ox.graph_from_xml(read_path, simplify=True, bidirectional='walk')
        self.G = nx.convert_node_labels_to_integers(G)

        # Transformation matrix
        read_path = '/'.join([
            self.config['urdf_data_path'],
            self.config['simulation']['map_to_use'], 'coordinates.csv'
        ])
        points = pd.read_csv(read_path)
        target = points[['x', 'z']].values
        source = points[['lat', 'lon']].values

        # Pad the points with ones
        X = np.hstack((source, np.ones((source.shape[0], 1))))
        Y = np.hstack((target, np.ones((target.shape[0], 1))))
        self.A, res, rank, s = np.linalg.lstsq(X, Y, rcond=None)

        return None

    def _initial_buildings_setup(self):
        """Perfrom initial building setup.
        """
        read_path = '/'.join([
            self.config['urdf_data_path'],
            self.config['simulation']['map_to_use'], 'buildings.csv'
        ])

        # Check if building information is already generated
        if Path(read_path).is_file():
            buildings = pd.read_csv(read_path)
        else:
            read_path = '/'.join([
                self.config['urdf_data_path'],
                self.config['simulation']['map_to_use'], 'map.osm'
            ])
            G = ox.graph_from_xml(read_path)
            # TODO: This method doesn't work if the building info is not there in OSM
            nodes, streets = ox.graph_to_gdfs(G)

            west, north, east, south = nodes.geometry.total_bounds
            polygon = ox.utils_geo.bbox_to_poly(north, south, east, west)
            gdf = ox.footprints.footprints_from_polygon(polygon)
            buildings_proj = ox.project_gdf(gdf)

            # Save the dataframe representing buildings
            buildings = pd.DataFrame()
            buildings['lon'] = gdf['geometry'].centroid.x
            buildings['lat'] = gdf['geometry'].centroid.y
            buildings['area'] = buildings_proj.area
            buildings['perimeter'] = buildings_proj.length
            try:
                buildings['height'] = buildings_proj['height']
            except KeyError:
                buildings['height'] = 10  # assumption
            buildings['id'] = np.arange(len(buildings_proj))

            # Save the building info
            save_path = read_path = '/'.join([
                self.config['urdf_data_path'],
                self.config['simulation']['map_to_use'], 'buildings.csv'
            ])
            buildings.to_csv(save_path, index=False)

        self.buildings = buildings
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
            info['lat'] = building_info['lat']
            info['lon'] = building_info['lon']
            info['perimeter'] = building_info['perimeter']
            info['area'] = building_info['area']
            info['height'] = building_info['height']
            info['n_defence_perimeter'] = building_info['perimeter'] / (
                self.config['ugv']['defense_radius'] * 2)

            self.target.append(info)

    def node_info(self, idx):
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
        return self.G.nodes[idx]

    def building_info(self, idx):
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
        return self.buildings.loc[self.buildings['id'] == idx]

    def get_image(self, platoon_id, platoon_type, vehicle_id, image_type):
        """Get the image of the agent

        Parameters
        ----------
        platoon_id : int
            The platoon ID to vehicle belongs to.
        platoon_type : str
            Platoon type 'uav' or 'ugv'
        vehicle_id : int
            Vehicle ID from which image is acquired
        image_type : str
            Type of image to return rgb, seg, depth

        Returns
        -------
        array
            A image from the vehicle of required type
        """
        if platoon_type == 'uav':
            platoon_key = 'uav_p_' + str(platoon_id)
            image = self.uav_platoons[platoon_key].get_camera_image(
                vehicle_id, image_type)
        else:
            platoon_key = 'ugv_p_' + str(platoon_id)
            image = self.ugv_platoons[platoon_key].get_camera_image(
                vehicle_id, image_type)
        return image

    def get_states(self):
        return self.__dict__
