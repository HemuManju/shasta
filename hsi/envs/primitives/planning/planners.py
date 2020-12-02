import numpy as np
import pandas as pd
import networkx as nx
import osmnx as ox


class PathPlanning():
    """Path planner based on the skeleton of the image.
    Generates a spline path
    """
    def __init__(self, config):
        read_path = '/'.join([
            config['urdf_data_path'], config['simulation']['map_to_use'],
            'map.osm'
        ])
        self.G = ox.graph_from_xml(read_path,
                                   simplify=True,
                                   bidirectional='walk')
        self.A = self.find_homogenous_affine_transformation(config)
        return None

    def find_homogenous_affine_transformation(self, config):
        """Find the affine transfromation from source points to target points
        source = A*target

        Parameters
        ----------
        config : yaml
            A simulation configuration file

        Returns
        -------
        A : array
            A numpy array such that source = A*target
        """
        read_path = '/'.join([
            config['urdf_data_path'], config['simulation']['map_to_use'],
            'coordinates.csv'
        ])
        points = pd.read_csv(read_path)
        target = points[['x', 'z']].values
        source = points[['lat', 'lon']].values

        # Pad the points with ones
        X = np.hstack((source, np.ones((source.shape[0], 1))))
        Y = np.hstack((target, np.ones((target.shape[0], 1))))
        A, res, rank, s = np.linalg.lstsq(X, Y, rcond=None)
        return A

    def linear_refine_implicit(self, x, n):
        """Given a 2D ndarray (npt, m) of npt coordinates in m dimension,
        insert 2**(n-1) additional points on each trajectory segment
        Returns an (npt*2**(n-1), m) ndarray

        Parameters
        ----------
        x : array
            A 2D input array
        n : int
            Number of intermediate points to insert between two consecutive points in x

        Returns
        -------
        array
            An array with interploated points

        Raises
        ------
        NotImplementedError
            The functions is not implemented for 3D or higher dimensions
        ValueError
            Number of intermediate points should be greated than zero
        """
        if n > 1:
            m = 0.5 * (x[:-1] + x[1:])
            if x.ndim == 2:
                msize = (x.shape[0] + m.shape[0], x.shape[1])
            else:
                raise NotImplementedError

            x_new = np.empty(msize, dtype=x.dtype)
            x_new[0::2] = x
            x_new[1::2] = m
            return self.linear_refine_implicit(x_new, n - 1)
        elif n == 1:
            return x
        else:
            raise ValueError

    def convert_to_lat_lon(self, point):
        """Convert a given point to lat lon co-ordinates

        Parameters
        ----------
        point : array
            A numpy array in pybullet cartesian co-ordinates

        Returns
        -------
        lat_lon : array
            The lat lon co-ordinates
        """
        point[2] = 1
        lat_lon = np.dot(point, np.linalg.inv(self.A))
        return lat_lon

    def find_path(self, start, end, n_splits=1):
        """Finds a path between start and end using path graph

        Parameters
        ----------
        start : array
            A catersian co-ordinate specifying the start position
        end : array
            A node ID specifying the end position
        n_splits : int, optional
            Number of splits in refining the path points, by default 1

        Returns
        -------
        path_points : array
            A refined path points in pybullet cartesian co-ordinate system
        """
        x = []
        y = []

        # Convert the node index to node ID
        # TODO: Very dirty way to implement
        if not isinstance(start, int):
            start_lat_lon = self.convert_to_lat_lon(start)
            start = ox.get_nearest_node(self.G, start_lat_lon)
        if not isinstance(end, int):
            # end_lat_lon = self.convert_to_lat_lon(end)
            end = ox.get_nearest_node(self.G, end)

        route = nx.shortest_path(self.G, start, end, weight='length')
        for u, v in zip(route[:-1], route[1:]):
            # if there are parallel edges, select the shortest in length
            data = min(self.G.get_edge_data(u, v).values(),
                       key=lambda d: d["length"])
            if "geometry" in data:
                # if geometry attribute exists, add all its coords to list
                xs, ys = data["geometry"].xy
                x.extend(xs)
                y.extend(ys)
            else:
                # otherwise, the edge is a straight line from node to node
                x.extend((self.G.nodes[u]["x"], self.G.nodes[v]["x"]))
                y.extend((self.G.nodes[u]["y"], self.G.nodes[v]["y"]))

        # Add more path points for smooth travel
        lat_lon = np.array((x, y)).T
        refined_points = self.linear_refine_implicit(lat_lon, n=n_splits)
        refined_points = np.hstack(
            (refined_points, np.ones((refined_points.shape[0], 1))))

        # Exchange x and y as they are reversed in pybullet
        refined_points[:, [1, 0]] = refined_points[:, [0, 1]]

        # Convert the lat lon to pybullet co-ordinates
        path_points = np.dot(refined_points, self.A)

        return path_points
