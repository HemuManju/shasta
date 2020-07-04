from pathlib import Path

import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

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
