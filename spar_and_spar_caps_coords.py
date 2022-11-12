"""A script that contains the class that calculates the spars coordinates."""

import numpy as np
import matplotlib.pyplot as plt
from intersect import intersection


class SparsAndCapsCoords:
    """A class for the spars and spar caps coordinates calculation."""

    def __init__(self, Parameters, wing, N_spars, Spars_position, SC_width,
                 SemiSpan):
        Rib_Sections_ID = Parameters.Rib_Sections_ID
        N_ribs = Parameters.N_ribs
        Origin = Parameters.Origin
        # FSL = Parameters.FSL
        """
        ### Spar and spar caps coordinates: ###
        """

        # Define the index of fuselage rib and initialize the Spars Nodes array
        Fuselage_rib = Rib_Sections_ID[0] - 1
        Spars_nodes_X = np.zeros((N_spars, N_ribs))
        Spars_nodes_Y = np.zeros((N_spars, N_ribs))
        Spars_nodes_X_incl = np.zeros((N_spars, N_ribs))
        Spars_nodes_Y_incl = np.zeros((N_spars, N_ribs))

        # Translate their coordinates. No rotation in the y direction!
        for i in range(0, N_spars):
            for j in range(0, N_ribs):
                Spars_nodes_Y[:, j] = Origin[j, 2]
                if j > Fuselage_rib - 1:
                    Spars_nodes_X[i, j] = Spars_position[i] * \
                                          wing.chords[0, j] + Origin[j, 0]
                else:
                    # If the rib is in the fuselage section
                    # keep Fuselage_rib coords
                    Spars_nodes_X[i, j] = Spars_position[i] * \
                                          wing.chords[0, Fuselage_rib] +\
                                          Origin[Fuselage_rib, 0]

        Spar_Caps_XL = np.zeros((N_spars, N_ribs))
        Spar_Caps_XR = np.zeros((N_spars, N_ribs))
        Spar_Caps_XL_incl = np.zeros((N_spars, N_ribs))
        Spar_Caps_XR_incl = np.zeros((N_spars, N_ribs))
        Spar_Caps_YL_incl = np.zeros((N_spars, N_ribs))
        Spar_Caps_YR_incl = np.zeros((N_spars, N_ribs))

        SC_XL_Width = np.interp(Origin[:, 2], [Origin[0, 2], Origin[-1, 2]],
                                SC_width[:, 0])
        SC_XR_Width = np.interp(Origin[:, 2], [Origin[0, 2], Origin[-1, 2]],
                                SC_width[:, 1])

        for i in range(0, N_spars):
            Spar_Caps_XL[i, :] = Spars_nodes_X[i, :] - SC_XL_Width[:]
            Spar_Caps_XR[i, :] = Spars_nodes_X[i, :] + SC_XR_Width[:]

        Spar_Caps_YL = Spars_nodes_Y
        Spar_Caps_YR = Spars_nodes_Y

        # This code section modifies the spars after
        # fuselage in order to be straight
        # for i in range(0, N_spars):
        #     for j in range(0, N_ribs):
        #         Spars_nodes_X[i, j] = np.interp(Spars_nodes_Y[i, j],
        #                                         [FSL, SemiSpan],
        #                                         [Spars_nodes_X[i,
        #                                          Fuselage_rib],
        #                                          Spars_nodes_X[i, -1]])

        for i in range(0, N_spars):
            for j in range(0, N_ribs):
                x_int, y_int =\
                    intersection(
                        Spars_nodes_X[i, :], Spars_nodes_Y[i, :],
                        wing.Rib_line_x[j, :],
                        wing.Rib_line_y[j, :])
                x_int_sc_l, y_int_sc_l =\
                    intersection(
                        Spar_Caps_XL[i, :], Spar_Caps_YL[i, :],
                        wing.Rib_line_x[j, :],
                        wing.Rib_line_y[j, :])
                x_int_sc_r, y_int_sc_r =\
                    intersection(
                        Spar_Caps_XR[i, :], Spar_Caps_YR[i, :],
                        wing.Rib_line_x[j, :],
                        wing.Rib_line_y[j, :])
                if len(x_int) == 0:
                    pass
                else:
                    Spars_nodes_X_incl[i, j] = x_int[0]
                    Spars_nodes_Y_incl[i, j] = y_int[0]
                    Spar_Caps_XL_incl[i, j] = x_int_sc_l[0]
                    Spar_Caps_YL_incl[i, j] = y_int_sc_l[0]
                    Spar_Caps_XR_incl[i, j] = x_int_sc_r[0]
                    Spar_Caps_YR_incl[i, j] = y_int_sc_r[0]

        Spars_nodes_X = Spars_nodes_X_incl
        Spars_nodes_Y = Spars_nodes_Y_incl

        self.Spars_nodes_X = Spars_nodes_X
        self.Spars_nodes_Y = Spars_nodes_Y
        self.Spar_Caps_XL = Spar_Caps_XL_incl
        self.Spar_Caps_YL = Spar_Caps_YL_incl
        self.Spar_Caps_XR = Spar_Caps_XR_incl
        self.Spar_Caps_YR = Spar_Caps_YR_incl
