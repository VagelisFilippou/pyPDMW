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

# delete_files()

# ################# User Defined Values: ##################

# See the wing_parameters.py file for more info about the parameters
parameters = Parameters(
    29.38,  # Semispan
    0.37,   # Yehudi break normalized
    4,      # Number of spars
    5,      # Number of central ribs
    12,      # Number of ribs from fuselage till yehudi break
    30,     # Number of ribs from yehudi break till semispan
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
        self.groups = {}

        z_lower = np.ones((Derived_Geometry.N_ribs, )) * (- 10)
        z_upper = np.ones((Derived_Geometry.N_ribs, )) * 10

        self.groups[0] = GroupOfNodes(
            inclination.Rib_line_x[:, 0],
            inclination.Rib_line_y[:, 0],
            z_upper[:, ],
            0)

        self.groups[1] = GroupOfNodes(
            inclination.Rib_line_x[:, 1],
            inclination.Rib_line_y[:, 1],
            z_upper[:, ],
            1)

        self.groups[2] = GroupOfNodes(
            inclination.Rib_line_x[:, 1],
            inclination.Rib_line_y[:, 1],
            z_lower[:, ],
            2)

        self.groups[3] = GroupOfNodes(
            inclination.Rib_line_x[:, 0],
            inclination.Rib_line_y[:, 0],
            z_lower[:, ],
            3)

        for i in range(0, N_ribs):
            self.surfaces[i] = Surface(self.groups, i)
        self.write_nodes(N_ribs)
        self.write_surfaces(N_ribs)

    def write_nodes(self, n_ribs):
        with open('HM_Files/Construct_Nodes.tcl', 'w') as file:
            fig = plt.figure()
            ax = fig.add_subplot(projection='3d')
            for i in range(0, 4):
                for j in range(0, n_ribs):
                    file.write('*createnode %.7f %.7f %.7f 0 0 0\n'
                               % (self.groups[i].nodes[j].coord_x,
                                  self.groups[i].nodes[j].coord_y,
                                  self.groups[i].nodes[j].coord_z))
                    ax.scatter(self.groups[i].nodes[j].coord_x,
                               self.groups[i].nodes[j].coord_y,
                               self.groups[i].nodes[j].coord_z)
        file.close()

    def write_surfaces(self, n_ribs):
        with open('HM_Files/Construct_Nodes.tcl', 'a') as file:
            for i in range(0, n_ribs):
                file.write('*surfacemode 4\n'
                           '*createlist nodes 1 %.0f %.0f %.0f %.0f\n'
                           '*surfacesplineonnodesloop2 1 0\n'
                           % (self.surfaces[i].nodal_ids[0].node_id,
                              self.surfaces[i].nodal_ids[1].node_id,
                              self.surfaces[i].nodal_ids[2].node_id,
                              self.surfaces[i].nodal_ids[3].node_id))
                self.surfaces[i].surface_id = i + 1
        file.close()


class Surface:
    def __init__(self, groups, i):
        self.nodal_ids = [groups[0].nodes[i], groups[1].nodes[i],
                          groups[2].nodes[i], groups[3].nodes[i]]
        self.surface_id = None


class GroupOfNodes:
    def __init__(self, coord_x, coord_y, coord_z, group_id):
        n_ribs = len(coord_x)
        node_id = range(group_id * n_ribs + 1, (group_id + 1) * n_ribs + 1)
        self.nodes = {}
        for i in range(0, n_ribs):
            self.nodes[i] = Node(node_id[i], coord_x[i] + 23.08821955,
                                 coord_y[i], coord_z[i])


@dataclass
class Node:
    """A class that stores the nodal information."""

    node_id: float
    coord_x: float
    coord_y: float
    coord_z: float


class OmlSurfacesIDs:
    """A class that stores the surface ids of uCRM wing."""

    def __init__(self, n_ribs):
        self.crm_ids = {}
        self.crm_ids[0] = n_ribs + 2  # central_upper
        self.crm_ids[1] = n_ribs + 1  # central_lower
        self.crm_ids[2] = n_ribs + 3  # yehudi_upper
        self.crm_ids[3] = n_ribs + 4  # yehudi_lower
        self.crm_ids[4] = n_ribs + 5  # tip_upper
        self.crm_ids[5] = n_ribs + 6  # tip_lower


class IntersectionCurves:

    def __init__(self, construct_geometry, crm_surfaces, n_ribs, number_of_nodes):
        self.curves = np.zeros((n_ribs, 2))
        self.curves_from_intersections(construct_geometry, crm_surfaces, n_ribs)
        self.node_creation(n_ribs, number_of_nodes)

    def curves_from_intersections(self, construct_geometry,
                                  crm_surfaces, n_ribs):
        curve_counter = 4 * n_ribs + 14 + 1
        with open('HM_Files/Construct_Nodes.tcl', 'a') as file:
            for i in range(0, n_ribs):
                if i < Derived_Geometry.Rib_Sections_ID[0]:
                    file.write(intersection_command(
                        construct_geometry.surfaces[i].surface_id,
                        crm_surfaces.crm_ids[0]))
                    self.curves[i, 0] = curve_counter
                    curve_counter += 1
                    file.write(intersection_command(
                        construct_geometry.surfaces[i].surface_id,
                        crm_surfaces.crm_ids[1]))
                    self.curves[i, 1] = curve_counter
                    curve_counter += 1
                elif Derived_Geometry.Rib_Sections_ID[0] <= i <\
                        Derived_Geometry.Rib_Sections_ID[1]:
                    file.write(intersection_command(
                        construct_geometry.surfaces[i].surface_id,
                        crm_surfaces.crm_ids[2]))
                    self.curves[i, 0] = curve_counter
                    curve_counter += 1
                    file.write(intersection_command(
                        construct_geometry.surfaces[i].surface_id,
                        crm_surfaces.crm_ids[3]))
                    self.curves[i, 1] = curve_counter
                    curve_counter += 1
                elif Derived_Geometry.Rib_Sections_ID[1] <= i <=\
                        Derived_Geometry.Rib_Sections_ID[2]:
                    file.write(intersection_command(
                        construct_geometry.surfaces[i].surface_id,
                        crm_surfaces.crm_ids[4]))
                    self.curves[i, 0] = curve_counter
                    curve_counter += 1
                    file.write(intersection_command(
                        construct_geometry.surfaces[i].surface_id,
                        crm_surfaces.crm_ids[5]))
                    self.curves[i, 1] = curve_counter
                    curve_counter += 1
        file.close()

    def node_creation(self, n_ribs, n):
        with open('HM_Files/Construct_Nodes.tcl', 'a') as file:
            file.write("*nodecleartempmark\n")
            for i in range(0, n_ribs):
                for j in range(0, 2):
                    file.write('*createmark lines 1 %.0f\n'
                               '*nodecreateonlines lines 1 %.0f 0 0\n'
                               % (self.curves[i, j], n))
        file.close()


def del_surfaces(construct_geometry):
    with open('HM_Files/Construct_Nodes.tcl', 'a') as file:
        for i in range(0, len(construct_geometry.surfaces)):
            file.write('*deleteelementsmode 0\n'
                       '*createmark surfaces 1 %.0f\n'
                       '*deletemark surfaces 1\n'
                       '*deleteelementsmode 1283\n'
                       % (construct_geometry.surfaces[i].surface_id))


def intersection_command(id_1, id_2):
    command = (('*createmark surfaces 1 %.0f\n'
                '*createplane 1 0 0 1 0 0 0\n'
                '*createmark surfaces 2 %.0f\n'
                '*surfaceintersectmark2 1 0 1 2 0\n')
               % (id_1, id_2))
    return command


construct_geometry = RibInclinedSurfaces(inclination, Derived_Geometry.N_ribs)
crm_surfaces = OmlSurfacesIDs(Derived_Geometry.N_ribs)

import_geom_command =\
    ('*geomimport "auto_detect" "C:/Users/Vagelis/Documents/UC3M_Internship/Python'
     '/ASD_Lab_Parametric_Design_of_Wing_OOP/HM_Files/uCRM_9_LOFT.hm.iges"'
     ' "CheckFacet=on" "CleanupTol=-0.01" "ColorsAsMetadata=off" "CreationType=Parts"'
     ' "DegSurfTol=0.0" "DoNotMergeEdges=off" "GroupsAsRegions=off"'
     ' "ImportBlanked=off" "ImportForVisualizationOnly=off" "ImportFreeCurves=on"'
     ' "ImportFreePoints=on" "ImportType=ASSEMBLY" "LayerAsMetadata=off"'
     ' "LegacyHierarchyAsMetadata=off" "ScaleFactor=1.0"'
     ' "SkipConnectivityComputation=off" "SkipCreationOfSolid=off" "SkipEntities="'
     ' "SplitComponents=Body" "TagsAsMetadata=on" "TargetUnits=CAD units"'
     ' "TrimWithModelSpaceCurves=off" "TrimWithPreferredRepresentation=off"\n')

with open('HM_Files/Construct_Nodes.tcl', 'a') as file:
    file.write(import_geom_command)
file.close()

number_of_nodes = 50
x = IntersectionCurves(construct_geometry, crm_surfaces,
                       Derived_Geometry.N_ribs, number_of_nodes)
del_surfaces(construct_geometry)

with open('HM_Files/Construct_Nodes.tcl', 'a') as file:
    #  Tcl Script for nodal coordinates export
    my_list = list(range(4 * Derived_Geometry.N_ribs + 1,
                         4 * Derived_Geometry.N_ribs +
                         2 * Derived_Geometry.N_ribs * number_of_nodes + 1))
    STR_IDS = ' '.join(map(str, my_list))
    file.write(
        'proc exportNodeCoords args {\n'
        'set dat [open "HM_Files/nodes.txt" w+]\n'
        # *createmarkpanel nodes 1 "Select points:"\n
        '*createmark nodes 1 ' + STR_IDS + ' \n'
        'foreach nodeId [hm_getmark nodes 1] {\n'
        'set x [hm_getentityvalue nodes $nodeId x 0]\n'
        'set y [hm_getentityvalue nodes $nodeId y 0]\n'
        'set z [hm_getentityvalue nodes $nodeId z 0]\n'
        # '*tagcreate nodes $nodeId [format "(%.1f  %.1f  %.1f)" $x $y $z] "N$nodeId" 2\n'
        'puts $dat [format "%.0f %.8f  %.8f  %.8f" $nodeId $x $y $z]\n'
        '}\n'
        '*clearmark nodes 1\n'
        'close $dat;\n'
        '}\n'
        'exportNodeCoords')
file.close()


# Location of .tcl script and run
TCL_SCRIPT_PATH = "/ASD_Lab_Parametric_Design_of_Wing_OOP/"\
                    "HM_Files/Construct_Nodes.tcl"
run_argument(TCL_SCRIPT_PATH)


# End time counter
toc = time.perf_counter()
# Print time
print(f"Script run in {toc - tic:0.3f} seconds")
