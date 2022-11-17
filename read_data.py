"""It's a script that reads the ribs coordinates and stores them in a class."""
import numpy as np


class coordinates:
    """A class that reads, sorts and stores the coords of each node."""

    def __init__(self):
        with open('HM_Files/nodes.txt', 'r') as infile:
            node_id, x, y, z = np.loadtxt(infile, unpack=True)
        infile.close()
        node_id = node_id.astype('int')
        coords = np.array([node_id, x, y, z])
        i = np.argsort(node_id)
        coords = coords[:, i]

        self.Nodes = list()
        for i in range(1, len(node_id)):
            self.Nodes.append(Node(coords[0, :],
                              coords[1, :],
                              coords[3, :],
                              coords[3, :]))


class Node:

    def __init__(self, node_id, x, y, z):
        self.node_id = node_id
        self.x = x
        self.y = y
        self.z = z


rib_coords = coordinates()
