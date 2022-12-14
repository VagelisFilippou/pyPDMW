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
        spars_nodes_x = np.zeros((3, parameters.n_spars, derived_geometry.N_ribs))
        spars_nodes_y = np.zeros((3, parameters.n_spars, derived_geometry.N_ribs))
        spars_nodes_x_incl = np.zeros((3, parameters.n_spars,
                                       derived_geometry.N_ribs))
        spars_nodes_y_incl = np.zeros((3, parameters.n_spars,
                                       derived_geometry.N_ribs))
        # Initialize the stringers nodes array
        stringers_nodes_x = np.zeros((3, n_stringers_total,
                                      derived_geometry.N_ribs))
        stringers_nodes_y = np.zeros((3, n_stringers_total,
                                      derived_geometry.N_ribs))
        stringers_nodes_x_incl = np.zeros((3, n_stringers_total,
                                           derived_geometry.N_ribs))
        stringers_nodes_y_incl = np.zeros((3, n_stringers_total,
                                           derived_geometry.N_ribs))
        stringers_nodes_x_par = np.zeros((3, n_stringers_total,
                                          derived_geometry.N_ribs))
        stringers_nodes_y_par = np.zeros((3, n_stringers_total,
                                          derived_geometry.N_ribs))
        stringers_nodes_x_incl_par = np.zeros((3, n_stringers_total,
                                               derived_geometry.N_ribs))
        stringers_nodes_y_incl_par = np.zeros((3, n_stringers_total,
                                               derived_geometry.N_ribs))
        self.stringers_nodes_x_inters = {}
        self.stringers_nodes_y_inters = {}
        # Translate the spars
        translation(parameters.n_spars, derived_geometry, wing, fuselage_rib,
                    spars_position, spars_nodes_x, spars_nodes_y)
        # Translate the stringers
        translation(n_stringers_total, derived_geometry, wing, fuselage_rib,
                    stringers_position, stringers_nodes_x, stringers_nodes_y)
        stringers_translation(n_stringers_total, derived_geometry, wing,
                              fuselage_rib, stringers_position, spars_nodes_x,
                              stringers_nodes_x_par, stringers_nodes_y_par)
        # Initialize the spar caps arrays
        spar_caps_xl = np.zeros((3, parameters.n_spars, derived_geometry.N_ribs))
        spar_caps_xr = np.zeros((3, parameters.n_spars, derived_geometry.N_ribs))
        spar_caps_xl_incl = np.zeros((3, parameters.n_spars,
                                      derived_geometry.N_ribs))
        spar_caps_xr_incl = np.zeros((3, parameters.n_spars,
                                      derived_geometry.N_ribs))
        spar_caps_yl_incl = np.zeros((3, parameters.n_spars,
                                      derived_geometry.N_ribs))
        spar_caps_yr_incl = np.zeros((3, parameters.n_spars,
                                      derived_geometry.N_ribs))
        # Linear interpolation for the spar caps' width
        sc_xl_width = np.zeros((3, derived_geometry.N_ribs))
        sc_xr_width = np.zeros((3, derived_geometry.N_ribs))

        for k in range(0, 3):
            sc_xl_width[k, :] =\
                np.interp(derived_geometry.Origin[k, :, 2],
                          [derived_geometry.Origin[k, 0, 2],
                           derived_geometry.Origin[k, -1, 2]],
                          sc_width[:, 0])
            sc_xr_width[k, :] =\
                np.interp(derived_geometry.Origin[k, :, 2],
                          [derived_geometry.Origin[k, 0, 2],
                           derived_geometry.Origin[k, -1, 2]],
                          sc_width[:, 1])

        # Now find the true position of spar caps
        for i in range(0, parameters.n_spars):
            spar_caps_xl[:, i, :] = spars_nodes_x[:, i, :] - sc_xl_width[:, :]
            spar_caps_xr[:, i, :] = spars_nodes_x[:, i, :] + sc_xr_width[:, :]
        # Spar caps Y is the same with spars'
        spar_caps_yl = spars_nodes_y
        spar_caps_yr = spars_nodes_y


        # Calculate the intersection with the ribs that define their coordinates
        for i in range(0, parameters.n_spars):
            for j in range(0, derived_geometry.N_ribs):
                for k in range(0, 3):
                    x_int, y_int =\
                        intersection(
                            spars_nodes_x[k, i, :], spars_nodes_y[k, i, :],
                            wing.rib_line_x[k, j, :],
                            wing.rib_line_y[k, j, :])
                    x_int_sc_l, y_int_sc_l =\
                        intersection(
                            spar_caps_xl[k, i, :], spar_caps_yl[k, i, :],
                            wing.rib_line_x[k, j, :],
                            wing.rib_line_y[k, j, :])
                    x_int_sc_r, y_int_sc_r =\
                        intersection(
                            spar_caps_xr[k, i, :], spar_caps_yr[k, i, :],
                            wing.rib_line_x[k, j, :],
                            wing.rib_line_y[k, j, :])
                    if len(x_int) == 0:
                        pass
                    else:
                        spars_nodes_x_incl[k, i, j] = x_int[0]
                        spars_nodes_y_incl[k, i, j] = y_int[0]
                        spar_caps_xl_incl[k, i, j] = x_int_sc_l[0]
                        spar_caps_yl_incl[k, i, j] = y_int_sc_l[0]
                        spar_caps_xr_incl[k, i, j] = x_int_sc_r[0]
                        spar_caps_yr_incl[k, i, j] = y_int_sc_r[0]
        keys = []
        for i in range(0, n_stringers_total):
            sign = 0
            for j in range(0, derived_geometry.N_ribs):
                for k in range(0, 3):
                    x_int_str, y_int_str =\
                        intersection(
                            stringers_nodes_x[k, i, :],
                            stringers_nodes_y[k, i, :],
                            wing.rib_line_x[k, j, :],
                            wing.rib_line_y[k, j, :])
                    if len(x_int_str) == 0:
                        pass
                    else:
                        stringers_nodes_x_incl[k, i, j] = x_int_str[0]
                        stringers_nodes_y_incl[k, i, j] = y_int_str[0]

                    x_int_str_par, y_int_str_par =\
                        intersection(
                            stringers_nodes_x_par[k, i, :],
                            stringers_nodes_y_par[k, i, :],
                            wing.rib_line_x[k, j, :],
                            wing.rib_line_y[k, j, :])
                    if len(x_int_str_par) == 0:
                        pass
                    else:
                        stringers_nodes_x_incl_par[k, i, j] = x_int_str_par[0]
                        stringers_nodes_y_incl_par[k, i, j] = y_int_str_par[0]
                if stringers_nodes_x_incl_par[0, i, j] <\
                        spar_caps_xr_incl[0, 0, j] + parameters.stringers_tolerance and sign == 0:
                    sign = 1
                    # Caution!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    # This is wrong! shoud be equal to the intersection with right spar cap
                    self.stringers_nodes_x_inters[i, j] = stringers_nodes_x_incl_par[0, i, j]
                    self.stringers_nodes_y_inters[i, j] = stringers_nodes_y_incl_par[0, i, j]

                if stringers_nodes_x_incl_par[0, i, j] <\
                        spar_caps_xr_incl[0, 0, j] + parameters.stringers_tolerance:
                    stringers_nodes_x_incl_par[:, i, j] = np.nan
                    stringers_nodes_y_incl_par[:, i, j] = np.nan

        self.Spars_nodes_X = spars_nodes_x_incl
        self.Spars_nodes_Y = spars_nodes_y_incl
        self.Spar_Caps_XL = spar_caps_xl_incl
        self.Spar_Caps_YL = spar_caps_yl_incl
        self.Spar_Caps_XR = spar_caps_xr_incl
        self.Spar_Caps_YR = spar_caps_yr_incl
        self.stringers_nodes_x = stringers_nodes_x_incl
        self.stringers_nodes_y = stringers_nodes_y_incl
        self.stringers_nodes_x_par = stringers_nodes_x_incl_par
        self.stringers_nodes_y_par = stringers_nodes_y_incl_par


def translation(n_nodes, derived_geometry, wing, fuselage_rib,
                position, nodes_x, nodes_y):
    # Translate their coordinates. No rotation in the y direction!
    for j in range(0, derived_geometry.N_ribs):
        for k in range(0, 3):
            nodes_y[k, :, j] = derived_geometry.Origin[k, j, 2]
            for i in range(0, n_nodes):
                if j > fuselage_rib - 1:
                    nodes_x[k, i, j] =\
                        position[i] * wing.chords[k, j] +\
                        derived_geometry.Origin[k, j, 0]
                else:
                    # If the rib is in the fuselage section
                    # keep fuselage_rib coordinates
                    nodes_x[k, i, j] =\
                        position[i] * wing.chords[k, fuselage_rib] +\
                        derived_geometry.Origin[k, fuselage_rib, 0]
    # This code section modifies the spars after fuselage in order to be straight
    # for j in range(0, derived_geometry.N_ribs):
    #     for k in range(0, 3):
    #         for i in range(0, n_nodes):
    #             nodes_x[k, i, j] =\
    #                 np.interp(nodes_y[k, i, j],
    #                           [nodes_y[0, 0, derived_geometry.Rib_Sections_ID[0] - 1], nodes_y[0, 0, -1]],
    #                           [nodes_x[k, i, derived_geometry.Rib_Sections_ID[0] - 1],
    #                            nodes_x[k, i, -1]])

    nodes_x[2, :, 0: fuselage_rib + 1] = nodes_x[0, :, 0: fuselage_rib + 1]
    nodes_x[1, :, 0: fuselage_rib] = nodes_x[0, :, 0: fuselage_rib]

    return nodes_x, nodes_y


def stringers_translation(n_nodes, derived_geometry, wing, fuselage_rib,
                          position, spars_nodes_x, nodes_x, nodes_y):
    # Translate their coordinates. No rotation in the y direction!
    distance = np.zeros((3, n_nodes))
    for j in range(0, derived_geometry.N_ribs):
        for k in range(0, 3):
            nodes_y[k, :, j] = derived_geometry.Origin[k, j, 2]
            for i in range(0, n_nodes):
                # If the rib is in the fuselage section
                # keep fuselage_rib coordinates
                if j == 0:
                    nodes_x[k, i, j] = position[i] * \
                        wing.chords[0, fuselage_rib] +\
                        derived_geometry.Origin[0, fuselage_rib, j]
                    distance[k, i] = spars_nodes_x[0, -1, 0] - nodes_x[0, i, j]
                else:
                    nodes_x[k, i, j] = spars_nodes_x[k, -1, j] - distance[k, i]
    nodes_x[2, :, 0: fuselage_rib + 1] = nodes_x[0, :, 0: fuselage_rib + 1]
    nodes_x[1, :, 0: fuselage_rib] = nodes_x[0, :, 0: fuselage_rib]
    return nodes_x, nodes_y
