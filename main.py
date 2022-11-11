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
from derive_geometry import DerivedGeometry
from read_crm_data_incl import RibsInclined
from spar_and_spar_caps_coords import SparsAndCapsCoords
from store_spar_ids import SparsCapsIDs
from connection_nodes import ConnectionNodes
from run_arg import run_argument
from delete_files import delete_files

# Set counter
tic = time.perf_counter()

"""
################## Delete Previous Files: ##################
"""

delete_files()

"""
################## User Defined Values: ##################
"""

# Define Wing's Parameters:
SEMI_SPAN = 29.38
YB_PERCENT = 0.37  # Yehudi Break in Percent of Semispan

# Define Wing's Structural Parameters
N_SPARS = 3  # Number of spars
N_RIBS_CENTRAL = 5  # Number of equally spaced ribs
N_RIBS_YEHUDI = 5  # Number of equally spaced ribs
N_RIBS_SEMISPAN = 5  # Number of equally spaced ribs

# List with the location of each spar
SPARS_POSITION = np.linspace(0.1, 0.7, num=N_SPARS, endpoint=True)

# Specify the length of the fuselage wingbox
FSLG_SECTION_PERCENT = 0.1

# Define two widths per spar at the root and at the tip: UL, UR, LL, LR
SC_width = np.array([[0.3, 0.3], [0.1, 0.1]]) * 0.6

"""
################## Derive the Geometry and its' Parameters: ##################
"""

Parameters = DerivedGeometry(SEMI_SPAN,
                             YB_PERCENT,
                             N_SPARS,
                             N_RIBS_CENTRAL,
                             N_RIBS_YEHUDI,
                             N_RIBS_SEMISPAN,
                             SPARS_POSITION,
                             FSLG_SECTION_PERCENT,
                             SC_width)

wing = RibsInclined(Parameters.Y_list,
                    SPARS_POSITION,
                    Parameters.Origin[:, 0],
                    Parameters.Rib_Sections_ID)


X, Y, Z = wing.X, wing.Y, wing.Z

N_RIBS = Parameters.N_ribs
Origin = Parameters.Origin
Rib_Sections_ID = Parameters.Rib_Sections_ID
NUMBER_OF_NODES = Parameters.n

"""
### Spar and spar caps coordinates: ###
"""

Spars_And_Spar_Caps = SparsAndCapsCoords(Parameters,
                                         wing,
                                         N_SPARS,
                                         SPARS_POSITION,
                                         SC_width,
                                         SEMI_SPAN)
Spars_nodes_X = Spars_And_Spar_Caps.Spars_nodes_X
Spars_nodes_Y = Spars_And_Spar_Caps.Spars_nodes_Y
Spar_Caps_XL = Spars_And_Spar_Caps.Spar_Caps_XL
Spar_Caps_XR = Spars_And_Spar_Caps.Spar_Caps_XR
Spar_Caps_YL = Spars_And_Spar_Caps.Spar_Caps_YL
Spar_Caps_YR = Spars_And_Spar_Caps.Spar_Caps_YR

"""
### Put the spars' coordinates in the XYZ arrays and store their index: ###
"""

XYZ = SparsCapsIDs(Spars_And_Spar_Caps, X, Y, Z, N_RIBS, N_SPARS,
                   NUMBER_OF_NODES)

X = XYZ.X
Y = XYZ.Y
Z = XYZ.Z

Spar_ID_Lower = XYZ.Spar_ID_Lower
Spar_ID_Upper = XYZ.Spar_ID_Upper
Spar_Cap_ID_Lower_Left = XYZ.Spar_Cap_ID_Lower_Left
Spar_Cap_ID_Upper_Left = XYZ.Spar_Cap_ID_Upper_Left
Spar_Cap_ID_Lower_Right = XYZ.Spar_Cap_ID_Lower_Right
Spar_Cap_ID_Upper_Right = XYZ.Spar_Cap_ID_Upper_Right

"""
###
Insert LE, TE, Spars and Spar Caps to coords arrays for curve construction:
###
"""

Con_Nodes = ConnectionNodes(Parameters, XYZ, N_SPARS)
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

"""
################## Writing in Command file: ##################
"""

# Initialization of counters
COURVE_COUNTER = 0
SURFACE_COUNTER = 0
COMPONENT_COUNTER = 1

# Open a .tcl file and write the commands there
with open('Wing_Geometry_Generation.tcl', 'w') as f:
    f.write('#----------Commands for wing geometry generation----------\n')
    # Change node tolerance
    f.write('*toleranceset 0.01\n')

    # Now print nodes in this format: *createnode x y z system id 0 0
    for i in range(0, N_RIBS):
        for j in range(0, 2 * NUMBER_OF_NODES):
            # Free point
            # f.write('*createpoint %.7f %.7f %.7f 0\n'
            # % (X[i, j], Y[i, j], Z[i, j]))
            # Nodes
            f.write('*createnode %.7f %.7f %.7f 0 0 0\n'
                    % (X[i, j], Y[i, j], Z[i, j]))

    # Print upper rib curves
    Curve_U_Rib = np.zeros((N_RIBS, 3 * N_SPARS + 1))
    for i in range(0, N_RIBS):
        for j in range(0, 3 * N_SPARS + 1):
            my_list = list(range(Curve_IDs_Upper[i, j + 1], Curve_IDs_Upper[i, j] + 1))
            STR_IDS = ' '.join(map(str, my_list))
            CMD = "*createlist nodes 1 " + STR_IDS
            f.write(CMD)
            f.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0\n"
                    "*linecreatespline nodes 1 0 0 1 2\n")
            COURVE_COUNTER += 1
            Curve_U_Rib[i, j] = COURVE_COUNTER

    # Store the id of each curve type
    Curve_U_Rib_LE = Curve_U_Rib[:, 0]
    Curve_U_Rib_TE = Curve_U_Rib[:, -1]
    Curve_U_Rib_SC_L = np.zeros((N_RIBS, N_SPARS))
    Curve_U_Rib_SC_R = np.zeros((N_RIBS, N_SPARS))
    Curve_U_Rib_Spars = np.zeros((N_RIBS, N_SPARS - 1))
    for i in range(0, N_SPARS):
        if i < N_SPARS - 1:
            Curve_U_Rib_SC_L[:, i] = Curve_U_Rib[:, 3 * i + 1]
            Curve_U_Rib_SC_R[:, i] = Curve_U_Rib[:, 3 * i + 2]
            Curve_U_Rib_Spars[:, i] = Curve_U_Rib[:, 3 * i + 3]
        elif i == N_SPARS - 1:
            Curve_U_Rib_SC_L[:, i] = Curve_U_Rib[:, 3 * i + 1]
            Curve_U_Rib_SC_R[:, i] = Curve_U_Rib[:, 3 * i + 2]

    # Print lower rib curves
    Curve_L_Rib = np.zeros((N_RIBS, 3 * N_SPARS + 1))
    for i in range(0, N_RIBS):
        for j in range(0, 3 * N_SPARS + 1):
            my_list = list(range(Curve_IDs_Lower[i, j], Curve_IDs_Lower[i, j + 1] + 1))
            STR_IDS = ' '.join(map(str, my_list))
            CMD = "*createlist nodes 1 " + STR_IDS
            f.write(CMD)
            f.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0\n"
                    "*linecreatespline nodes 1 0 0 1 2\n")
            COURVE_COUNTER += 1
            Curve_L_Rib[i, j] = COURVE_COUNTER

    # Store the id of each curve type
    Curve_L_Rib_LE = Curve_L_Rib[:, 0]
    Curve_L_Rib_TE = Curve_L_Rib[:, -1]
    Curve_L_Rib_SC_L = np.zeros((N_RIBS, N_SPARS))
    Curve_L_Rib_SC_R = np.zeros((N_RIBS, N_SPARS))
    Curve_L_Rib_Spars = np.zeros((N_RIBS, N_SPARS - 1))
    for i in range(0, N_SPARS):
        if i < N_SPARS - 1:
            Curve_L_Rib_SC_L[:, i] = Curve_L_Rib[:, 3 * i + 1]
            Curve_L_Rib_SC_R[:, i] = Curve_L_Rib[:, 3 * i + 2]
            Curve_L_Rib_Spars[:, i] = Curve_L_Rib[:, 3 * i + 3]
        elif i == N_SPARS - 1:
            Curve_L_Rib_SC_L[:, i] = Curve_L_Rib[:, 3 * i + 1]
            Curve_L_Rib_SC_R[:, i] = Curve_L_Rib[:, 3 * i + 2]

    # Print LE and TE curves
    Curve_LE = np.zeros((N_RIBS - 1, 1))
    Curve_TE = np.zeros((N_RIBS - 1, 1))
    for i in range(0, N_RIBS - 1):
        my_list = [i * 2 * NUMBER_OF_NODES + 1,
                   (i + 1) * 2 * NUMBER_OF_NODES + 1]
        STR_IDS = ' '.join(map(str, my_list))
        CMD = "*createlist nodes 1 " + STR_IDS
        f.write(CMD)
        f.write("\n*linecreatefromnodes 1 0 150 5 179\n")
        COURVE_COUNTER += 1
        Curve_TE[i, 0] = COURVE_COUNTER
    for i in range(0, N_RIBS - 1):
        my_list = [LE_IDs[i, 0], LE_IDs[i + 1, 0]]
        STR_IDS = ' '.join(map(str, my_list))
        CMD = "*createlist nodes 1 " + STR_IDS
        f.write(CMD)
        f.write("\n*linecreatefromnodes 1 0 150 5 179\n")
        COURVE_COUNTER += 1
        Curve_LE[i, 0] = COURVE_COUNTER

    # Print spar curves in ribs
    Curve_Spar_iN_RIBS = np.zeros((N_RIBS, N_SPARS))
    for i in range(0, N_RIBS):
        for j in range(0, N_SPARS):
            my_list = list((Spar_ID_Upper[i, j], Spar_ID_Lower[i, j]))
            STR_IDS = ' '.join(map(str, my_list))
            CMD = "*createlist nodes 1 " + STR_IDS
            f.write(CMD)
            f.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0\n"
                    "*linecreatespline nodes 1 0 0 1 2\n")
            COURVE_COUNTER += 1
            Curve_Spar_iN_RIBS[i, j] = COURVE_COUNTER

    # Print left spar cap curves in ribs
    Curve_Spar_Cap_Left_iN_RIBS = np.zeros((N_RIBS, N_SPARS))
    for i in range(0, N_RIBS):
        for j in range(0, N_SPARS):
            my_list = list((Spar_Cap_ID_Lower_Left[i, j], Spar_Cap_ID_Upper_Left[i, j]))
            STR_IDS = ' '.join(map(str, my_list))
            CMD = "*createlist nodes 1 " + STR_IDS
            f.write(CMD)
            f.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0\n"
                    "*linecreatespline nodes 1 0 0 1 2\n")
            COURVE_COUNTER += 1
            Curve_Spar_Cap_Left_iN_RIBS[i, j] = COURVE_COUNTER

    # Print right spar cap curves in ribs
    Curve_Spar_Cap_Right_iN_RIBS = np.zeros((N_RIBS, N_SPARS))
    for i in range(0, N_RIBS):
        for j in range(0, N_SPARS):
            my_list = list((Spar_Cap_ID_Lower_Right[i, j], Spar_Cap_ID_Upper_Right[i, j]))
            STR_IDS = ' '.join(map(str, my_list))
            CMD = "*createlist nodes 1 " + STR_IDS
            f.write(CMD)
            f.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0\n"
                    "*linecreatespline nodes 1 0 0 1 2\n")
            COURVE_COUNTER += 1
            Curve_Spar_Cap_Right_iN_RIBS[i, j] = COURVE_COUNTER

    # Print upper spar curves
    Curve_U_Spar = np.zeros((N_RIBS - 1, N_SPARS))
    for i in range(0, N_RIBS - 1):
        for j in range(0, N_SPARS):
            my_list = list((Spar_ID_Upper[i, j], Spar_ID_Upper[i + 1, j]))
            STR_IDS = ' '.join(map(str, my_list))
            CMD = "*createlist nodes 1 " + STR_IDS
            f.write(CMD)
            f.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0\n"
                    "*linecreatespline nodes 1 0 0 1 2\n")
            COURVE_COUNTER += 1
            Curve_U_Spar[i, j] = COURVE_COUNTER

    # Print lower spar curves
    Curve_L_Spar = np.zeros((N_RIBS - 1, N_SPARS))
    for i in range(0, N_RIBS - 1):
        for j in range(0, N_SPARS):
            my_list = list((Spar_ID_Lower[i, j], Spar_ID_Lower[i + 1, j]))
            STR_IDS = ' '.join(map(str, my_list))
            CMD = "*createlist nodes 1 " + STR_IDS
            f.write(CMD)
            f.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0\n"
                    "*linecreatespline nodes 1 0 0 1 2\n")
            COURVE_COUNTER += 1
            Curve_L_Spar[i, j] = COURVE_COUNTER

    # Print upper left spar cap curves
    Curve_UL_Spar_Cap = np.zeros((N_RIBS - 1, N_SPARS))
    for i in range(0, N_RIBS - 1):
        for j in range(0, N_SPARS):
            my_list = list((Spar_Cap_ID_Upper_Left[i, j], Spar_Cap_ID_Upper_Left[i + 1, j]))
            STR_IDS = ' '.join(map(str, my_list))
            CMD = "*createlist nodes 1 " + STR_IDS
            f.write(CMD)
            f.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0\n"
                    "*linecreatespline nodes 1 0 0 1 2\n")
            COURVE_COUNTER += 1
            Curve_UL_Spar_Cap[i, j] = COURVE_COUNTER

    # Print lower left spar cap curves
    Curve_LL_Spar_Cap = np.zeros((N_RIBS - 1, N_SPARS))
    for i in range(0, N_RIBS - 1):
        for j in range(0, N_SPARS):
            my_list = list((Spar_Cap_ID_Lower_Left[i, j], Spar_Cap_ID_Lower_Left[i + 1, j]))
            STR_IDS = ' '.join(map(str, my_list))
            CMD = "*createlist nodes 1 " + STR_IDS
            f.write(CMD)
            f.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0\n"
                    "*linecreatespline nodes 1 0 0 1 2\n")
            COURVE_COUNTER += 1
            Curve_LL_Spar_Cap[i, j] = COURVE_COUNTER

    # Print upper right spar cap curves
    Curve_UR_Spar_Cap = np.zeros((N_RIBS - 1, N_SPARS))
    for i in range(0, N_RIBS - 1):
        for j in range(0, N_SPARS):
            my_list = list((Spar_Cap_ID_Upper_Right[i, j], Spar_Cap_ID_Upper_Right[i + 1, j]))
            STR_IDS = ' '.join(map(str, my_list))
            CMD = "*createlist nodes 1 " + STR_IDS
            f.write(CMD)
            f.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0\n"
                    "*linecreatespline nodes 1 0 0 1 2\n")
            COURVE_COUNTER += 1
            Curve_UR_Spar_Cap[i, j] = COURVE_COUNTER

    # Print lower right spar cap curves
    Curve_LR_Spar_Cap = np.zeros((N_RIBS - 1, N_SPARS))
    for i in range(0, N_RIBS - 1):
        for j in range(0, N_SPARS):
            my_list = list((Spar_Cap_ID_Lower_Right[i, j], Spar_Cap_ID_Lower_Right[i + 1, j]))
            STR_IDS = ' '.join(map(str, my_list))
            CMD = "*createlist nodes 1 " + STR_IDS
            f.write(CMD)
            f.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0\n"
                    "*linecreatespline nodes 1 0 0 1 2\n")
            COURVE_COUNTER += 1
            Curve_LR_Spar_Cap[i, j] = COURVE_COUNTER

    # Print left spar cap rib surfaces
    Surface_LSC_Rib = np.zeros((N_RIBS, N_SPARS))
    Component_LSC_Rib = np.zeros((N_RIBS, 1))
    for i in range(0, N_RIBS):
        for j in range(0, N_SPARS):
            my_list = list((Curve_U_Rib_SC_L[i, j],
                            Curve_L_Rib_SC_L[i, j],
                            Curve_Spar_Cap_Left_iN_RIBS[i, j],
                            Curve_Spar_iN_RIBS[i, j]))
            STR_IDS = ' '.join(map(str, my_list))
            CMD = "*surfacemode 4\n*createmark lines 1 " + STR_IDS
            f.write(CMD)
            f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
            SURFACE_COUNTER += 1
            Surface_LSC_Rib[i, j] = SURFACE_COUNTER
        f.write('*createentity comps name="Rib_LSC_%.0f"\n'
                % (i + 1))
        # f.write("*drawlistresetstyle\n")
        f.write('*startnotehistorystate {Moved surfaces into component "Rib_LSC_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f-%.0f\n'
                % (Surface_LSC_Rib[i, 0], Surface_LSC_Rib[i, -1]))
        f.write('*movemark surfaces 1 "Rib_LSC_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Rib_LSC_%.0f"}\n'
                % (i + 1))
        COMPONENT_COUNTER += 1
        Component_LSC_Rib[i, 0] = COMPONENT_COUNTER
    f.write('*createentity assems name="WingBox_Ribs"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=1 components={comps %.0f-%.0f}'
            % (Component_LSC_Rib[0, 0], Component_LSC_Rib[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print right spar cap rib surfaces
    Surface_RSC_Rib = np.zeros((N_RIBS, N_SPARS))
    Component_RSC_Rib = np.zeros((N_RIBS, 1))
    for i in range(0, N_RIBS):
        for j in range(0, N_SPARS):
            my_list = list((Curve_U_Rib_SC_R[i, j],
                            Curve_L_Rib_SC_R[i, j],
                            Curve_Spar_Cap_Right_iN_RIBS[i, j],
                            Curve_Spar_iN_RIBS[i, j]))
            STR_IDS = ' '.join(map(str, my_list))
            CMD = "*surfacemode 4\n*createmark lines 1 " + STR_IDS
            f.write(CMD)
            f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
            SURFACE_COUNTER += 1
            Surface_RSC_Rib[i, j] = SURFACE_COUNTER
        f.write('*createentity comps name="Rib_RSC_%.0f"\n'
                % (i + 1))
        # f.write("*drawlistresetstyle\n")
        f.write('*startnotehistorystate {Moved surfaces into component "Rib_RSC_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f-%.0f\n'
                % (Surface_RSC_Rib[i, 0], Surface_RSC_Rib[i, -1]))
        f.write('*movemark surfaces 1 "Rib_RSC_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Rib_RSC_%.0f"}\n'
                % (i + 1))
        COMPONENT_COUNTER += 1
        Component_RSC_Rib[i, 0] = COMPONENT_COUNTER
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=1 components={comps %.0f-%.0f}'
            % (Component_RSC_Rib[0, 0], Component_RSC_Rib[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print main rib surfaces
    Surface_Rib = np.zeros((N_RIBS, N_SPARS - 1))
    Component_Rib = np.zeros((N_RIBS, 1))
    for i in range(0, N_RIBS):
        for j in range(0, N_SPARS - 1):
            my_list = list((Curve_U_Rib_Spars[i, j],
                            Curve_L_Rib_Spars[i, j],
                            Curve_Spar_Cap_Right_iN_RIBS[i, j],
                            Curve_Spar_Cap_Left_iN_RIBS[i, j + 1]))
            STR_IDS = ' '.join(map(str, my_list))
            CMD = "*surfacemode 4\n*createmark lines 1 " + STR_IDS
            f.write(CMD)
            f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
            SURFACE_COUNTER += 1
            Surface_Rib[i, j] = SURFACE_COUNTER
        f.write('*createentity comps name="Rib_Main_%.0f"\n'
                % (i + 1))
        # f.write("*drawlistresetstyle\n")
        f.write('*startnotehistorystate {Moved surfaces into component "Rib_Main_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f-%.0f\n'
                % (Surface_Rib[i, 0], Surface_Rib[i, -1]))
        f.write('*movemark surfaces 1 "Rib_Main_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Rib_Main_%.0f"}\n'
                % (i + 1))
        COMPONENT_COUNTER += 1
        Component_Rib[i, 0] = COMPONENT_COUNTER
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=1 components={comps %.0f-%.0f}'
            % (Component_Rib[0, 0], Component_Rib[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print spar surfaces
    Surface_Spar = np.zeros((N_RIBS - 1, N_SPARS))
    Component_Spar = np.zeros((N_RIBS - 1, 1))
    for i in range(0, N_RIBS - 1):
        for j in range(0, N_SPARS):
            my_list = list((Curve_L_Spar[i, j], Curve_U_Spar[i, j],
                            Curve_Spar_iN_RIBS[i, j],
                            Curve_Spar_iN_RIBS[i + 1, j]))
            STR_IDS = ' '.join(map(str, my_list))
            CMD = "*surfacemode 4\n*createmark lines 1 " + STR_IDS
            f.write(CMD)
            f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
            SURFACE_COUNTER += 1
            Surface_Spar[i, j] = SURFACE_COUNTER
        f.write('*createentity comps name="Spar_%.0f"\n'
                % (i + 1))
        f.write('*startnotehistorystate {Moved surfaces into component "Spar_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f-%.0f\n'
                % (Surface_Spar[i, 0], Surface_Spar[i, -1]))
        f.write('*movemark surfaces 1 "Spar_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Spar_%.0f"}\n'
                % (i + 1))
        COMPONENT_COUNTER += 1
        Component_Spar[i, 0] = COMPONENT_COUNTER
    f.write('*createentity assems name="Spars"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=2 components={comps %.0f-%.0f}'
            % (Component_Spar[0, 0], Component_Spar[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print lower skin surfaces
    Surface_Lower_Skin = np.zeros((N_RIBS - 1, N_SPARS - 1))
    Component_Lower_Skin = np.zeros((N_RIBS - 1, 1))
    for i in range(0, N_RIBS - 1):
        for j in range(0, N_SPARS - 1):
            my_list = list((Curve_L_Rib_Spars[i, j], Curve_L_Rib_Spars[i + 1, j],
                            Curve_LL_Spar_Cap[i, j + 1],
                            Curve_LR_Spar_Cap[i, j]))
            STR_IDS = ' '.join(map(str, my_list))
            CMD = "*surfacemode 4\n*createmark lines 1 " + STR_IDS
            f.write(CMD)
            f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
            SURFACE_COUNTER += 1
            Surface_Lower_Skin[i, j] = SURFACE_COUNTER
        f.write('*createentity comps name="Lower_Skin_%.0f"\n'
                % (i + 1))
        f.write('*startnotehistorystate {Moved surfaces into component "Lower_Skin_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f-%.0f\n'
                % (Surface_Lower_Skin[i, 0], Surface_Lower_Skin[i, -1]))
        f.write('*movemark surfaces 1 "Lower_Skin_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Lower_Skin_%.0f"}\n'
                % (i + 1))
        COMPONENT_COUNTER += 1
        Component_Lower_Skin[i, 0] = COMPONENT_COUNTER
    f.write('*createentity assems name="Lower_Skin"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=3 components={comps %.0f-%.0f}'
            % (Component_Lower_Skin[0, 0], Component_Lower_Skin[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print upper skin surfaces
    Surface_Upper_Skin = np.zeros((N_RIBS - 1, N_SPARS - 1))
    Component_Upper_Skin = np.zeros((N_RIBS - 1, 1))
    for i in range(0, N_RIBS - 1):
        for j in range(0, N_SPARS - 1):
            my_list = list((Curve_U_Rib_Spars[i, j], Curve_U_Rib_Spars[i + 1, j],
                            Curve_UL_Spar_Cap[i, j + 1],
                            Curve_UR_Spar_Cap[i, j]))
            STR_IDS = ' '.join(map(str, my_list))
            CMD = "*surfacemode 4\n*createmark lines 1 " + STR_IDS
            f.write(CMD)
            f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
            SURFACE_COUNTER += 1
            Surface_Upper_Skin[i, j] = SURFACE_COUNTER
        f.write('*createentity comps name="Upper_Skin_%.0f"\n'
                % (i + 1))
        f.write('*startnotehistorystate {Moved surfaces into component "Upper_Skin_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f-%.0f\n'
                % (Surface_Upper_Skin[i, 0], Surface_Upper_Skin[i, -1]))
        f.write('*movemark surfaces 1 "Upper_Skin_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Upper_Skin_%.0f"}\n'
                % (i + 1))
        COMPONENT_COUNTER += 1
        Component_Upper_Skin[i, 0] = COMPONENT_COUNTER
    f.write('*createentity assems name="Upper_Skin"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=4 components={comps %.0f-%.0f}'
            % (Component_Upper_Skin[0, 0], Component_Upper_Skin[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print front rib surfaces
    Surface_Front_Rib = np.zeros((N_RIBS, 1))
    Component_Front_Rib = np.zeros((N_RIBS, 1))
    for i in range(0, N_RIBS):
        my_list = list((Curve_U_Rib_LE[i],
                        Curve_L_Rib_LE[i],
                        Curve_Spar_Cap_Left_iN_RIBS[i, 0]))
        STR_IDS = ' '.join(map(str, my_list))
        CMD = "*surfacemode 4\n*createmark lines 1 " + STR_IDS
        f.write(CMD)
        f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
        SURFACE_COUNTER += 1
        Surface_Front_Rib[i, 0] = SURFACE_COUNTER
        f.write('*createentity comps name="Front_Rib_%.0f"\n'
                % (i + 1))
        f.write('*startnotehistorystate {Moved surfaces into component "Front_Rib_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f\n'
                % (Surface_Front_Rib[i, 0]))
        f.write('*movemark surfaces 1 "Front_Rib_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Front_Rib_%.0f"}\n'
                % (i + 1))
        COMPONENT_COUNTER += 1
        Component_Front_Rib[i, 0] = COMPONENT_COUNTER
    f.write('*createentity assems name="Front_Rib"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=5 components={comps  %.0f-%.0f}'
            % (Component_Front_Rib[0, 0], Component_Front_Rib[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print rear rib surfaces
    Surface_Rear_Rib = np.zeros((N_RIBS, 1))
    Component_Rear_Rib = np.zeros((N_RIBS, 1))
    for i in range(0, N_RIBS):
        my_list = list((Curve_U_Rib_TE[i],
                        Curve_L_Rib_TE[i],
                        Curve_Spar_Cap_Right_iN_RIBS[i, - 1]))
        STR_IDS = ' '.join(map(str, my_list))
        CMD = "*surfacemode 4\n*createmark lines 1 " + STR_IDS
        f.write(CMD)
        f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
        SURFACE_COUNTER += 1
        Surface_Rear_Rib[i, 0] = SURFACE_COUNTER
        f.write('*createentity comps name="Rear_Rib_%.0f"\n'
                % (i + 1))
        f.write('*startnotehistorystate {Moved surfaces into component "Rear_Rib_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f\n'
                % (Surface_Rear_Rib[i, 0]))
        f.write('*movemark surfaces 1 "Rear_Rib_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Rear_Rib_%.0f"}\n'
                % (i + 1))
        COMPONENT_COUNTER += 1
        Component_Rear_Rib[i, 0] = COMPONENT_COUNTER
    f.write('*createentity assems name="Rear_Rib"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=6 components={comps %.0f-%.0f}'
            % (Component_Rear_Rib[0, 0], Component_Rear_Rib[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print front upper skin surfaces
    Surface_Front_Upper_Skin = np.zeros((N_RIBS - 1, 1))
    Component_Front_Upper_Skin = np.zeros((N_RIBS - 1, 1))
    for i in range(0, N_RIBS - 1):
        my_list = list((Curve_U_Rib_LE[i],
                        Curve_U_Rib_LE[i + 1],
                        Curve_UL_Spar_Cap[i, 0],
                        Curve_LE[i, 0]))
        STR_IDS = ' '.join(map(str, my_list))
        CMD = "*surfacemode 4\n*createmark lines 1 " + STR_IDS
        f.write(CMD)
        f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
        SURFACE_COUNTER += 1
        Surface_Front_Upper_Skin[i, 0] = SURFACE_COUNTER
        f.write('*createentity comps name="Front_Upper_Skin_%.0f"\n'
                % (i + 1))
        f.write('*startnotehistorystate {Moved surfaces into component "Front_Upper_Skin_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f\n'
                % (Surface_Front_Upper_Skin[i, 0]))
        f.write('*movemark surfaces 1 "Front_Upper_Skin_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Front_Upper_Skin_%.0f"}\n'
                % (i + 1))
        COMPONENT_COUNTER += 1
        Component_Front_Upper_Skin[i, 0] = COMPONENT_COUNTER
    f.write('*createentity assems name="Front_Upper_Skin"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=7 components={comps %.0f-%.0f}'
            % (Component_Front_Upper_Skin[0, 0], Component_Front_Upper_Skin[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print front lower skin surfaces
    Surface_Front_Lower_Skin = np.zeros((N_RIBS - 1, 1))
    Component_Front_Lower_Skin = np.zeros((N_RIBS - 1, 1))
    for i in range(0, N_RIBS - 1):
        my_list = list((Curve_L_Rib_LE[i],
                        Curve_L_Rib_LE[i + 1],
                        Curve_LL_Spar_Cap[i, 0],
                        Curve_LE[i, 0]))
        STR_IDS = ' '.join(map(str, my_list))
        CMD = "*surfacemode 4\n*createmark lines 1 " + STR_IDS
        f.write(CMD)
        f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
        SURFACE_COUNTER += 1
        Surface_Front_Lower_Skin[i, 0] = SURFACE_COUNTER
        f.write('*createentity comps name="Front_Lower_Skin_%.0f"\n'
                % (i + 1))
        f.write('*startnotehistorystate {Moved surfaces into component "Front_Lower_Skin_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f\n'
                % (Surface_Front_Lower_Skin[i, 0]))
        f.write('*movemark surfaces 1 "Front_Lower_Skin_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Front_Lower_Skin_%.0f"}\n'
                % (i + 1))
        COMPONENT_COUNTER += 1
        Component_Front_Lower_Skin[i, 0] = COMPONENT_COUNTER
    f.write('*createentity assems name="Front_Lower_Skin"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=8 components={comps %.0f-%.0f}'
            % (Component_Front_Lower_Skin[0, 0], Component_Front_Lower_Skin[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print rear upper skin surfaces
    Surface_Rear_Upper_Skin = np.zeros((N_RIBS - 1, 1))
    Component_Rear_Upper_Skin = np.zeros((N_RIBS - 1, 1))
    for i in range(0, N_RIBS - 1):
        my_list = list((Curve_U_Rib_TE[i],
                        Curve_U_Rib_TE[i + 1],
                        Curve_UR_Spar_Cap[i, - 1],
                        Curve_TE[i, 0]))
        STR_IDS = ' '.join(map(str, my_list))
        CMD = "*surfacemode 4\n*createmark lines 1 " + STR_IDS
        f.write(CMD)
        f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
        SURFACE_COUNTER += 1
        Surface_Rear_Upper_Skin[i, 0] = SURFACE_COUNTER
        f.write('*createentity comps name="Rear_Upper_Skin_%.0f"\n'
                % (i + 1))
        f.write('*startnotehistorystate {Moved surfaces into component "Rear_Upper_Skin_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f\n'
                % (Surface_Rear_Upper_Skin[i, 0]))
        f.write('*movemark surfaces 1 "Rear_Upper_Skin_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Rear_Upper_Skin_%.0f"}\n'
                % (i + 1))
        COMPONENT_COUNTER += 1
        Component_Rear_Upper_Skin[i, 0] = COMPONENT_COUNTER
    f.write('*createentity assems name="Rear_Upper_Skin"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=9 components={comps %.0f-%.0f}'
            % (Component_Rear_Upper_Skin[0, 0], Component_Rear_Upper_Skin[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print rear lower skin surfaces
    Surface_Rear_Lower_Skin = np.zeros((N_RIBS - 1, 1))
    Component_Rear_Lower_Skin = np.zeros((N_RIBS - 1, 1))
    for i in range(0, N_RIBS - 1):
        my_list = list((Curve_L_Rib_TE[i],
                        Curve_L_Rib_TE[i + 1],
                        Curve_LR_Spar_Cap[i, - 1],
                        Curve_TE[i, 0]))
        STR_IDS = ' '.join(map(str, my_list))
        CMD = "*surfacemode 4\n*createmark lines 1 " + STR_IDS
        f.write(CMD)
        f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
        SURFACE_COUNTER += 1
        Surface_Rear_Lower_Skin[i, 0] = SURFACE_COUNTER
        f.write('*createentity comps name="Rear_Lower_Skin_%.0f"\n'
                % (i + 1))
        f.write('*startnotehistorystate {Moved surfaces into component "Rear_Lower_Skin_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f\n'
                % (Surface_Rear_Lower_Skin[i, 0]))
        f.write('*movemark surfaces 1 "Rear_Lower_Skin_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Rear_Lower_Skin_%.0f"}\n'
                % (i + 1))
        COMPONENT_COUNTER += 1
        Component_Rear_Lower_Skin[i, 0] = COMPONENT_COUNTER
    f.write('*createentity assems name="Rear_Lower_Skin"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=10 components={comps %.0f-%.0f}'
            % (Component_Rear_Lower_Skin[0, 0], Component_Rear_Lower_Skin[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print upper left spar cap surfaces
    Surface_Spar_Cap_Upper_Left = np.zeros((N_RIBS - 1, N_SPARS))
    Component_Spar_Cap_Upper_Left = np.zeros((N_RIBS - 1, 1))
    for i in range(0, N_RIBS - 1):
        for j in range(0, N_SPARS):
            my_list = list((Curve_UL_Spar_Cap[i, j], Curve_U_Spar[i, j],
                            Curve_U_Rib_SC_L[i + 1, j],
                            Curve_U_Rib_SC_L[i, j]))
            STR_IDS = ' '.join(map(str, my_list))
            CMD = "*surfacemode 4\n*createmark lines 1 " + STR_IDS
            f.write(CMD)
            f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
            SURFACE_COUNTER += 1
            Surface_Spar_Cap_Upper_Left[i, j] = SURFACE_COUNTER
        f.write('*createentity comps name="Spar_Cap_Upper_Left_%.0f"\n'
                % (i + 1))
        f.write('*startnotehistorystate {Moved surfaces into component "Spar_Cap_Upper_Left_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f-%.0f\n'
                % (Surface_Spar_Cap_Upper_Left[i, 0], Surface_Spar_Cap_Upper_Left[i, -1]))
        f.write('*movemark surfaces 1 "Spar_Cap_Upper_Left_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Spar_Cap_Upper_Left_%.0f"}\n'
                % (i + 1))
        COMPONENT_COUNTER += 1
        Component_Spar_Cap_Upper_Left[i, 0] = COMPONENT_COUNTER
    f.write('*createentity assems name="Spar_Caps_Upper_Left_"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=11 components={comps %.0f-%.0f}'
            % (Component_Spar_Cap_Upper_Left[0, 0], Component_Spar_Cap_Upper_Left[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print upper right spar cap surfaces
    Surface_Spar_Cap_Upper_Right = np.zeros((N_RIBS - 1, N_SPARS))
    Component_Spar_Cap_Upper_Right = np.zeros((N_RIBS - 1, 1))
    for i in range(0, N_RIBS - 1):
        for j in range(0, N_SPARS):
            my_list = list((Curve_UR_Spar_Cap[i, j], Curve_U_Spar[i, j],
                            Curve_U_Rib_SC_R[i + 1, j],
                            Curve_U_Rib_SC_R[i, j]))
            STR_IDS = ' '.join(map(str, my_list))
            CMD = "*surfacemode 4\n*createmark lines 1 " + STR_IDS
            f.write(CMD)
            f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
            SURFACE_COUNTER += 1
            Surface_Spar_Cap_Upper_Right[i, j] = SURFACE_COUNTER
        f.write('*createentity comps name="Spar_Cap_Upper_Right_%.0f"\n'
                % (i + 1))
        f.write('*startnotehistorystate {Moved surfaces into component "Spar_Cap_Upper_Right_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f-%.0f\n'
                % (Surface_Spar_Cap_Upper_Right[i, 0], Surface_Spar_Cap_Upper_Right[i, -1]))
        f.write('*movemark surfaces 1 "Spar_Cap_Upper_Right_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Spar_Cap_Upper_Right_%.0f"}\n'
                % (i + 1))
        COMPONENT_COUNTER += 1
        Component_Spar_Cap_Upper_Right[i, 0] = COMPONENT_COUNTER
    f.write('*createentity assems name="Spar_Caps_Upper_Right_"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=12 components={comps %.0f-%.0f}'
            % (Component_Spar_Cap_Upper_Right[0, 0], Component_Spar_Cap_Upper_Right[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print lower left spar cap surfaces
    Surface_Spar_Cap_Lower_Left = np.zeros((N_RIBS - 1, N_SPARS))
    Component_Spar_Cap_Lower_Left = np.zeros((N_RIBS - 1, 1))
    for i in range(0, N_RIBS - 1):
        for j in range(0, N_SPARS):
            my_list = list((Curve_LL_Spar_Cap[i, j], Curve_L_Spar[i, j],
                            Curve_L_Rib_SC_L[i + 1, j],
                            Curve_L_Rib_SC_L[i, j]))
            STR_IDS = ' '.join(map(str, my_list))
            CMD = "*surfacemode 4\n*createmark lines 1 " + STR_IDS
            f.write(CMD)
            f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
            SURFACE_COUNTER += 1
            Surface_Spar_Cap_Lower_Left[i, j] = SURFACE_COUNTER
        f.write('*createentity comps name="Spar_Cap_Lower_Left_%.0f"\n'
                % (i + 1))
        f.write('*startnotehistorystate {Moved surfaces into component "Spar_Cap_Lower_Left_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f-%.0f\n'
                % (Surface_Spar_Cap_Lower_Left[i, 0], Surface_Spar_Cap_Lower_Left[i, -1]))
        f.write('*movemark surfaces 1 "Spar_Cap_Lower_Left_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Spar_Cap_Lower_Left_%.0f"}\n'
                % (i + 1))
        COMPONENT_COUNTER += 1
        Component_Spar_Cap_Lower_Left[i, 0] = COMPONENT_COUNTER
    f.write('*createentity assems name="Spar_Caps_Lower_Left_"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=13 components={comps %.0f-%.0f}'
            % (Component_Spar_Cap_Lower_Left[0, 0], Component_Spar_Cap_Lower_Left[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print lower right spar cap surfaces
    Surface_Spar_Cap_Lower_Right = np.zeros((N_RIBS - 1, N_SPARS))
    Component_Spar_Cap_Lower_Right = np.zeros((N_RIBS - 1, 1))
    for i in range(0, N_RIBS - 1):
        for j in range(0, N_SPARS):
            my_list = list((Curve_LR_Spar_Cap[i, j], Curve_L_Spar[i, j],
                            Curve_L_Rib_SC_R[i + 1, j],
                            Curve_L_Rib_SC_R[i, j]))
            STR_IDS = ' '.join(map(str, my_list))
            CMD = "*surfacemode 4\n*createmark lines 1 " + STR_IDS
            f.write(CMD)
            f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
            SURFACE_COUNTER += 1
            Surface_Spar_Cap_Lower_Right[i, j] = SURFACE_COUNTER
        f.write('*createentity comps name="Spar_Cap_Lower_Right_%.0f"\n'
                % (i + 1))
        f.write('*startnotehistorystate {Moved surfaces into component "Spar_Cap_Lower_Right_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f-%.0f\n'
                % (Surface_Spar_Cap_Lower_Right[i, 0], Surface_Spar_Cap_Lower_Right[i, -1]))
        f.write('*movemark surfaces 1 "Spar_Cap_Lower_Right_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Spar_Cap_Lower_Right_%.0f"}\n'
                % (i + 1))
        COMPONENT_COUNTER += 1
        Component_Spar_Cap_Lower_Right[i, 0] = COMPONENT_COUNTER
    f.write('*createentity assems name="Spar_Caps_Lower_Right_"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=14 components={comps %.0f-%.0f}'
            % (Component_Spar_Cap_Lower_Right[0, 0], Component_Spar_Cap_Lower_Right[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Clear all nodes
    f.write("*nodecleartempmark\n")

    # Clean-up the geometry
    my_list = list(range(1, SURFACE_COUNTER + 1))
    STR_IDS = ' '.join(map(str, my_list))
    CMD = "*createmark surfaces 1 " + STR_IDS
    f.write(CMD)
    f.write('\n*selfstitchcombine 1 146 0.01 0.01\n')
    # f.write('\n*multi_surfs_lines_merge 1 0 0\n*normalsoff\n')
    # Save the file and close
    # f.write("*writefile \"C:/Users/efilippo/Documents/"
    #         "ASD_Lab_Parametric_Design_of_Wing_OOP/HM_Files/wing.hm\" 1\n")
    f.write("*writefile \"C:/Users/Vagelis/Documents/UC3M_Internship/Python/"
            "ASD_Lab_Parametric_Design_of_Wing_OOP/HM_Files/wing.hm\" 1\n")
    f.write("return; # Stop script and return to application\n*quit 1;\n")

f.close()


"""
################## Running the Command file: ##################
"""

# Location of .tcl script and run
TCL_SCRIPT_PATH = "/ASD_Lab_Parametric_Design_of_Wing_OOP/"\
                    "Wing_Geometry_Generation.tcl"
run_argument(TCL_SCRIPT_PATH)

# End time counter
toc = time.perf_counter()
# Print time
print(f"Script run in {toc - tic:0.3f} seconds")
