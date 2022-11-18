"""It's a script that reads the ribs coordinates and stores them in a class."""
import numpy as np


class Coordinates:
    """A class that reads, sorts and creates a list of Node objects."""

    def __init__(self):
        with open('HM_Files/nodes.txt', 'r') as infile:
            node_id, coord_x, coord_y, coord_z = np.loadtxt(infile,
                                                            unpack=True)
        infile.close()
        node_id = node_id.astype('int')
        coords = np.array([node_id, coord_x, coord_y, coord_z])
        i = np.argsort(node_id)
        coords = coords[:, i]

        self.nodes = {}
        for i in range(0, len(node_id)):
            self.nodes[i] = self.Node(coords[0, i],
                                      coords[1, i],
                                      coords[3, i],
                                      coords[3, i])

    class Node:
        """A class that stores the nodal information."""

        def __init__(self, node_id, coord_x, coord_y, coord_z):
            self.node_id = node_id
            self.coord_x = coord_x
            self.coord_y = coord_y
            self.coord_z = coord_z


rib_coords = Coordinates()

# x = (rib_coords.Nodes[1].x)
