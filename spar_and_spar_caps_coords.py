"""A script that contains the class that calculates the spars coordinates."""

import numpy as np
from intersect import intersection


# Too much repeated code. Needs improvement
class SparsAndCapsCoords:
    """A class for the spars and spar caps coordinates calculation."""

    def __init__(self, derived_geometry, wing, parameters):

        spars_position = parameters.spars_position()
        sc_width = parameters.sc_widths()
        stringers_position = parameters.stringers_pos()
        n_stringers_total = len(stringers_position)
        # FSL = Parameters.FSL
        """
        ### Spar and spar caps coordinates: ###
        """

        # Define the index of fuselage rib
        fuselage_rib = derived_geometry.Rib_Sections_ID[0] - 1
        # Initialize the Spars Nodes array
        spars_nodes_x = np.zeros((parameters.n_spars, derived_geometry.N_ribs))
        spars_nodes_y = np.zeros((parameters.n_spars, derived_geometry.N_ribs))
        spars_nodes_x_incl = np.zeros((parameters.n_spars,
                                       derived_geometry.N_ribs))
        spars_nodes_y_incl = np.zeros((parameters.n_spars,
                                       derived_geometry.N_ribs))
        # Initialize the stringers nodes array
        stringers_nodes_x = np.zeros((n_stringers_total,
                                      derived_geometry.N_ribs))
        stringers_nodes_y = np.zeros((n_stringers_total,
                                      derived_geometry.N_ribs))
        stringers_nodes_x_incl = np.zeros((n_stringers_total,
                                           derived_geometry.N_ribs))
        stringers_nodes_y_incl = np.zeros((n_stringers_total,
                                           derived_geometry.N_ribs))
        # Translate the spars
        translation(parameters.n_spars, derived_geometry, wing, fuselage_rib,
                    spars_position, spars_nodes_x, spars_nodes_y)
        # Translate the stringers
        translation(n_stringers_total, derived_geometry, wing, fuselage_rib,
                    stringers_position, stringers_nodes_x, stringers_nodes_y)
        # Initialize the spar caps arrays
        spar_caps_xl = np.zeros((parameters.n_spars, derived_geometry.N_ribs))
        spar_caps_xr = np.zeros((parameters.n_spars, derived_geometry.N_ribs))
        spar_caps_xl_incl = np.zeros((parameters.n_spars,
                                      derived_geometry.N_ribs))
        spar_caps_xr_incl = np.zeros((parameters.n_spars,
                                      derived_geometry.N_ribs))
        spar_caps_yl_incl = np.zeros((parameters.n_spars,
                                      derived_geometry.N_ribs))
        spar_caps_yr_incl = np.zeros((parameters.n_spars,
                                      derived_geometry.N_ribs))
        # Linear interpolation for the spar caps' width
        sc_xl_width = np.interp(derived_geometry.Origin[:, 2],
                                [derived_geometry.Origin[0, 2],
                                 derived_geometry.Origin[-1, 2]],
                                sc_width[:, 0])
        sc_xr_width = np.interp(derived_geometry.Origin[:, 2],
                                [derived_geometry.Origin[0, 2],
                                 derived_geometry.Origin[-1, 2]],
                                sc_width[:, 1])
        # Now find the true position of spar caps
        for i in range(0, parameters.n_spars):
            spar_caps_xl[i, :] = spars_nodes_x[i, :] - sc_xl_width[:]
            spar_caps_xr[i, :] = spars_nodes_x[i, :] + sc_xr_width[:]
        # Spar caps Y is the same with spars'
        spar_caps_yl = spars_nodes_y
        spar_caps_yr = spars_nodes_y

        # Calculate the intersection with the ribs that define their coordinates
        for i in range(0, parameters.n_spars):
            for j in range(0, derived_geometry.N_ribs):
                x_int, y_int =\
                    intersection(
                        spars_nodes_x[i, :], spars_nodes_y[i, :],
                        wing.rib_line_x[j, :],
                        wing.rib_line_y[j, :])
                x_int_sc_l, y_int_sc_l =\
                    intersection(
                        spar_caps_xl[i, :], spar_caps_yl[i, :],
                        wing.rib_line_x[j, :],
                        wing.rib_line_y[j, :])
                x_int_sc_r, y_int_sc_r =\
                    intersection(
                        spar_caps_xr[i, :], spar_caps_yr[i, :],
                        wing.rib_line_x[j, :],
                        wing.rib_line_y[j, :])
                if len(x_int) == 0:
                    pass
                else:
                    spars_nodes_x_incl[i, j] = x_int[0]
                    spars_nodes_y_incl[i, j] = y_int[0]
                    spar_caps_xl_incl[i, j] = x_int_sc_l[0]
                    spar_caps_yl_incl[i, j] = y_int_sc_l[0]
                    spar_caps_xr_incl[i, j] = x_int_sc_r[0]
                    spar_caps_yr_incl[i, j] = y_int_sc_r[0]

        for i in range(0, n_stringers_total):
            for j in range(0, derived_geometry.N_ribs):
                x_int_str, y_int_str =\
                    intersection(
                        stringers_nodes_x[i, :], stringers_nodes_y[i, :],
                        wing.rib_line_x[j, :],
                        wing.rib_line_y[j, :])
                if len(x_int) == 0:
                    pass
                else:
                    stringers_nodes_x_incl[i, j] = x_int_str[0]
                    stringers_nodes_y_incl[i, j] = y_int_str[0]

        self.Spars_nodes_X = spars_nodes_x_incl
        self.Spars_nodes_Y = spars_nodes_y_incl
        self.Spar_Caps_XL = spar_caps_xl_incl
        self.Spar_Caps_YL = spar_caps_yl_incl
        self.Spar_Caps_XR = spar_caps_xr_incl
        self.Spar_Caps_YR = spar_caps_yr_incl
        self.stringers_nodes_x = stringers_nodes_x_incl
        self.stringers_nodes_y = stringers_nodes_y_incl


def translation(n_nodes, derived_geometry, wing, fuselage_rib,
                position, nodes_x, nodes_y):
    # Translate their coordinates. No rotation in the y direction!
    for j in range(0, derived_geometry.N_ribs):
        nodes_y[:, j] = derived_geometry.Origin[j, 2]
        for i in range(0, n_nodes):
            if j > fuselage_rib - 1:
                nodes_x[i, j] = position[i] * \
                                      wing.chords[0, j] +\
                                      derived_geometry.Origin[j, 0]
            else:
                # If the rib is in the fuselage section
                # keep fuselage_rib coordinates
                nodes_x[i, j] = position[i] * \
                                      wing.chords[0, fuselage_rib] +\
                                      derived_geometry.Origin[fuselage_rib,
                                                              0]
    return nodes_x, nodes_y
