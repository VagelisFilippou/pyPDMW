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
import curve_classes
import surface_classes
from run_arg import run_argument
from delete_files import delete_files

# Set counter
tic = time.perf_counter()

"""
################## Delete Previous Files: ##################
"""

delete_files()

# ################# User Defined Values: ##################

# Define Wing's Parameters:
SEMI_SPAN = 29.38
YB_PERCENT = 0.37  # Yehudi Break in Percent of Semispan

# Define Wing's Structural Parameters
N_SPARS = 3  # Number of spars
N_RIBS_CENTRAL = 5  # Number of equally spaced ribs
N_RIBS_YEHUDI = 5  # Number of equally spaced ribs
N_RIBS_SEMISPAN = 5  # Number of equally spaced ribs
N_STRINGERS = 5  # Number of stringers per section
# List with the location of each spar
SPARS_POSITION = np.linspace(0.1, 0.7, num=N_SPARS, endpoint=True)

# Specify the length of the fuselage wingbox
FSLG_SECTION_PERCENT = 0.1

# Define two widths per spar at the root and at the tip: UL, UR, LL, LR
SC_width = np.array([[0.3, 0.3], [0.1, 0.1]]) * 0.6

# ################# Derive the Geometry and its' Parameters: ##################


Parameters = DerivedGeometry(SEMI_SPAN,
                             YB_PERCENT,
                             N_RIBS_CENTRAL,
                             N_RIBS_YEHUDI,
                             N_RIBS_SEMISPAN,
                             FSLG_SECTION_PERCENT,
                             )

wing = RibsInclined(Parameters.Y_list,
                    SPARS_POSITION,
                    Parameters.Origin[:, 0],
                    Parameters.Rib_Sections_ID)


X, Y, Z = wing.X, wing.Y, wing.Z

N_RIBS = Parameters.N_ribs
Origin = Parameters.Origin
Rib_Sections_ID = Parameters.Rib_Sections_ID
NUMBER_OF_NODES = Parameters.n

# ## Spar and spar caps coordinates: ###

Spars_And_Spar_Caps = SparsAndCapsCoords(Parameters,
                                         wing,
                                         N_SPARS,
                                         SPARS_POSITION,
                                         SC_width,
                                         SEMI_SPAN
                                         )

# ## Put the spars' coordinates in the XYZ arrays and store their index: ###

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

###
# Insert LE, TE, Spars and Spar Caps to coords arrays for curve construction:
###

Con_Nodes = ConnectionNodes(Parameters, XYZ, N_SPARS)
Curve_IDs_Upper = Con_Nodes.Curve_IDs_Upper
Curve_IDs_Lower = Con_Nodes.Curve_IDs_Lower
LE_IDs = Con_Nodes.LE_IDs
TE_IDs_u = Con_Nodes.TE_IDs_u
TE_IDs_l = Con_Nodes.TE_IDs_l

# ################# Writing in Command file: ##################

# Initialization of counters
CURVE_COUNTER = 0
SURFACE_COUNTER = 0
COMPONENT_COUNTER = 1  # =1 because of the initial component
ASSEMBLY_COUNTER = 1
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
            #         % (X[i, j], Y[i, j], Z[i, j]))
            # Nodes
            f.write('*createnode %.7f %.7f %.7f 0 0 0\n'
                    % (X[i, j], Y[i, j], Z[i, j]))
f.close()


Curve_Upper_Rib = curve_classes.UpperRibCurve(N_RIBS, N_SPARS,
                                              Curve_IDs_Upper,
                                              CURVE_COUNTER)
Curve_Lower_Rib = curve_classes.LowerRibCurve(N_RIBS, N_SPARS,
                                              Curve_IDs_Lower,
                                              Curve_Upper_Rib.curvecounter)

Curve_Leading_Edge = curve_classes.LeadingTrailingEdgeCurves(N_RIBS,
                                                             1,
                                                             LE_IDs,
                                                             Curve_Lower_Rib
                                                             .curvecounter)

Curve_Trailing_Edge = curve_classes.LeadingTrailingEdgeCurves(N_RIBS,
                                                              1,
                                                              TE_IDs_u,
                                                              Curve_Leading_Edge
                                                              .curvecounter)

Curve_Spar_In_Ribs = curve_classes.MultipleCurves(N_RIBS, N_SPARS,
                                                  Spar_ID_Upper,
                                                  Spar_ID_Lower,
                                                  Curve_Trailing_Edge.
                                                  curvecounter)

Curve_Left_Spar_Cap_In_Ribs =\
    curve_classes.MultipleCurves(N_RIBS, N_SPARS,
                                 Spar_Cap_ID_Lower_Left,
                                 Spar_Cap_ID_Upper_Left,
                                 Curve_Spar_In_Ribs.
                                 curvecounter)

Curve_Right_Spar_Cap_In_Ribs =\
    curve_classes.MultipleCurves(N_RIBS, N_SPARS,
                                 Spar_Cap_ID_Lower_Right,
                                 Spar_Cap_ID_Upper_Right,
                                 Curve_Left_Spar_Cap_In_Ribs.
                                 curvecounter)

Curve_Upper_Spar =\
    curve_classes.SparAndSparCapCurves(N_RIBS - 1,
                                       N_SPARS,
                                       Spar_ID_Upper,
                                       Spar_ID_Upper,
                                       Curve_Right_Spar_Cap_In_Ribs.
                                       curvecounter)

Curve_Lower_Spar =\
    curve_classes.SparAndSparCapCurves(N_RIBS - 1,
                                       N_SPARS,
                                       Spar_ID_Lower,
                                       Spar_ID_Lower,
                                       Curve_Upper_Spar.
                                       curvecounter)

Curve_Upper_Left_Spar_Cap =\
    curve_classes.SparAndSparCapCurves(N_RIBS - 1,
                                       N_SPARS,
                                       Spar_Cap_ID_Upper_Left,
                                       Spar_Cap_ID_Upper_Left,
                                       Curve_Lower_Spar.
                                       curvecounter)

Curve_Lower_Left_Spar_Cap =\
    curve_classes.SparAndSparCapCurves(N_RIBS - 1,
                                       N_SPARS,
                                       Spar_Cap_ID_Lower_Left,
                                       Spar_Cap_ID_Lower_Left,
                                       Curve_Upper_Left_Spar_Cap.
                                       curvecounter)

Curve_Upper_Right_Spar_Cap =\
    curve_classes.SparAndSparCapCurves(N_RIBS - 1,
                                       N_SPARS,
                                       Spar_Cap_ID_Upper_Right,
                                       Spar_Cap_ID_Upper_Right,
                                       Curve_Lower_Left_Spar_Cap.
                                       curvecounter)

Curve_Lower_Right_Spar_Cap =\
    curve_classes.SparAndSparCapCurves(N_RIBS - 1,
                                       N_SPARS,
                                       Spar_Cap_ID_Lower_Right,
                                       Spar_Cap_ID_Lower_Right,
                                       Curve_Upper_Right_Spar_Cap.
                                       curvecounter)


with open('Wing_Geometry_Generation.tcl', 'a+') as f:
    # Clear all nodes
    f.write("*nodecleartempmark\n")
    # Save the file and close
    # f.write("*writefile \"C:/Users/efilippo/Documents/"
    #         "ASD_Lab_Parametric_Design_of_Wing_OOP/HM_Files/wing.hm\" 1\n")
    f.write("*writefile \"C:/Users/Vagelis/Documents/UC3M_Internship/Python/"
            "ASD_Lab_Parametric_Design_of_Wing_OOP/HM_Files/wing.hm\" 1\n")
    f.write("return; # Stop script and return to application\n*quit 1;\n")
f.close()

# ################# Running the Command file: ##################


# Location of .tcl script and run
TCL_SCRIPT_PATH = "/ASD_Lab_Parametric_Design_of_Wing_OOP/"\
                    "Wing_Geometry_Generation.tcl"
run_argument(TCL_SCRIPT_PATH)

# End time counter
toc = time.perf_counter()
# Print time
print(f"Script run in {toc - tic:0.3f} seconds")
