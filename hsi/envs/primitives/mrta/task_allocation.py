import numpy as np
import networkx as nx


class MRTA(object):
    """
    A class to handle Multi-robot Task Allocations.

    .. todo:: Optimize/learn weight function.
    """
    def __init__(self, maxiter=None, fixedprec=1e9):
        """Constructor of the class, initilize robots' parameters.

        Parameters
        ----------
        vel : int, optional
            Average velocity of robot, by default 2
        safeBattery : float, optional
            Min. battery to land (it is only set non-zero for UAVs)
            by default 0
        """

        self.maxiter = maxiter
        self.fixedprec = fixedprec

    def allocateRobots(self, robotInfo, groupInfo):
        """Allocate robots to given groups.

        Parameters
        ----------
        robotInfo : array, Nr by 3; Nr: number of robots
            Robots' information; row contains [pos-x, pos-y, Battery Level]
        groupInfo : array, Ng by 6; Ng: number of groups
            Groups' information; each row contains
            [c-x, c-y, # of robots, Priority, Min. Battery, Deadline Time]

        Returns
        -------
        array, Nr by 1
            Robot-group allocation; row-i is corresponding to robot-i
            and it contains the group that robot-i is allocated to.

        >>> from mrta import mrta
        >>> Nr = 15
        >>> robotInfo = np.random.rand(Nr,3)
        >>> Ng = 4
        >>> groupInfo = np.random.rand(Ng,6)
        >>> for i in range(Ng):
        >>>     groupInfo[i,2] = np.random.randint(1,3)
        >>> mrta = mrta()
        >>> robotGroupAlloc = mrta.allocateRobots(robotInfo, groupInfo)
        """

        maxiter = self.maxiter
        fixedprec = self.fixedprec

        nRobot = np.shape(robotInfo)[0]
        nGroup = np.shape(groupInfo)[0]
        data = np.array(robotInfo[:, :2])

        min_ = np.min(data, axis=0)
        max_ = np.max(data, axis=0)
        nRobotWanted = sum(groupInfo[:, 2])

        demand = [nRobot - nRobotWanted]
        for i in range(nGroup):
            demand.append(groupInfo[i, 2])
        # print(demand)

        C = min_ + np.random.random(
            (len(demand), data.shape[1])) * (max_ - min_)
        M = np.array([-1] * len(data), dtype=np.int)

        itercnt = 0
        while True:
            itercnt += 1

            # memberships
            g = nx.DiGraph()
            g.add_nodes_from(range(0, data.shape[0]), demand=-1)  # points
            for i in range(0, len(C)):
                g.add_node(len(data) + i, demand=demand[i])

            # Calculating cost...
            cost = np.array([
                np.linalg.norm(np.tile(data.T, len(C)).T - np.tile(
                    C, len(data)).reshape(len(C) * len(data), C.shape[1]),
                               axis=1)
            ])
            # Preparing data_to_C_edges...
            data_to_C_edges = np.concatenate(
                (np.tile([range(0, data.shape[0])], len(C)).T,
                 np.tile(
                     np.array([
                         range(data.shape[0], data.shape[0] + C.shape[0])
                     ]).T, len(data)).reshape(len(C) * len(data),
                                              1), cost.T * fixedprec),
                axis=1).astype(np.uint64)
            # Adding to graph
            g.add_weighted_edges_from(data_to_C_edges)

            a = len(data) + len(C)
            g.add_node(a, demand=len(data) - np.sum(demand))
            C_to_a_edges = np.concatenate((np.array(
                [range(len(data),
                       len(data) + len(C))]).T, np.tile([[a]], len(C)).T),
                                          axis=1)
            g.add_edges_from(C_to_a_edges)

            # Calculating min cost flow...
            f = nx.min_cost_flow(g)

            # assign
            M_new = np.ones(len(data), dtype=np.int) * -1
            for i in range(len(data)):
                p = sorted(f[i].items(), key=lambda x: x[1])[-1][0]
                M_new[i] = p - len(data)

            # stop condition
            if np.all(M_new == M):
                # Stop
                # return (C, M, f)
                break

            M = M_new

            # compute new centers
            for i in range(len(C)):
                C[i, :] = np.mean(data[M == i, :], axis=0)

            if maxiter is not None and itercnt >= maxiter:
                # Max iterations reached
                break

            robotGroup = M
            groupCenter = C[1:-1, :]

            return robotGroup, groupCenter
