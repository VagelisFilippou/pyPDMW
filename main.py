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

import matplotlib.pyplot as plt
import numpy as np
import time
from derive_geometry import DerivedGeometry
from read_crm_data_incl import RibsInclined
from Spar_and_Spar_Caps_Coords import SparsAndCapsCoords
from Store_Spar_IDs import SparsCapsIDs
from Connection_Nodes import ConnectionNodes
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
SemiSpan = 29.38
YB_percent = 0.37  # Yehudi Break in Percent of Semispan

# Define Wing's Structural Parameters
N_spars = 3  # Number of spars
N_ribs_central = 5  # Number of equally spaced ribs
N_ribs_yehudi = 5  # Number of equally spaced ribs
N_ribs_semispan = 5  # Number of equally spaced ribs

# List with the location of each spar
Spars_position = np.linspace(0.1, 0.7, num=N_spars, endpoint=True)

# Specify the length of the fuselage wingbox
Fuselage_section_percent = 0.1

# Define two widths per spar at the root and at the tip: UL, UR, LL, LR
SC_width = np.array([[0.3, 0.3], [0.1, 0.1]]) * 0.6

"""
################## Derive the Geometry and its' Parameters: ##################
"""

Parameters = DerivedGeometry(SemiSpan,
                             YB_percent,
                             N_spars,
                             N_ribs_central,
                             N_ribs_yehudi,
                             N_ribs_semispan,
                             Spars_position,
                             Fuselage_section_percent,
                             SC_width)

wing = RibsInclined(Parameters.Y_list,
                    Spars_position,
                    Parameters.Origin[:, 0],
                    Parameters.Rib_Sections_ID)


X, Y, Z = wing.X, wing.Y, wing.Z

N_ribs = Parameters.N_ribs
Origin = Parameters.Origin
Rib_Sections_ID = Parameters.Rib_Sections_ID
n = Parameters.n

"""
### Spar and spar caps coordinates: ###
"""

Spars_And_Spar_Caps = SparsAndCapsCoords(Parameters,
                                         wing,
                                         N_spars,
                                         Spars_position,
                                         SC_width,
                                         SemiSpan)
Spars_nodes_X = Spars_And_Spar_Caps.Spars_nodes_X
Spars_nodes_Y = Spars_And_Spar_Caps.Spars_nodes_Y
Spar_Caps_XL = Spars_And_Spar_Caps.Spar_Caps_XL
Spar_Caps_XR = Spars_And_Spar_Caps.Spar_Caps_XR
Spar_Caps_YL = Spars_And_Spar_Caps.Spar_Caps_YL
Spar_Caps_YR = Spars_And_Spar_Caps.Spar_Caps_YR

"""
### Put the spars' coordinates in the XYZ arrays and store their index: ###
"""

XYZ = SparsCapsIDs(Spars_And_Spar_Caps, X, Y, Z, N_ribs, N_spars, n)

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

Con_Nodes = ConnectionNodes(Parameters, XYZ, N_spars)
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
curvecounter = 0
surfacecounter = 0
componentcounter = 1

# Open a .tcl file and write the commands there
with open('Wing_Geometry_Generation.tcl', 'w') as f:
    f.write('#----------Commands for wing geometry generation----------\n')
    # Change node tolerance
    f.write('*toleranceset 0.01\n')

    # Now print nodes in this format: *createnode x y z system id 0 0
    for i in range(0, N_ribs):
        for j in range(0, 2 * n):
            # Free point
            # f.write('*createpoint %.7f %.7f %.7f 0\n'
            # % (X[i, j], Y[i, j], Z[i, j]))
            # Nodes
            f.write('*createnode %.7f %.7f %.7f 0 0 0\n'
                    % (X[i, j], Y[i, j], Z[i, j]))

    # Print upper rib curves
    Curve_U_Rib = np.zeros((N_ribs, 3 * N_spars + 1))
    for i in range(0, N_ribs):
        for j in range(0, 3 * N_spars + 1):
            my_list = list(range(Curve_IDs_Upper[i, j + 1], Curve_IDs_Upper[i, j] + 1))
            my_str = ' '.join(map(str, my_list))
            cmd = "*createlist nodes 1 " + my_str
            f.write(cmd)
            f.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0\n"
                    "*linecreatespline nodes 1 0 0 1 2\n")
            curvecounter += 1
            Curve_U_Rib[i, j] = curvecounter

    # Store the id of each curve type
    Curve_U_Rib_LE = Curve_U_Rib[:, 0]
    Curve_U_Rib_TE = Curve_U_Rib[:, -1]
    Curve_U_Rib_SC_L = np.zeros((N_ribs, N_spars))
    Curve_U_Rib_SC_R = np.zeros((N_ribs, N_spars))
    Curve_U_Rib_Spars = np.zeros((N_ribs, N_spars - 1))
    for i in range(0, N_spars):
        if i < N_spars - 1:
            Curve_U_Rib_SC_L[:, i] = Curve_U_Rib[:, 3 * i + 1]
            Curve_U_Rib_SC_R[:, i] = Curve_U_Rib[:, 3 * i + 2]
            Curve_U_Rib_Spars[:, i] = Curve_U_Rib[:, 3 * i + 3]
        elif i == N_spars - 1:
            Curve_U_Rib_SC_L[:, i] = Curve_U_Rib[:, 3 * i + 1]
            Curve_U_Rib_SC_R[:, i] = Curve_U_Rib[:, 3 * i + 2]

    # Print lower rib curves
    Curve_L_Rib = np.zeros((N_ribs, 3 * N_spars + 1))
    for i in range(0, N_ribs):
        for j in range(0, 3 * N_spars + 1):
            my_list = list(range(Curve_IDs_Lower[i, j], Curve_IDs_Lower[i, j + 1] + 1))
            my_str = ' '.join(map(str, my_list))
            cmd = "*createlist nodes 1 " + my_str
            f.write(cmd)
            f.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0\n"
                    "*linecreatespline nodes 1 0 0 1 2\n")
            curvecounter += 1
            Curve_L_Rib[i, j] = curvecounter

    # Store the id of each curve type
    Curve_L_Rib_LE = Curve_L_Rib[:, 0]
    Curve_L_Rib_TE = Curve_L_Rib[:, -1]
    Curve_L_Rib_SC_L = np.zeros((N_ribs, N_spars))
    Curve_L_Rib_SC_R = np.zeros((N_ribs, N_spars))
    Curve_L_Rib_Spars = np.zeros((N_ribs, N_spars - 1))
    for i in range(0, N_spars):
        if i < N_spars - 1:
            Curve_L_Rib_SC_L[:, i] = Curve_L_Rib[:, 3 * i + 1]
            Curve_L_Rib_SC_R[:, i] = Curve_L_Rib[:, 3 * i + 2]
            Curve_L_Rib_Spars[:, i] = Curve_L_Rib[:, 3 * i + 3]
        elif i == N_spars - 1:
            Curve_L_Rib_SC_L[:, i] = Curve_L_Rib[:, 3 * i + 1]
            Curve_L_Rib_SC_R[:, i] = Curve_L_Rib[:, 3 * i + 2]

    # Print LE and TE curves
    Curve_LE = np.zeros((N_ribs - 1, 1))
    Curve_TE = np.zeros((N_ribs - 1, 1))
    for i in range(0, N_ribs - 1):
        my_list = [i * 2 * n + 1, (i + 1) * 2 * n + 1]
        my_str = ' '.join(map(str, my_list))
        cmd = "*createlist nodes 1 " + my_str
        f.write(cmd)
        f.write("\n*linecreatefromnodes 1 0 150 5 179\n")
        curvecounter += 1
        Curve_TE[i, 0] = curvecounter
    for i in range(0, N_ribs - 1):
        my_list = [LE_IDs[i, 0], LE_IDs[i + 1, 0]]
        my_str = ' '.join(map(str, my_list))
        cmd = "*createlist nodes 1 " + my_str
        f.write(cmd)
        f.write("\n*linecreatefromnodes 1 0 150 5 179\n")
        curvecounter += 1
        Curve_LE[i, 0] = curvecounter

    # Print spar curves in ribs
    Curve_Spar_in_Ribs = np.zeros((N_ribs, N_spars))
    for i in range(0, N_ribs):
        for j in range(0, N_spars):
            my_list = list((Spar_ID_Upper[i, j], Spar_ID_Lower[i, j]))
            my_str = ' '.join(map(str, my_list))
            cmd = "*createlist nodes 1 " + my_str
            f.write(cmd)
            f.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0\n"
                    "*linecreatespline nodes 1 0 0 1 2\n")
            curvecounter += 1
            Curve_Spar_in_Ribs[i, j] = curvecounter

    # Print left spar cap curves in ribs
    Curve_Spar_Cap_Left_in_Ribs = np.zeros((N_ribs, N_spars))
    for i in range(0, N_ribs):
        for j in range(0, N_spars):
            my_list = list((Spar_Cap_ID_Lower_Left[i, j], Spar_Cap_ID_Upper_Left[i, j]))
            my_str = ' '.join(map(str, my_list))
            cmd = "*createlist nodes 1 " + my_str
            f.write(cmd)
            f.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0\n"
                    "*linecreatespline nodes 1 0 0 1 2\n")
            curvecounter += 1
            Curve_Spar_Cap_Left_in_Ribs[i, j] = curvecounter

    # Print right spar cap curves in ribs
    Curve_Spar_Cap_Right_in_Ribs = np.zeros((N_ribs, N_spars))
    for i in range(0, N_ribs):
        for j in range(0, N_spars):
            my_list = list((Spar_Cap_ID_Lower_Right[i, j], Spar_Cap_ID_Upper_Right[i, j]))
            my_str = ' '.join(map(str, my_list))
            cmd = "*createlist nodes 1 " + my_str
            f.write(cmd)
            f.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0\n"
                    "*linecreatespline nodes 1 0 0 1 2\n")
            curvecounter += 1
            Curve_Spar_Cap_Right_in_Ribs[i, j] = curvecounter

    # Print upper spar curves
    Curve_U_Spar = np.zeros((N_ribs - 1, N_spars))
    for i in range(0, N_ribs - 1):
        for j in range(0, N_spars):
            my_list = list((Spar_ID_Upper[i, j], Spar_ID_Upper[i + 1, j]))
            my_str = ' '.join(map(str, my_list))
            cmd = "*createlist nodes 1 " + my_str
            f.write(cmd)
            f.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0\n"
                    "*linecreatespline nodes 1 0 0 1 2\n")
            curvecounter += 1
            Curve_U_Spar[i, j] = curvecounter

    # Print lower spar curves
    Curve_L_Spar = np.zeros((N_ribs - 1, N_spars))
    for i in range(0, N_ribs - 1):
        for j in range(0, N_spars):
            my_list = list((Spar_ID_Lower[i, j], Spar_ID_Lower[i + 1, j]))
            my_str = ' '.join(map(str, my_list))
            cmd = "*createlist nodes 1 " + my_str
            f.write(cmd)
            f.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0\n"
                    "*linecreatespline nodes 1 0 0 1 2\n")
            curvecounter += 1
            Curve_L_Spar[i, j] = curvecounter

    # Print upper left spar cap curves
    Curve_UL_Spar_Cap = np.zeros((N_ribs - 1, N_spars))
    for i in range(0, N_ribs - 1):
        for j in range(0, N_spars):
            my_list = list((Spar_Cap_ID_Upper_Left[i, j], Spar_Cap_ID_Upper_Left[i + 1, j]))
            my_str = ' '.join(map(str, my_list))
            cmd = "*createlist nodes 1 " + my_str
            f.write(cmd)
            f.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0\n"
                    "*linecreatespline nodes 1 0 0 1 2\n")
            curvecounter += 1
            Curve_UL_Spar_Cap[i, j] = curvecounter

    # Print lower left spar cap curves
    Curve_LL_Spar_Cap = np.zeros((N_ribs - 1, N_spars))
    for i in range(0, N_ribs - 1):
        for j in range(0, N_spars):
            my_list = list((Spar_Cap_ID_Lower_Left[i, j], Spar_Cap_ID_Lower_Left[i + 1, j]))
            my_str = ' '.join(map(str, my_list))
            cmd = "*createlist nodes 1 " + my_str
            f.write(cmd)
            f.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0\n"
                    "*linecreatespline nodes 1 0 0 1 2\n")
            curvecounter += 1
            Curve_LL_Spar_Cap[i, j] = curvecounter

    # Print upper right spar cap curves
    Curve_UR_Spar_Cap = np.zeros((N_ribs - 1, N_spars))
    for i in range(0, N_ribs - 1):
        for j in range(0, N_spars):
            my_list = list((Spar_Cap_ID_Upper_Right[i, j], Spar_Cap_ID_Upper_Right[i + 1, j]))
            my_str = ' '.join(map(str, my_list))
            cmd = "*createlist nodes 1 " + my_str
            f.write(cmd)
            f.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0\n"
                    "*linecreatespline nodes 1 0 0 1 2\n")
            curvecounter += 1
            Curve_UR_Spar_Cap[i, j] = curvecounter

    # Print lower right spar cap curves
    Curve_LR_Spar_Cap = np.zeros((N_ribs - 1, N_spars))
    for i in range(0, N_ribs - 1):
        for j in range(0, N_spars):
            my_list = list((Spar_Cap_ID_Lower_Right[i, j], Spar_Cap_ID_Lower_Right[i + 1, j]))
            my_str = ' '.join(map(str, my_list))
            cmd = "*createlist nodes 1 " + my_str
            f.write(cmd)
            f.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0\n"
                    "*linecreatespline nodes 1 0 0 1 2\n")
            curvecounter += 1
            Curve_LR_Spar_Cap[i, j] = curvecounter

    # Print left spar cap rib surfaces
    Surface_LSC_Rib = np.zeros((N_ribs, N_spars))
    Component_LSC_Rib = np.zeros((N_ribs, 1))
    for i in range(0, N_ribs):
        for j in range(0, N_spars):
            my_list = list((Curve_U_Rib_SC_L[i, j],
                            Curve_L_Rib_SC_L[i, j],
                            Curve_Spar_Cap_Left_in_Ribs[i, j],
                            Curve_Spar_in_Ribs[i, j]))
            my_str = ' '.join(map(str, my_list))
            cmd = "*surfacemode 4\n*createmark lines 1 " + my_str
            f.write(cmd)
            f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
            surfacecounter += 1
            Surface_LSC_Rib[i, j] = surfacecounter
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
        componentcounter += 1
        Component_LSC_Rib[i, 0] = componentcounter
    f.write('*createentity assems name="WingBox_Ribs"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=1 components={comps %.0f-%.0f}'
            % (Component_LSC_Rib[0, 0], Component_LSC_Rib[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print right spar cap rib surfaces
    Surface_RSC_Rib = np.zeros((N_ribs, N_spars))
    Component_RSC_Rib = np.zeros((N_ribs, 1))
    for i in range(0, N_ribs):
        for j in range(0, N_spars):
            my_list = list((Curve_U_Rib_SC_R[i, j],
                            Curve_L_Rib_SC_R[i, j],
                            Curve_Spar_Cap_Right_in_Ribs[i, j],
                            Curve_Spar_in_Ribs[i, j]))
            my_str = ' '.join(map(str, my_list))
            cmd = "*surfacemode 4\n*createmark lines 1 " + my_str
            f.write(cmd)
            f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
            surfacecounter += 1
            Surface_RSC_Rib[i, j] = surfacecounter
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
        componentcounter += 1
        Component_RSC_Rib[i, 0] = componentcounter
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=1 components={comps %.0f-%.0f}'
            % (Component_RSC_Rib[0, 0], Component_RSC_Rib[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print main rib surfaces
    Surface_Rib = np.zeros((N_ribs, N_spars - 1))
    Component_Rib = np.zeros((N_ribs, 1))
    for i in range(0, N_ribs):
        for j in range(0, N_spars - 1):
            my_list = list((Curve_U_Rib_Spars[i, j],
                            Curve_L_Rib_Spars[i, j],
                            Curve_Spar_Cap_Right_in_Ribs[i, j],
                            Curve_Spar_Cap_Left_in_Ribs[i, j + 1]))
            my_str = ' '.join(map(str, my_list))
            cmd = "*surfacemode 4\n*createmark lines 1 " + my_str
            f.write(cmd)
            f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
            surfacecounter += 1
            Surface_Rib[i, j] = surfacecounter
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
        componentcounter += 1
        Component_Rib[i, 0] = componentcounter
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=1 components={comps %.0f-%.0f}'
            % (Component_Rib[0, 0], Component_Rib[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print spar surfaces
    Surface_Spar = np.zeros((N_ribs - 1, N_spars))
    Component_Spar = np.zeros((N_ribs - 1, 1))
    for i in range(0, N_ribs - 1):
        for j in range(0, N_spars):
            my_list = list((Curve_L_Spar[i, j], Curve_U_Spar[i, j],
                            Curve_Spar_in_Ribs[i, j],
                            Curve_Spar_in_Ribs[i + 1, j]))
            my_str = ' '.join(map(str, my_list))
            cmd = "*surfacemode 4\n*createmark lines 1 " + my_str
            f.write(cmd)
            f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
            surfacecounter += 1
            Surface_Spar[i, j] = surfacecounter
        f.write('*createentity comps name="Spar_%.0f"\n'
                % (i + 1))
        f.write('*startnotehistorystate {Moved surfaces into component "Spar_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f-%.0f\n'
                % (Surface_Spar[i, 0], Surface_Spar[i, -1]))
        f.write('*movemark surfaces 1 "Spar_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Spar_%.0f"}\n'
                % (i + 1))
        componentcounter += 1
        Component_Spar[i, 0] = componentcounter
    f.write('*createentity assems name="Spars"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=2 components={comps %.0f-%.0f}'
            % (Component_Spar[0, 0], Component_Spar[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print lower skin surfaces
    Surface_Lower_Skin = np.zeros((N_ribs - 1, N_spars - 1))
    Component_Lower_Skin = np.zeros((N_ribs - 1, 1))
    for i in range(0, N_ribs - 1):
        for j in range(0, N_spars - 1):
            my_list = list((Curve_L_Rib_Spars[i, j], Curve_L_Rib_Spars[i + 1, j],
                            Curve_LL_Spar_Cap[i, j + 1],
                            Curve_LR_Spar_Cap[i, j]))
            my_str = ' '.join(map(str, my_list))
            cmd = "*surfacemode 4\n*createmark lines 1 " + my_str
            f.write(cmd)
            f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
            surfacecounter += 1
            Surface_Lower_Skin[i, j] = surfacecounter
        f.write('*createentity comps name="Lower_Skin_%.0f"\n'
                % (i + 1))
        f.write('*startnotehistorystate {Moved surfaces into component "Lower_Skin_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f-%.0f\n'
                % (Surface_Lower_Skin[i, 0], Surface_Lower_Skin[i, -1]))
        f.write('*movemark surfaces 1 "Lower_Skin_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Lower_Skin_%.0f"}\n'
                % (i + 1))
        componentcounter += 1
        Component_Lower_Skin[i, 0] = componentcounter
    f.write('*createentity assems name="Lower_Skin"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=3 components={comps %.0f-%.0f}'
            % (Component_Lower_Skin[0, 0], Component_Lower_Skin[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print upper skin surfaces
    Surface_Upper_Skin = np.zeros((N_ribs - 1, N_spars - 1))
    Component_Upper_Skin = np.zeros((N_ribs - 1, 1))
    for i in range(0, N_ribs - 1):
        for j in range(0, N_spars - 1):
            my_list = list((Curve_U_Rib_Spars[i, j], Curve_U_Rib_Spars[i + 1, j],
                            Curve_UL_Spar_Cap[i, j + 1],
                            Curve_UR_Spar_Cap[i, j]))
            my_str = ' '.join(map(str, my_list))
            cmd = "*surfacemode 4\n*createmark lines 1 " + my_str
            f.write(cmd)
            f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
            surfacecounter += 1
            Surface_Upper_Skin[i, j] = surfacecounter
        f.write('*createentity comps name="Upper_Skin_%.0f"\n'
                % (i + 1))
        f.write('*startnotehistorystate {Moved surfaces into component "Upper_Skin_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f-%.0f\n'
                % (Surface_Upper_Skin[i, 0], Surface_Upper_Skin[i, -1]))
        f.write('*movemark surfaces 1 "Upper_Skin_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Upper_Skin_%.0f"}\n'
                % (i + 1))
        componentcounter += 1
        Component_Upper_Skin[i, 0] = componentcounter
    f.write('*createentity assems name="Upper_Skin"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=4 components={comps %.0f-%.0f}'
            % (Component_Upper_Skin[0, 0], Component_Upper_Skin[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print front rib surfaces
    Surface_Front_Rib = np.zeros((N_ribs, 1))
    Component_Front_Rib = np.zeros((N_ribs, 1))
    for i in range(0, N_ribs):
        my_list = list((Curve_U_Rib_LE[i],
                        Curve_L_Rib_LE[i],
                        Curve_Spar_Cap_Left_in_Ribs[i, 0]))
        my_str = ' '.join(map(str, my_list))
        cmd = "*surfacemode 4\n*createmark lines 1 " + my_str
        f.write(cmd)
        f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
        surfacecounter += 1
        Surface_Front_Rib[i, 0] = surfacecounter
        f.write('*createentity comps name="Front_Rib_%.0f"\n'
                % (i + 1))
        f.write('*startnotehistorystate {Moved surfaces into component "Front_Rib_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f\n'
                % (Surface_Front_Rib[i, 0]))
        f.write('*movemark surfaces 1 "Front_Rib_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Front_Rib_%.0f"}\n'
                % (i + 1))
        componentcounter += 1
        Component_Front_Rib[i, 0] = componentcounter
    f.write('*createentity assems name="Front_Rib"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=5 components={comps  %.0f-%.0f}'
            % (Component_Front_Rib[0, 0], Component_Front_Rib[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print rear rib surfaces
    Surface_Rear_Rib = np.zeros((N_ribs, 1))
    Component_Rear_Rib = np.zeros((N_ribs, 1))
    for i in range(0, N_ribs):
        my_list = list((Curve_U_Rib_TE[i],
                        Curve_L_Rib_TE[i],
                        Curve_Spar_Cap_Right_in_Ribs[i, - 1]))
        my_str = ' '.join(map(str, my_list))
        cmd = "*surfacemode 4\n*createmark lines 1 " + my_str
        f.write(cmd)
        f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
        surfacecounter += 1
        Surface_Rear_Rib[i, 0] = surfacecounter
        f.write('*createentity comps name="Rear_Rib_%.0f"\n'
                % (i + 1))
        f.write('*startnotehistorystate {Moved surfaces into component "Rear_Rib_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f\n'
                % (Surface_Rear_Rib[i, 0]))
        f.write('*movemark surfaces 1 "Rear_Rib_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Rear_Rib_%.0f"}\n'
                % (i + 1))
        componentcounter += 1
        Component_Rear_Rib[i, 0] = componentcounter
    f.write('*createentity assems name="Rear_Rib"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=6 components={comps %.0f-%.0f}'
            % (Component_Rear_Rib[0, 0], Component_Rear_Rib[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print front upper skin surfaces
    Surface_Front_Upper_Skin = np.zeros((N_ribs - 1, 1))
    Component_Front_Upper_Skin = np.zeros((N_ribs - 1, 1))
    for i in range(0, N_ribs - 1):
        my_list = list((Curve_U_Rib_LE[i],
                        Curve_U_Rib_LE[i + 1],
                        Curve_UL_Spar_Cap[i, 0],
                        Curve_LE[i, 0]))
        my_str = ' '.join(map(str, my_list))
        cmd = "*surfacemode 4\n*createmark lines 1 " + my_str
        f.write(cmd)
        f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
        surfacecounter += 1
        Surface_Front_Upper_Skin[i, 0] = surfacecounter
        f.write('*createentity comps name="Front_Upper_Skin_%.0f"\n'
                % (i + 1))
        f.write('*startnotehistorystate {Moved surfaces into component "Front_Upper_Skin_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f\n'
                % (Surface_Front_Upper_Skin[i, 0]))
        f.write('*movemark surfaces 1 "Front_Upper_Skin_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Front_Upper_Skin_%.0f"}\n'
                % (i + 1))
        componentcounter += 1
        Component_Front_Upper_Skin[i, 0] = componentcounter
    f.write('*createentity assems name="Front_Upper_Skin"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=7 components={comps %.0f-%.0f}'
            % (Component_Front_Upper_Skin[0, 0], Component_Front_Upper_Skin[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print front lower skin surfaces
    Surface_Front_Lower_Skin = np.zeros((N_ribs - 1, 1))
    Component_Front_Lower_Skin = np.zeros((N_ribs - 1, 1))
    for i in range(0, N_ribs - 1):
        my_list = list((Curve_L_Rib_LE[i],
                        Curve_L_Rib_LE[i + 1],
                        Curve_LL_Spar_Cap[i, 0],
                        Curve_LE[i, 0]))
        my_str = ' '.join(map(str, my_list))
        cmd = "*surfacemode 4\n*createmark lines 1 " + my_str
        f.write(cmd)
        f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
        surfacecounter += 1
        Surface_Front_Lower_Skin[i, 0] = surfacecounter
        f.write('*createentity comps name="Front_Lower_Skin_%.0f"\n'
                % (i + 1))
        f.write('*startnotehistorystate {Moved surfaces into component "Front_Lower_Skin_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f\n'
                % (Surface_Front_Lower_Skin[i, 0]))
        f.write('*movemark surfaces 1 "Front_Lower_Skin_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Front_Lower_Skin_%.0f"}\n'
                % (i + 1))
        componentcounter += 1
        Component_Front_Lower_Skin[i, 0] = componentcounter
    f.write('*createentity assems name="Front_Lower_Skin"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=8 components={comps %.0f-%.0f}'
            % (Component_Front_Lower_Skin[0, 0], Component_Front_Lower_Skin[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print rear upper skin surfaces
    Surface_Rear_Upper_Skin = np.zeros((N_ribs - 1, 1))
    Component_Rear_Upper_Skin = np.zeros((N_ribs - 1, 1))
    for i in range(0, N_ribs - 1):
        my_list = list((Curve_U_Rib_TE[i],
                        Curve_U_Rib_TE[i + 1],
                        Curve_UR_Spar_Cap[i, - 1],
                        Curve_TE[i, 0]))
        my_str = ' '.join(map(str, my_list))
        cmd = "*surfacemode 4\n*createmark lines 1 " + my_str
        f.write(cmd)
        f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
        surfacecounter += 1
        Surface_Rear_Upper_Skin[i, 0] = surfacecounter
        f.write('*createentity comps name="Rear_Upper_Skin_%.0f"\n'
                % (i + 1))
        f.write('*startnotehistorystate {Moved surfaces into component "Rear_Upper_Skin_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f\n'
                % (Surface_Rear_Upper_Skin[i, 0]))
        f.write('*movemark surfaces 1 "Rear_Upper_Skin_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Rear_Upper_Skin_%.0f"}\n'
                % (i + 1))
        componentcounter += 1
        Component_Rear_Upper_Skin[i, 0] = componentcounter
    f.write('*createentity assems name="Rear_Upper_Skin"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=9 components={comps %.0f-%.0f}'
            % (Component_Rear_Upper_Skin[0, 0], Component_Rear_Upper_Skin[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print rear lower skin surfaces
    Surface_Rear_Lower_Skin = np.zeros((N_ribs - 1, 1))
    Component_Rear_Lower_Skin = np.zeros((N_ribs - 1, 1))
    for i in range(0, N_ribs - 1):
        my_list = list((Curve_L_Rib_TE[i],
                        Curve_L_Rib_TE[i + 1],
                        Curve_LR_Spar_Cap[i, - 1],
                        Curve_TE[i, 0]))
        my_str = ' '.join(map(str, my_list))
        cmd = "*surfacemode 4\n*createmark lines 1 " + my_str
        f.write(cmd)
        f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
        surfacecounter += 1
        Surface_Rear_Lower_Skin[i, 0] = surfacecounter
        f.write('*createentity comps name="Rear_Lower_Skin_%.0f"\n'
                % (i + 1))
        f.write('*startnotehistorystate {Moved surfaces into component "Rear_Lower_Skin_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f\n'
                % (Surface_Rear_Lower_Skin[i, 0]))
        f.write('*movemark surfaces 1 "Rear_Lower_Skin_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Rear_Lower_Skin_%.0f"}\n'
                % (i + 1))
        componentcounter += 1
        Component_Rear_Lower_Skin[i, 0] = componentcounter
    f.write('*createentity assems name="Rear_Lower_Skin"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=10 components={comps %.0f-%.0f}'
            % (Component_Rear_Lower_Skin[0, 0], Component_Rear_Lower_Skin[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print upper left spar cap surfaces
    Surface_Spar_Cap_Upper_Left = np.zeros((N_ribs - 1, N_spars))
    Component_Spar_Cap_Upper_Left = np.zeros((N_ribs - 1, 1))
    for i in range(0, N_ribs - 1):
        for j in range(0, N_spars):
            my_list = list((Curve_UL_Spar_Cap[i, j], Curve_U_Spar[i, j],
                            Curve_U_Rib_SC_L[i + 1, j],
                            Curve_U_Rib_SC_L[i, j]))
            my_str = ' '.join(map(str, my_list))
            cmd = "*surfacemode 4\n*createmark lines 1 " + my_str
            f.write(cmd)
            f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
            surfacecounter += 1
            Surface_Spar_Cap_Upper_Left[i, j] = surfacecounter
        f.write('*createentity comps name="Spar_Cap_Upper_Left_%.0f"\n'
                % (i + 1))
        f.write('*startnotehistorystate {Moved surfaces into component "Spar_Cap_Upper_Left_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f-%.0f\n'
                % (Surface_Spar_Cap_Upper_Left[i, 0], Surface_Spar_Cap_Upper_Left[i, -1]))
        f.write('*movemark surfaces 1 "Spar_Cap_Upper_Left_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Spar_Cap_Upper_Left_%.0f"}\n'
                % (i + 1))
        componentcounter += 1
        Component_Spar_Cap_Upper_Left[i, 0] = componentcounter
    f.write('*createentity assems name="Spar_Caps_Upper_Left_"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=11 components={comps %.0f-%.0f}'
            % (Component_Spar_Cap_Upper_Left[0, 0], Component_Spar_Cap_Upper_Left[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print upper right spar cap surfaces
    Surface_Spar_Cap_Upper_Right = np.zeros((N_ribs - 1, N_spars))
    Component_Spar_Cap_Upper_Right = np.zeros((N_ribs - 1, 1))
    for i in range(0, N_ribs - 1):
        for j in range(0, N_spars):
            my_list = list((Curve_UR_Spar_Cap[i, j], Curve_U_Spar[i, j],
                            Curve_U_Rib_SC_R[i + 1, j],
                            Curve_U_Rib_SC_R[i, j]))
            my_str = ' '.join(map(str, my_list))
            cmd = "*surfacemode 4\n*createmark lines 1 " + my_str
            f.write(cmd)
            f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
            surfacecounter += 1
            Surface_Spar_Cap_Upper_Right[i, j] = surfacecounter
        f.write('*createentity comps name="Spar_Cap_Upper_Right_%.0f"\n'
                % (i + 1))
        f.write('*startnotehistorystate {Moved surfaces into component "Spar_Cap_Upper_Right_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f-%.0f\n'
                % (Surface_Spar_Cap_Upper_Right[i, 0], Surface_Spar_Cap_Upper_Right[i, -1]))
        f.write('*movemark surfaces 1 "Spar_Cap_Upper_Right_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Spar_Cap_Upper_Right_%.0f"}\n'
                % (i + 1))
        componentcounter += 1
        Component_Spar_Cap_Upper_Right[i, 0] = componentcounter
    f.write('*createentity assems name="Spar_Caps_Upper_Right_"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=12 components={comps %.0f-%.0f}'
            % (Component_Spar_Cap_Upper_Right[0, 0], Component_Spar_Cap_Upper_Right[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print lower left spar cap surfaces
    Surface_Spar_Cap_Lower_Left = np.zeros((N_ribs - 1, N_spars))
    Component_Spar_Cap_Lower_Left = np.zeros((N_ribs - 1, 1))
    for i in range(0, N_ribs - 1):
        for j in range(0, N_spars):
            my_list = list((Curve_LL_Spar_Cap[i, j], Curve_L_Spar[i, j],
                            Curve_L_Rib_SC_L[i + 1, j],
                            Curve_L_Rib_SC_L[i, j]))
            my_str = ' '.join(map(str, my_list))
            cmd = "*surfacemode 4\n*createmark lines 1 " + my_str
            f.write(cmd)
            f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
            surfacecounter += 1
            Surface_Spar_Cap_Lower_Left[i, j] = surfacecounter
        f.write('*createentity comps name="Spar_Cap_Lower_Left_%.0f"\n'
                % (i + 1))
        f.write('*startnotehistorystate {Moved surfaces into component "Spar_Cap_Lower_Left_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f-%.0f\n'
                % (Surface_Spar_Cap_Lower_Left[i, 0], Surface_Spar_Cap_Lower_Left[i, -1]))
        f.write('*movemark surfaces 1 "Spar_Cap_Lower_Left_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Spar_Cap_Lower_Left_%.0f"}\n'
                % (i + 1))
        componentcounter += 1
        Component_Spar_Cap_Lower_Left[i, 0] = componentcounter
    f.write('*createentity assems name="Spar_Caps_Lower_Left_"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=13 components={comps %.0f-%.0f}'
            % (Component_Spar_Cap_Lower_Left[0, 0], Component_Spar_Cap_Lower_Left[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')

    # Print lower right spar cap surfaces
    Surface_Spar_Cap_Lower_Right = np.zeros((N_ribs - 1, N_spars))
    Component_Spar_Cap_Lower_Right = np.zeros((N_ribs - 1, 1))
    for i in range(0, N_ribs - 1):
        for j in range(0, N_spars):
            my_list = list((Curve_LR_Spar_Cap[i, j], Curve_L_Spar[i, j],
                            Curve_L_Rib_SC_R[i + 1, j],
                            Curve_L_Rib_SC_R[i, j]))
            my_str = ' '.join(map(str, my_list))
            cmd = "*surfacemode 4\n*createmark lines 1 " + my_str
            f.write(cmd)
            f.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
            surfacecounter += 1
            Surface_Spar_Cap_Lower_Right[i, j] = surfacecounter
        f.write('*createentity comps name="Spar_Cap_Lower_Right_%.0f"\n'
                % (i + 1))
        f.write('*startnotehistorystate {Moved surfaces into component "Spar_Cap_Lower_Right_%.0f"}\n' % (i + 1))
        f.write('*createmark surfaces 1 %.0f-%.0f\n'
                % (Surface_Spar_Cap_Lower_Right[i, 0], Surface_Spar_Cap_Lower_Right[i, -1]))
        f.write('*movemark surfaces 1 "Spar_Cap_Lower_Right_%.0f"\n'
                % (i + 1))
        f.write('*endnotehistorystate {Moved surfaces into component "Spar_Cap_Lower_Right_%.0f"}\n'
                % (i + 1))
        componentcounter += 1
        Component_Spar_Cap_Lower_Right[i, 0] = componentcounter
    f.write('*createentity assems name="Spar_Caps_Lower_Right_"\n')
    f.write('*startnotehistorystate {Modified Components of assembly}\n')
    f.write('*setvalue assems id=14 components={comps %.0f-%.0f}'
            % (Component_Spar_Cap_Lower_Right[0, 0], Component_Spar_Cap_Lower_Right[-1, 0]))
    f.write('\n*endnotehistorystate {Modified Components of assembly}\n')


    # Clear all nodes
    f.write("*nodecleartempmark\n")
    # Clean-up the geometry
    my_list = list(range(1, surfacecounter + 1))
    my_str = ' '.join(map(str, my_list))
    cmd = "*createmark surfaces 1 " + my_str
    f.write(cmd)
    f.write('\n*selfstitchcombine 1 146 0.01 0.01\n')
    # f.write('\n*multi_surfs_lines_merge 1 0 0\n*normalsoff\n')
    # Save the file and close
    f.write("*writefile \"C:/Users/efilippo/Documents/"
            "ASD_Lab_Parametric_Design_of_Wing/HM_Files/wing.hm\" 1\n")
    # f.write("*writefile \"C:/Users/Vagelis/Documents/UC3M_Internship/Python/"
    #         "ASD_Lab_Parametric_Design_of_Wing/HM_Files/wing.hm\" 1\n")
    f.write("return; # Stop script and return to application\n*quit 1;\n")
f.close()


"""
################## Running the Command file: ##################
"""

# Location of .tcl script and run
TCLScript = "/ASD_Lab_Parametric_Design_of_Wing/Wing_Geometry_Generation.tcl"
# run_argument(TCLScript)

# End time counter
toc = time.perf_counter()
# Print time
print(f"Script run in {toc - tic:0.3f} seconds")
