from pathlib import Path

import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import osmnx as ox

from .sknw import build_sknw

from scipy.spatial import cKDTree
from scipy import interpolate
from skimage.morphology import medial_axis, binary_closing


class SkeletonPlanning():
    """Path planner based on the skeleton of the image.
    Generates a spline path
    """
    def __init__(self, config, grid):
        # Save the graph if not there
        file_path = Path(__file__).parents[4] / config[
            'graph_save_path'] / 'planning_graph.gpickle'
        if not Path(file_path).exists():
            self.full_map = grid.astype(int)
            self.grid = grid.astype(int)
            self.grid[self.grid == -1] = 1
            self.skeleton = binary_closing(medial_axis(1 - self.grid))
            self.sparse_graph = build_sknw(self.skeleton)

            # Get the dense graph
            self.dense_graph = self.make_dense_graph(self.sparse_graph)
            nx.write_gpickle(self.dense_graph, file_path)
        else:
            # Load if it is already there
            self.dense_graph = nx.read_gpickle(str(file_path))
        return None

    def add_node_edge(self, T, start, stop):
        """Add node and edges to the tree (graph)

        Parameters
        ----------
        T : graph
            A networkx graph object
        start : list
            The start point of the edge.
        stop : list
            The end point of the edge.

        Returns
        -------
        graph
            A graph appended with a node and an edge.
        """
        # Swap so that it aligns with image co-ordinate
        T.add_node(tuple(start[::-1]), x=start[1], y=start[0])  # swap
        distance = np.linalg.norm(start[::-1] - stop[::-1])
        T.add_edge(tuple(start[::-1]), tuple(stop[::-1]), weight=distance)
        return T

    def make_dense_graph(self, graph):
        """Convert a sparse graph to a dense graph.

        Parameters
        ----------
        graph : graph
            A networkx graph object.

        Returns
        -------
        graph
            A dense graph with added nodes and edges.
        """
        T = nx.Graph()
        for (s, e) in graph.edges():
            ps = graph[s][e]['pts']
            # Add first node
            start = graph.nodes()[s]['o']
            stop = ps[0]
            # Add the edge nodes
            T = self.add_node_edge(T, start, stop)
            for i in range(len(ps) - 1):
                T = self.add_node_edge(T, ps[i], ps[i + 1])
            # Add the last node
            start = ps[-1]
            stop = graph.nodes()[e]['o']
            T = self.add_node_edge(T, start, stop)
        return T

    def fit_spline(self, path):
        """Fit a spline to given points in the path.

        Parameters
        ----------
        path : list
            A list of points with x and y co-ordinates.

        Returns
        -------
        array
            A array of points on the spline.
        """
        points = []
        for node in path:
            points.append([node[0], node[1]])  # swap
        points = np.vstack(points)
        tck, u = interpolate.splprep(points.T)
        unew = np.linspace(u.min(), u.max(), 300)
        x_new, y_new = interpolate.splev(unew, tck)

        return np.asarray([x_new, y_new]).T

    def get_nearest_node(self, point):
        """Get the nearest node on the graph for a given point.

        Parameters
        ----------
        point : list
            A list with x and y co-ordinates.

        Returns
        -------
        list
            A list containing the nearest node on the graph.
        """
        nodes = pd.DataFrame({
            'x': nx.get_node_attributes(self.dense_graph, 'x'),
            'y': nx.get_node_attributes(self.dense_graph, 'y')
        })
        node_temp = nodes.copy()
        tree = cKDTree(data=node_temp[['x', 'y']])
        points = np.array([point[0], point[1]])
        _, idx = tree.query(points, k=1)
        return tuple(nodes.iloc[idx].values)

    def find_path(self, start, finish, spline=True):
        """Get the shorted path on the graph from start to finish

        Parameters
        ----------
        start : list
            A list with x and y co-ordinates specifying the start point.
        finish : list
            A list with x and y co-ordinates specifying the end point.
        spline : bool, optional
            Whether to fit a spline or not, by default True

        Returns
        -------
        list
            A list containing the co-ordinates points on the shortest path.
        """
        start_node = self.get_nearest_node(start)
        finish_node = self.get_nearest_node(finish)
        path = nx.shortest_path(self.dense_graph, start_node, finish_node)
        # Add start and end points before fitting spline
        if spline:
            # Fit a spline
            path.insert(0, tuple(start))
            path.append(tuple(finish))
            path = self.fit_spline(path)
        else:
            points = []
            for node in path:
                points.append([node[0], node[1]])
            points.insert(0, tuple(start))
            points.append(tuple(finish))
            path = np.vstack(points)

        return path

    def plot_trajectory(self, start, finish):
        """Plot the trajectory and the map from start to finish

        Parameters
        ----------
        start : list
            An list containing x and y co-ordinates of start point.
        finish : list
            An list containing x and y co-ordinate of finish point.

        Returns
        -------
        None
        """
        path = self.find_path(start, finish)
        plt.scatter(start[0], start[1], s=10, facecolor='r')
        plt.scatter(finish[0], finish[1], s=10, facecolor='r')
        for node in path:
            plt.scatter(node[0], node[1], s=10, facecolor='k')
        plt.imshow(self.full_map, origin='lower')
        plt.show()
        return None


class PathPlanning():
    """Path planner based on the skeleton of the image.
    Generates a spline path
    """
    def __init__(self, config):
        read_path = '/'.join(
            [config['map_data_path'], config['simulation']['map'], 'map.osm'])
        self.G = ox.graph_from_xml(read_path,
                                   simplify=True,
                                   bidirectional='drive')
        self.find_homogenous_affine_transformation(config)
        return None

    def find_homogenous_affine_transformation(self, config):
        """Find the affine transfromation from source points to target points
        source = A*target
        """
        read_path = '/'.join([
            config['map_data_path'], config['simulation']['map'],
            'coordinates.csv'
        ])
        points = pd.read_csv(read_path)
        target = points[['x', 'z']].values
        source = points[['lat', 'lon']].values

        # Pad the points with ones
        X = np.hstack((source, np.ones((source.shape[0], 1))))
        Y = np.hstack((target, np.ones((target.shape[0], 1))))
        self.A, res, rank, s = np.linalg.lstsq(X, Y, rcond=None)
        return None

    def linear_refine_implicit(self, x, n):
        """Given a 2D ndarray (npt, m) of npt coordinates in m dimension,
        insert 2**(n-1) additional points on each trajectory segment
        Returns an (npt*2**(n-1), m) ndarray
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
        point[2] = 1
        lat_lon = np.dot(point, np.linalg.inv(self.A))
        return lat_lon

    def find_path(self, start, end, n_splits=1):
        x = []
        y = []

        # Convert the node index to node ID
        if not isinstance(start, int):
            start_lat_lon = self.convert_to_lat_lon(start)
            start = ox.get_nearest_node(self.G, start_lat_lon)
        if not isinstance(end, int):
            # end_lat_lon = self.convert_to_lat_lon(end)
            end = ox.get_nearest_node(self.G, end)

        # TODO: Very dirty way to implement
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

        # Exchange x and z as they are reversed in pybullet
        refined_points[:, [1, 0]] = refined_points[:, [0, 1]]

        # Convert the lat lon to pybullet co-ordinates
        path_points = np.dot(refined_points, self.A)

        return path_points
