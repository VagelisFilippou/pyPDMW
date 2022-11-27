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
import numpy as np
from wing_parameters import Parameters
from derive_geometry import DerivedGeometry
from read_crm_data_incl import RibsInclined
from find_inclination import RibsOrientation
from spar_and_spar_caps_coords import SparsAndCapsCoords
from store_spar_ids import SparsCapsIDs
from connection_nodes import ConnectionNodes
import curve_classes
import surface_classes
import triple_surface_classes
from run_arg import run_argument
from delete_files import delete_files

# Set counter
tic = time.perf_counter()

"""
################## Delete Previous Files: ##################
"""

delete_files()

# ################# User Defined Values: ##################

# See the wing_parameters.py file for more info about the parameters
parameters = Parameters(
    29.38,  # Semi-span
    0.37,   # Yehudi break normalized
    3,      # Number of spars
    5,      # Number of central ribs
    10,      # Number of ribs from fuselage till yehudi break
    30,     # Number of ribs from yehudi break till semi-span
    0.15,    # front spar position
    0.75,    # rear spar position
    0.1,    # fuselage section normalized
    0.3,    # Root left spar cap width
    0.3,    # Root right spar cap width
    0.1,    # Tip left spar cap width
    0.1,    # Tip right spar cap width
    8,      # Number of stringers per spar section
    0.03    # Stringers tolerance from spar caps
    )

# ################# Derive the Geometry and its' parameters: ##################

Derived_Geometry = DerivedGeometry(parameters)
wing = RibsInclined(Derived_Geometry, parameters)
inclination = RibsOrientation(Derived_Geometry, parameters)

N_RIBS = Derived_Geometry.N_ribs
N_SPARS = parameters.n_spars
NUMBER_OF_NODES = Derived_Geometry.n
N_STRINGERS = len(parameters.stringers_pos())
N_STRINGERS_PER_SECT = parameters.n_stringers

# ## Spar and spar caps coordinates: ###

Spars_And_Spar_Caps = SparsAndCapsCoords(Derived_Geometry, wing, parameters)

Spars_nodes_X = Spars_And_Spar_Caps.Spars_nodes_X
Spars_nodes_Y = Spars_And_Spar_Caps.Spars_nodes_Y
Spar_Caps_XL = Spars_And_Spar_Caps.Spar_Caps_XL
Spar_Caps_XR = Spars_And_Spar_Caps.Spar_Caps_XR
Spar_Caps_YL = Spars_And_Spar_Caps.Spar_Caps_YL
Spar_Caps_YR = Spars_And_Spar_Caps.Spar_Caps_YR
Stringers_X = Spars_And_Spar_Caps.stringers_nodes_x
Stringers_Y = Spars_And_Spar_Caps.stringers_nodes_y

# ## Put the spars' coordinates in the xyz arrays and store their index: ###

xyz = SparsCapsIDs(wing,  Derived_Geometry, Spars_And_Spar_Caps, parameters)

X = xyz.coord_x
Y = xyz.coord_y
Z = xyz.coord_z

X_X = np.concatenate(X)

Spar_ID_Lower = xyz.Spar_ID_Lower
Spar_ID_Upper = xyz.Spar_ID_Upper
Spar_Cap_ID_Lower_Left = xyz.Spar_Cap_ID_Lower_Left
Spar_Cap_ID_Upper_Left = xyz.Spar_Cap_ID_Upper_Left
Spar_Cap_ID_Lower_Right = xyz.Spar_Cap_ID_Lower_Right
Spar_Cap_ID_Upper_Right = xyz.Spar_Cap_ID_Upper_Right
Stringer_ID_Lower = xyz.stringer_id_lower
Stringer_ID_Upper = xyz.stringer_id_upper

###
# Insert LE, TE, Spars and Spar Caps coordinates to arrays for curve construction:
###

Con_Nodes = ConnectionNodes(Derived_Geometry, xyz, parameters.n_spars,
                            N_STRINGERS)
Curve_IDs_Upper = Con_Nodes.Curve_IDs_Upper
Curve_IDs_Lower = Con_Nodes.Curve_IDs_Lower
LE_IDs = Con_Nodes.LE_IDs
TE_IDs_u = Con_Nodes.TE_IDs_u
TE_IDs_l = Con_Nodes.TE_IDs_l

plt.figure()
plt.scatter(X, Y, 1, marker='o')
plt.scatter(Spars_nodes_X, Spars_nodes_Y, 5, marker='o')
plt.scatter(Spar_Caps_XL, Spar_Caps_YL, 5, marker='o')
plt.scatter(Spar_Caps_XR, Spar_Caps_YR, 5, marker='o')
plt.scatter(Stringers_X, Stringers_Y, 5, marker='o')

# ################# Writing in Command file: ##################

# Initialization of counters
NODE_COUNTER = 0
CURVE_COUNTER = 0
SURFACE_COUNTER = 0
COMPONENT_COUNTER = 1  # =1 because of the initial component
ASSEMBLY_COUNTER = 1
# Open a .tcl file and write the commands there
with open('Wing_Geometry_Generation.tcl', 'w') as file:
    file.write('#----------Commands for wing geometry generation----------\n')
    # Change node tolerance
    file.write('*toleranceset 0.01\n')

    # Now print nodes in this format: *createnode x y z system id 0 0
    for i in range(0, N_RIBS):
        for j in range(0, 2 * NUMBER_OF_NODES):
            # Free point
            # f.write('*createpoint %.7f %.7f %.7f 0\n'
            #         % (X[i, j], Y[i, j], Z[i, j]))
            # Nodes
            file.write('*createnode %.7f %.7f %.7f 0 0 0\n'
                       % (X[i, j], Y[i, j], Z[i, j]))
            NODE_COUNTER += 1
    X_Y_Z = np.array((np.concatenate(X),
                      np.concatenate(Y),
                      np.concatenate(Z)),
                     )
    H = 0.08
    L = 0.05

    Stringer_ID_Upper_Extend = np.zeros((N_RIBS, N_STRINGERS))
    Stringer_ID_Lower_Extend = np.zeros((N_RIBS, N_STRINGERS))
    Stringer_ID_Upper_Extend_L = np.zeros((N_RIBS, N_STRINGERS))
    Stringer_ID_Lower_Extend_L = np.zeros((N_RIBS, N_STRINGERS))

    for i in range(0, N_RIBS):
        for j in range(0, N_STRINGERS):
            file.write('*createnode %.7f %.7f %.7f 0 0 0\n'
                       % (X_Y_Z[0, Stringer_ID_Upper[i, j] - 1],
                          X_Y_Z[1, Stringer_ID_Upper[i, j] - 1],
                          X_Y_Z[2, Stringer_ID_Upper[i, j] - 1] - H))
            NODE_COUNTER += 1
            Stringer_ID_Upper_Extend[i, j] = NODE_COUNTER

            file.write('*createnode %.7f %.7f %.7f 0 0 0\n'
                       % (X_Y_Z[0, Stringer_ID_Upper[i, j] - 1] + L,
                          X_Y_Z[1, Stringer_ID_Upper[i, j] - 1],
                          X_Y_Z[2, Stringer_ID_Upper[i, j] - 1] - H))
            NODE_COUNTER += 1
            Stringer_ID_Upper_Extend_L[i, j] = NODE_COUNTER

            file.write('*createnode %.7f %.7f %.7f 0 0 0\n'
                       % (X_Y_Z[0, Stringer_ID_Lower[i, j] - 1],
                          X_Y_Z[1, Stringer_ID_Lower[i, j] - 1],
                          X_Y_Z[2, Stringer_ID_Lower[i, j] - 1] + H))
            NODE_COUNTER += 1
            Stringer_ID_Lower_Extend[i, j] = NODE_COUNTER

            file.write('*createnode %.7f %.7f %.7f 0 0 0\n'
                       % (X_Y_Z[0, Stringer_ID_Lower[i, j] - 1] + L,
                          X_Y_Z[1, Stringer_ID_Lower[i, j] - 1],
                          X_Y_Z[2, Stringer_ID_Lower[i, j] - 1] + H))
            NODE_COUNTER += 1
            Stringer_ID_Lower_Extend_L[i, j] = NODE_COUNTER

file.close()


Curve_Upper_Rib = curve_classes.UpperRibCurve(N_RIBS,
                                              N_SPARS,
                                              Curve_IDs_Upper,
                                              parameters,
                                              CURVE_COUNTER)
Curve_Lower_Rib = curve_classes.LowerRibCurve(N_RIBS,
                                              N_SPARS,
                                              Curve_IDs_Lower,
                                              parameters,
                                              Curve_Upper_Rib.curve_counter)

Curve_Leading_Edge = curve_classes.LeadingTrailingEdgeCurves(N_RIBS,
                                                             1,
                                                             LE_IDs,
                                                             Curve_Lower_Rib
                                                             .curve_counter)

Curve_Trailing_Edge =\
    curve_classes.LeadingTrailingEdgeCurves(N_RIBS,
                                            1,
                                            TE_IDs_u,
                                            Curve_Leading_Edge
                                            .curve_counter)

Curve_Spar_In_Ribs = curve_classes.MultipleCurves(N_RIBS, N_SPARS,
                                                  Spar_ID_Upper,
                                                  Spar_ID_Lower,
                                                  Curve_Trailing_Edge.
                                                  curve_counter)

Curve_Left_Spar_Cap_In_Ribs =\
    curve_classes.MultipleCurves(N_RIBS, N_SPARS,
                                 Spar_Cap_ID_Lower_Left,
                                 Spar_Cap_ID_Upper_Left,
                                 Curve_Spar_In_Ribs.
                                 curve_counter)

Curve_Right_Spar_Cap_In_Ribs =\
    curve_classes.MultipleCurves(N_RIBS, N_SPARS,
                                 Spar_Cap_ID_Lower_Right,
                                 Spar_Cap_ID_Upper_Right,
                                 Curve_Left_Spar_Cap_In_Ribs.
                                 curve_counter)

Curve_Upper_Spar =\
    curve_classes.SparAndSparCapCurves(N_RIBS - 1,
                                       N_SPARS,
                                       Spar_ID_Upper,
                                       Spar_ID_Upper,
                                       Curve_Right_Spar_Cap_In_Ribs.
                                       curve_counter)

Curve_Lower_Spar =\
    curve_classes.SparAndSparCapCurves(N_RIBS - 1,
                                       N_SPARS,
                                       Spar_ID_Lower,
                                       Spar_ID_Lower,
                                       Curve_Upper_Spar.
                                       curve_counter)

Curve_Upper_Left_Spar_Cap =\
    curve_classes.SparAndSparCapCurves(N_RIBS - 1,
                                       N_SPARS,
                                       Spar_Cap_ID_Upper_Left,
                                       Spar_Cap_ID_Upper_Left,
                                       Curve_Lower_Spar.
                                       curve_counter)

Curve_Lower_Left_Spar_Cap =\
    curve_classes.SparAndSparCapCurves(N_RIBS - 1,
                                       N_SPARS,
                                       Spar_Cap_ID_Lower_Left,
                                       Spar_Cap_ID_Lower_Left,
                                       Curve_Upper_Left_Spar_Cap.
                                       curve_counter)

Curve_Upper_Right_Spar_Cap =\
    curve_classes.SparAndSparCapCurves(N_RIBS - 1,
                                       N_SPARS,
                                       Spar_Cap_ID_Upper_Right,
                                       Spar_Cap_ID_Upper_Right,
                                       Curve_Lower_Left_Spar_Cap.
                                       curve_counter)

Curve_Lower_Right_Spar_Cap =\
    curve_classes.SparAndSparCapCurves(N_RIBS - 1,
                                       N_SPARS,
                                       Spar_Cap_ID_Lower_Right,
                                       Spar_Cap_ID_Lower_Right,
                                       Curve_Upper_Right_Spar_Cap.
                                       curve_counter)

Curve_Upper_Stringers =\
    curve_classes.StringersCurves(
        N_RIBS - 1,
        N_STRINGERS,
        N_SPARS,
        N_STRINGERS_PER_SECT,
        Stringer_ID_Upper,
        Stringer_ID_Upper,
        Curve_Lower_Right_Spar_Cap.curve_counter)

Curve_Lower_Stringers =\
    curve_classes.StringersCurves(
        N_RIBS - 1,
        N_STRINGERS,
        N_SPARS,
        N_STRINGERS_PER_SECT,
        Stringer_ID_Lower,
        Stringer_ID_Lower,
        Curve_Upper_Stringers.curve_counter)

Curve_Stringer_In_Ribs =\
    curve_classes.StringersInRibsCurves(
        N_RIBS,
        N_STRINGERS,
        N_SPARS,
        N_STRINGERS_PER_SECT,
        Stringer_ID_Upper,
        Stringer_ID_Lower,
        Curve_Lower_Stringers.curve_counter)

Curve_Upper_Stringers_Extend =\
    curve_classes.StringersCurves(
        N_RIBS - 1,
        N_STRINGERS,
        N_SPARS,
        N_STRINGERS_PER_SECT,
        Stringer_ID_Upper_Extend,
        Stringer_ID_Upper_Extend,
        Curve_Stringer_In_Ribs.curve_counter)

Curve_Lower_Stringers_Extend =\
    curve_classes.StringersCurves(
        N_RIBS - 1,
        N_STRINGERS,
        N_SPARS,
        N_STRINGERS_PER_SECT,
        Stringer_ID_Lower_Extend,
        Stringer_ID_Lower_Extend,
        Curve_Upper_Stringers_Extend.curve_counter)

Curve_Upper_Stringers_Extend_L =\
    curve_classes.StringersCurves(
        N_RIBS - 1,
        N_STRINGERS,
        N_SPARS,
        N_STRINGERS_PER_SECT,
        Stringer_ID_Upper_Extend_L,
        Stringer_ID_Upper_Extend_L,
        Curve_Lower_Stringers_Extend.curve_counter)

Curve_Lower_Stringers_Extend_L =\
    curve_classes.StringersCurves(
        N_RIBS - 1,
        N_STRINGERS,
        N_SPARS,
        N_STRINGERS_PER_SECT,
        Stringer_ID_Lower_Extend_L,
        Stringer_ID_Lower_Extend_L,
        Curve_Upper_Stringers_Extend_L.curve_counter)

Curve_Rib_Holes_Upper =\
    curve_classes.CirclesForStringers(
        N_RIBS,
        N_STRINGERS,
        N_SPARS,
        N_STRINGERS_PER_SECT,
        Stringer_ID_Upper,
        Curve_Lower_Stringers_Extend.curve_counter)\

Curve_Rib_Holes_Lower =\
    curve_classes.CirclesForStringers(
        N_RIBS,
        N_STRINGERS,
        N_SPARS,
        N_STRINGERS_PER_SECT,
        Stringer_ID_Lower,
        Curve_Rib_Holes_Upper.curve_counter)

Surfaces_Left_Spar_Cap_Rib =\
    surface_classes.MultipleSurfaces(
        N_RIBS,
        N_SPARS,
        Curve_Upper_Rib.sections_id.SC_L,
        Curve_Lower_Rib.sections_id.SC_L,
        Curve_Left_Spar_Cap_In_Ribs.curves,
        Curve_Spar_In_Ribs.curves,
        SURFACE_COUNTER,
        COMPONENT_COUNTER,
        ASSEMBLY_COUNTER,
        'L_Spar_Cap_Rib')

Surfaces_Right_Spar_Cap_Rib =\
    surface_classes.MultipleSurfaces(
        N_RIBS,
        N_SPARS,
        Curve_Upper_Rib.sections_id.SC_R,
        Curve_Lower_Rib.sections_id.SC_R,
        Curve_Right_Spar_Cap_In_Ribs.curves,
        Curve_Spar_In_Ribs.curves,
        Surfaces_Left_Spar_Cap_Rib.surface_counter,
        Surfaces_Left_Spar_Cap_Rib.component_counter,
        Surfaces_Left_Spar_Cap_Rib.assembly_counter,
        'R_Spar_Cap_Rib')

Surfaces_Spars =\
    surface_classes.SparSurfaces(
        N_RIBS - 1,
        N_SPARS,
        Curve_Upper_Spar.curves,
        Curve_Lower_Spar.curves,
        Curve_Spar_In_Ribs.curves,
        Curve_Spar_In_Ribs.curves,
        Surfaces_Right_Spar_Cap_Rib.surface_counter,
        Surfaces_Right_Spar_Cap_Rib.component_counter,
        Surfaces_Right_Spar_Cap_Rib.assembly_counter,
        'Spars')

Surfaces_Front_Upper_Skin =\
    surface_classes.FrontSkins(
        N_RIBS - 1,
        Curve_Upper_Rib.sections_id.LE,
        Curve_Upper_Rib.sections_id.LE,
        Curve_Upper_Left_Spar_Cap.curves,
        Curve_Leading_Edge.curves,
        Surfaces_Spars.surface_counter,
        Surfaces_Spars.component_counter,
        Surfaces_Spars.assembly_counter,
        'Upper_Front_Skin')

Surfaces_Front_Lower_Skin =\
    surface_classes.FrontSkins(
        N_RIBS - 1,
        Curve_Lower_Rib.sections_id.LE,
        Curve_Lower_Rib.sections_id.LE,
        Curve_Lower_Left_Spar_Cap.curves,
        Curve_Leading_Edge.curves,
        Surfaces_Front_Upper_Skin.surface_counter,
        Surfaces_Front_Upper_Skin.component_counter,
        Surfaces_Front_Upper_Skin.assembly_counter,
        'Lower_Front_Skin')

Surfaces_Rear_Upper_Skin =\
    surface_classes.RearSkins(
        N_RIBS - 1,
        Curve_Upper_Rib.sections_id.TE,
        Curve_Upper_Rib.sections_id.TE,
        Curve_Upper_Right_Spar_Cap.curves,
        Curve_Trailing_Edge.curves,
        Surfaces_Front_Lower_Skin.surface_counter,
        Surfaces_Front_Lower_Skin.component_counter,
        Surfaces_Front_Lower_Skin.assembly_counter,
        'Upper_Rear_Skin')

Surfaces_Rear_Lower_Skin =\
    surface_classes.RearSkins(
        N_RIBS - 1,
        Curve_Lower_Rib.sections_id.TE,
        Curve_Lower_Rib.sections_id.TE,
        Curve_Lower_Right_Spar_Cap.curves,
        Curve_Trailing_Edge.curves,
        Surfaces_Rear_Upper_Skin.surface_counter,
        Surfaces_Rear_Upper_Skin.component_counter,
        Surfaces_Rear_Upper_Skin.assembly_counter,
        'Lower_Rear_Skin')

Surfaces_Front_Rib =\
    surface_classes.FrontRib(
        N_RIBS,
        Curve_Lower_Rib.sections_id.LE,
        Curve_Upper_Rib.sections_id.LE,
        Curve_Left_Spar_Cap_In_Ribs.curves,
        Surfaces_Rear_Lower_Skin.surface_counter,
        Surfaces_Rear_Lower_Skin.component_counter,
        Surfaces_Rear_Lower_Skin.assembly_counter,
        'Front_Rib')

Surfaces_Rear_Rib =\
    surface_classes.RearRib(
        N_RIBS,
        Curve_Lower_Rib.sections_id.TE,
        Curve_Upper_Rib.sections_id.TE,
        Curve_Right_Spar_Cap_In_Ribs.curves,
        Surfaces_Front_Rib.surface_counter,
        Surfaces_Front_Rib.component_counter,
        Surfaces_Front_Rib.assembly_counter,
        'Rear_Rib')

Surfaces_Upper_Left_Spar_Cap =\
    surface_classes.SparCapsSurfaces(
        N_RIBS - 1,
        N_SPARS,
        Curve_Upper_Left_Spar_Cap.curves,
        Curve_Upper_Spar.curves,
        Curve_Upper_Rib.sections_id.SC_L,
        Curve_Upper_Rib.sections_id.SC_L,
        Surfaces_Rear_Rib.surface_counter,
        Surfaces_Rear_Rib.component_counter,
        Surfaces_Rear_Rib.assembly_counter,
        'Upper_Left_Spar_Cap')

Surfaces_Upper_Right_Spar_Cap =\
    surface_classes.SparCapsSurfaces(
        N_RIBS - 1,
        N_SPARS,
        Curve_Upper_Right_Spar_Cap.curves,
        Curve_Upper_Spar.curves,
        Curve_Upper_Rib.sections_id.SC_R,
        Curve_Upper_Rib.sections_id.SC_R,
        Surfaces_Upper_Left_Spar_Cap.surface_counter,
        Surfaces_Upper_Left_Spar_Cap.component_counter,
        Surfaces_Upper_Left_Spar_Cap.assembly_counter,
        'Upper_Right_Spar_Cap')

Surfaces_Lower_Right_Spar_Cap =\
    surface_classes.SparCapsSurfaces(
        N_RIBS - 1,
        N_SPARS,
        Curve_Lower_Right_Spar_Cap.curves,
        Curve_Lower_Spar.curves,
        Curve_Lower_Rib.sections_id.SC_R,
        Curve_Lower_Rib.sections_id.SC_R,
        Surfaces_Upper_Right_Spar_Cap.surface_counter,
        Surfaces_Upper_Right_Spar_Cap.component_counter,
        Surfaces_Upper_Right_Spar_Cap.assembly_counter,
        'Lower_Right_Spar_Cap')

Surfaces_Lower_Left_Spar_Cap =\
    surface_classes.SparCapsSurfaces(
        N_RIBS - 1,
        N_SPARS,
        Curve_Lower_Left_Spar_Cap.curves,
        Curve_Lower_Spar.curves,
        Curve_Lower_Rib.sections_id.SC_L,
        Curve_Lower_Rib.sections_id.SC_L,
        Surfaces_Lower_Right_Spar_Cap.surface_counter,
        Surfaces_Lower_Right_Spar_Cap.component_counter,
        Surfaces_Lower_Right_Spar_Cap.assembly_counter,
        'Lower_Left_Spar_Cap')

Surfaces_Left_Side_Main_Rib =\
    surface_classes.LeftSideOfMainRibSurfaces(
        N_RIBS,
        N_SPARS - 1,
        Curve_Upper_Rib.sections_id.main_skin,
        Curve_Lower_Rib.sections_id.main_skin,
        Curve_Right_Spar_Cap_In_Ribs.curves,
        Curve_Stringer_In_Ribs.curves,
        Surfaces_Lower_Left_Spar_Cap.surface_counter,
        Surfaces_Lower_Left_Spar_Cap.component_counter,
        Surfaces_Lower_Left_Spar_Cap.assembly_counter,
        'Main_Rib_Left_Side')

Surfaces_Right_Side_Main_Rib =\
    surface_classes.RightSideOfMainRibSurfaces(
        N_RIBS,
        N_SPARS - 1,
        Curve_Upper_Rib.sections_id.main_skin,
        Curve_Lower_Rib.sections_id.main_skin,
        Curve_Left_Spar_Cap_In_Ribs.curves,
        Curve_Stringer_In_Ribs.curves,
        Surfaces_Left_Side_Main_Rib.surface_counter,
        Surfaces_Left_Side_Main_Rib.component_counter,
        Surfaces_Left_Side_Main_Rib.assembly_counter,
        'Main_Rib_Right_Side')

Surfaces_Left_Side_Upper_Skin =\
    surface_classes.LeftSideOfSkins(
        N_RIBS - 1,
        N_SPARS - 1,
        Curve_Upper_Rib.sections_id.main_skin,
        Curve_Upper_Rib.sections_id.main_skin,
        Curve_Upper_Right_Spar_Cap.curves,
        Curve_Upper_Stringers.curves,
        Surfaces_Right_Side_Main_Rib.surface_counter,
        Surfaces_Right_Side_Main_Rib.component_counter,
        Surfaces_Right_Side_Main_Rib.assembly_counter,
        'Upper_Skin_Left_Side')


Surfaces_Left_Side_Lower_Skin =\
    surface_classes.LeftSideOfSkins(
        N_RIBS - 1,
        N_SPARS - 1,
        Curve_Lower_Rib.sections_id.main_skin,
        Curve_Lower_Rib.sections_id.main_skin,
        Curve_Lower_Right_Spar_Cap.curves,
        Curve_Lower_Stringers.curves,
        Surfaces_Left_Side_Upper_Skin.surface_counter,
        Surfaces_Left_Side_Upper_Skin.component_counter,
        Surfaces_Left_Side_Upper_Skin.assembly_counter,
        'Lower_Skin_Left_Side')


Surfaces_Right_Side_Upper_Skin =\
    surface_classes.RightSideOfSkins(
        N_RIBS - 1,
        N_SPARS - 1,
        Curve_Upper_Rib.sections_id.main_skin,
        Curve_Upper_Rib.sections_id.main_skin,
        Curve_Upper_Left_Spar_Cap.curves,
        Curve_Upper_Stringers.curves,
        Surfaces_Left_Side_Lower_Skin.surface_counter,
        Surfaces_Left_Side_Lower_Skin.component_counter,
        Surfaces_Left_Side_Lower_Skin.assembly_counter,
        'Upper_Skin_Right_Side')

Surfaces_Right_Side_Lower_Skin =\
    surface_classes.RightSideOfSkins(
        N_RIBS - 1,
        N_SPARS - 1,
        Curve_Lower_Rib.sections_id.main_skin,
        Curve_Lower_Rib.sections_id.main_skin,
        Curve_Lower_Left_Spar_Cap.curves,
        Curve_Lower_Stringers.curves,
        Surfaces_Right_Side_Upper_Skin.surface_counter,
        Surfaces_Right_Side_Upper_Skin.component_counter,
        Surfaces_Right_Side_Upper_Skin.assembly_counter,
        'Lower_Skin_Right_Side')

Surfaces_Main_Rib =\
    triple_surface_classes.MultipleSurfaces(
        N_RIBS,
        N_SPARS - 1,
        N_STRINGERS_PER_SECT,
        Curve_Upper_Rib.sections_id.main_skin,
        Curve_Lower_Rib.sections_id.main_skin,
        Curve_Stringer_In_Ribs.curves,
        Curve_Stringer_In_Ribs.curves,
        Surfaces_Right_Side_Lower_Skin.surface_counter,
        Surfaces_Right_Side_Lower_Skin.component_counter,
        Surfaces_Right_Side_Lower_Skin.assembly_counter,
        'Main_Rib')

Surfaces_Upper_Skin =\
    triple_surface_classes.MultipleSurfaces(
        N_RIBS - 1,
        N_SPARS - 1,
        N_STRINGERS_PER_SECT,
        Curve_Upper_Rib.sections_id.main_skin,
        Curve_Upper_Rib.sections_id.main_skin,
        Curve_Upper_Stringers.curves,
        Curve_Upper_Stringers.curves,
        Surfaces_Main_Rib.surface_counter,
        Surfaces_Main_Rib.component_counter,
        Surfaces_Main_Rib.assembly_counter,
        'Upper_Skin')

Surfaces_Lower_Skin =\
    triple_surface_classes.MultipleSurfaces(
        N_RIBS - 1,
        N_SPARS - 1,
        N_STRINGERS_PER_SECT,
        Curve_Lower_Rib.sections_id.main_skin,
        Curve_Lower_Rib.sections_id.main_skin,
        Curve_Lower_Stringers.curves,
        Curve_Lower_Stringers.curves,
        Surfaces_Upper_Skin.surface_counter,
        Surfaces_Upper_Skin.component_counter,
        Surfaces_Upper_Skin.assembly_counter,
        'Lower_Skin')

Surfaces_Upper_Stringers =\
    triple_surface_classes.StringerSurfaces(
        N_RIBS - 1,
        N_SPARS - 1,
        N_STRINGERS_PER_SECT,
        Curve_Upper_Stringers.curves,
        Curve_Upper_Stringers_Extend.curves,
        Surfaces_Lower_Skin.surface_counter,
        Surfaces_Lower_Skin.component_counter,
        Surfaces_Lower_Skin.assembly_counter,
        'Upper_Stringers')

Surfaces_Upper_Stringers_L =\
    triple_surface_classes.StringerSurfaces(
        N_RIBS - 1,
        N_SPARS - 1,
        N_STRINGERS_PER_SECT,
        Curve_Upper_Stringers_Extend.curves,
        Curve_Upper_Stringers_Extend_L.curves,
        Surfaces_Upper_Stringers.surface_counter,
        Surfaces_Upper_Stringers.component_counter,
        Surfaces_Upper_Stringers.assembly_counter,
        'Upper_Stringers_L')

Surfaces_Lower_Stringers =\
    triple_surface_classes.StringerSurfaces(
        N_RIBS - 1,
        N_SPARS - 1,
        N_STRINGERS_PER_SECT,
        Curve_Lower_Stringers.curves,
        Curve_Lower_Stringers_Extend.curves,
        Surfaces_Upper_Stringers_L.surface_counter,
        Surfaces_Upper_Stringers_L.component_counter,
        Surfaces_Upper_Stringers_L.assembly_counter,
        'Lower_Stringers')

Surfaces_Lower_Stringers_L =\
    triple_surface_classes.StringerSurfaces(
        N_RIBS - 1,
        N_SPARS - 1,
        N_STRINGERS_PER_SECT,
        Curve_Lower_Stringers_Extend.curves,
        Curve_Lower_Stringers_Extend_L.curves,
        Surfaces_Lower_Stringers.surface_counter,
        Surfaces_Lower_Stringers.component_counter,
        Surfaces_Lower_Stringers.assembly_counter,
        'Lower_Stringers_L')

# surface_classes.CutRibHoles(
#     Surfaces_Main_Rib.surfaces,
#     Curve_Rib_Holes_Upper.curves,
#     N_RIBS,
#     N_SPARS)

# surface_classes.CutRibHoles(
#     Surfaces_Main_Rib.surfaces,
#     Curve_Rib_Holes_Lower.curves,
#     N_RIBS,
#     N_SPARS)

SURFACE_COUNTER = Surfaces_Lower_Stringers_L.surface_counter

with open('Wing_Geometry_Generation.tcl', 'a+') as file:
    # Clear all nodes
    file.write("*nodecleartempmark\n")

    # Clean-up the geometry
    my_list = list(range(1, SURFACE_COUNTER + 1))
    STR_IDS = ' '.join(map(str, my_list))
    CMD = "*createmark surfaces 1 " + STR_IDS
    file.write(CMD)
    file.write('\n*selfstitchcombine 1 146 0.01 0.01\n')
    # Save the file and close
    # file.write("*writefile \"C:/Users/efilippo/Documents/"
    #            "ASD_Lab_Parametric_Design_of_Wing_OOP/HM_Files/wing.hm\" 1\n")
    file.write(
            "*writefile \"C:/Users/Vagelis/Documents/UC3M_Internship/Python/"
            "ASD_Lab_Parametric_Design_of_Wing_OOP/HM_Files/wing.hm\" 1\n"
    )
    file.write("return; # Stop script and return to application\n*quit 1;\n")
file.close()

# ################# Running the Command file: ##################

# Location of .tcl script and run
TCL_SCRIPT_PATH = "/ASD_Lab_Parametric_Design_of_Wing_OOP/"\
                    "Wing_Geometry_Generation.tcl"
run_argument(TCL_SCRIPT_PATH)

# End time counter
toc = time.perf_counter()
# Print time
print(f"Script run in {toc - tic:0.3f} seconds")
