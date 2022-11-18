"""
Script for uCRM-9 wing's internal structure parameterization in HyperMesh.

Evangelos Filippou, October 2022

Pieces of software Needed:
- HyperMesh

Libraries:
- math
- numpy
- time
- urllib.request
- subprocess
- os
- matplotlib (if diagrams are needed)
- scipy

Other Things:
- Internet Connection

Advices:
- You must change all the relative paths if install to other PC
"""

import time
import matplotlib.pyplot as plt
from wing_parameters import Parameters
from derive_geometry import DerivedGeometry
from read_crm_data_incl import RibsInclined
from find_inclination import RibsOrientation
from dataclasses import dataclass
from spar_and_spar_caps_coords import SparsAndCapsCoords
from store_spar_ids import SparsCapsIDs
from connection_nodes import ConnectionNodes
import curve_classes
import surface_classes
import triple_surface_classes
from run_arg import run_argument
from delete_files import delete_files
import numpy as np

# Set counter
tic = time.perf_counter()

"""
################## Delete Previous Files: ##################
"""

delete_files()

# ################# User Defined Values: ##################

# See the wing_parameters.py file for more info about the parameters
parameters = Parameters(
    29.38,  # Semispan
    0.37,   # Yehudi break normalized
    2,      # Number of spars
    5,      # Number of central ribs
    5,      # Number of ribs from fuselage till yehudi break
    10,     # Number of ribs from yehudi break till semispan
    0.15,    # front spar position
    0.75,    # rear spar position
    0.1,    # fuselage section normalized
    0.3,    # Root left spar cap width
    0.3,    # Root right spar cap width
    0.1,    # Tip left spar cap width
    0.1,    # Tip right spar cap width
    3,      # Number of stringers per spar section
    0.03    # Stringers tolerance from spar caps
    )

# ################# Derive the Geometry and its' parameters: ##################

Derived_Geometry = DerivedGeometry(parameters)
wing = RibsInclined(Derived_Geometry, parameters)
inclination = RibsOrientation(Derived_Geometry, parameters)

class RibInclinedSurfaces:
    def __init__(self, inclination, N_ribs):
        self.surfaces = {}
        groups = {}

        z_lower = np.ones((Derived_Geometry.N_ribs, )) * (- 10)
        z_upper = np.ones((Derived_Geometry.N_ribs, )) * 10

        groups[0] = GroupOfNodes(
            N_ribs,
            inclination.Rib_line_x[:, 0],
            inclination.Rib_line_y[:, 0],
            z_upper[:, ],
            0)

        groups[1] = GroupOfNodes(
            N_ribs,
            inclination.Rib_line_x[:, 1],
            inclination.Rib_line_y[:, 1],
            z_upper[:, ],
            1)

        groups[2] = GroupOfNodes(
            N_ribs,
            inclination.Rib_line_x[:, 1],
            inclination.Rib_line_y[:, 1],
            z_lower[:, ],
            2)

        groups[3] = GroupOfNodes(
            N_ribs,
            inclination.Rib_line_x[:, 0],
            inclination.Rib_line_y[:, 0],
            z_lower[:, ],
            3)

        for i in range(0, N_ribs):
            self.surfaces[i] = Surface(groups[0], groups[1],
                                       groups[2], groups[3], i)
        self.write_nodes(N_ribs)
        self.write_surfaces(N_ribs)
    def write_nodes(self, n_ribs):
        with open('Construct_Nodes.tcl', 'w') as file:
            for i in range(0, n_ribs):
                for j in range(0, 4):
                    file.write('*createnode %.7f %.7f %.7f 0 0 0\n'
                               % (self.surfaces[i].nodal_ids[j].coord_x,
                                  self.surfaces[i].nodal_ids[j].coord_y,
                                  self.surfaces[i].nodal_ids[j].coord_z))
        file.close()

    def write_surfaces(self, n_ribs):
        with open('Construct_Nodes.tcl', 'a') as file:
            for i in range(0, n_ribs):
                file.write('*surfacemode 4\n'
                           '*createlist nodes 1 %.0f %.0f %.0f %.0f\n'
                           '*surfacesplineonnodesloop2 1 0\n'
                           % (self.surfaces[i].nodal_ids[0].node_id,
                              self.surfaces[i].nodal_ids[1].node_id,
                              self.surfaces[i].nodal_ids[2].node_id,
                              self.surfaces[i].nodal_ids[3].node_id))


class Surface:
    def __init__(self, group_0, group_1, group_2, group_3, i):
        self.nodal_ids = [group_0.nodes[i], group_1.nodes[i],
                          group_2.nodes[i], group_3.nodes[i]]


class GroupOfNodes:
    def __init__(self, n_ribs, coord_x, coord_y, coord_z, group_id):
        node_id = range(group_id * n_ribs + 1, (group_id + 1) * n_ribs + 1)
        self.nodes = {}
        for i in range(0, n_ribs):
            self.nodes[i] = Node(node_id[i], coord_x[i], coord_y[i], coord_z[i])


@dataclass
class Node:
    """A class that stores the nodal information."""

    node_id: float
    coord_x: float
    coord_y: float
    coord_z: float


construct_geometry = RibInclinedSurfaces(inclination, Derived_Geometry.N_ribs)

# End time counter
toc = time.perf_counter()
# Print time
print(f"Script run in {toc - tic:0.3f} seconds")
