"""A script that contains the SparsAndCapsCoords class."""

import numpy as np


class SparsCapsIDs:
    """A class that inserts the spar and caps coords into the XYZ arrays."""

    def __init__(self, wing,  derived_geometry, spars_and_spar_caps,
                 parameters):

        self.coord_x = wing.X
        self.coord_y = wing.Y
        self.coord_z = wing.Z
        self.n_nodes = derived_geometry.n
        self.n_ribs = derived_geometry.N_ribs

        spars_nodes_x = spars_and_spar_caps.Spars_nodes_X
        spar_caps_xl = spars_and_spar_caps.Spar_Caps_XL
        spar_caps_xr = spars_and_spar_caps.Spar_Caps_XR
        stringers_x = spars_and_spar_caps.stringers_nodes_x
        stringers_x_par = spars_and_spar_caps.stringers_nodes_x_par

        stringers_position = parameters.stringers_pos()
        n_stringers_total = len(stringers_position)
        n_ribs = derived_geometry.N_ribs
        n_spars = parameters.n_spars

        # Initialize ID arrays that spar nodes will be stored
        self.Spar_ID_Lower = np.zeros((3, n_ribs, n_spars))
        self.Spar_Cap_ID_Lower_Left = np.zeros((3, n_ribs, n_spars))
        self.Spar_Cap_ID_Lower_Right = np.zeros((3, n_ribs, n_spars))
        self.stringer_id_lower = np.zeros((3, n_ribs, n_stringers_total))
        self.stringer_par_id_lower = np.zeros((3, n_ribs, n_stringers_total))

        self.Spar_ID_Upper = np.zeros((3, n_ribs, n_spars))
        self.Spar_Cap_ID_Upper_Left = np.zeros((3, n_ribs, n_spars))
        self.Spar_Cap_ID_Upper_Right = np.zeros((3, n_ribs, n_spars))
        self.stringer_id_upper = np.zeros((3, n_ribs, n_stringers_total))
        self.stringer_par_id_upper = np.zeros((3, n_ribs, n_stringers_total))

        for l in range(0, 3):
            for i in range(0, n_ribs):
                for j in range(0, n_spars):
                    
                    # Lower nodes of spars
                    for k in range(self.n_nodes, 2 * self.n_nodes):
                        self.adjust_lower_nodes(l, i, j, k, spars_nodes_x,
                                                self.Spar_ID_Lower)
                        self.adjust_lower_nodes(l, i, j, k, spar_caps_xl,
                                                self.Spar_Cap_ID_Lower_Left)
                        self.adjust_lower_nodes(l, i, j, k, spar_caps_xr,
                                                self.Spar_Cap_ID_Lower_Right)

                    # Upper nodes of spars
                    for k in range(0, self.n_nodes):
                        self.adjust_upper_nodes(l, i, j, k, spars_nodes_x,
                                                self.Spar_ID_Upper)
                        self.adjust_upper_nodes(l, i, j, k, spar_caps_xl,
                                                self.Spar_Cap_ID_Upper_Left)
                        self.adjust_upper_nodes(l, i, j, k, spar_caps_xr,
                                                self.Spar_Cap_ID_Upper_Right)
                for j in range(0, n_stringers_total):
                    for k in range(self.n_nodes, 2 * self.n_nodes):
                        self.adjust_lower_nodes(l, i, j, k, stringers_x,
                                                self.stringer_id_lower)
                    for k in range(0, self.n_nodes):
                        self.adjust_upper_nodes(l, i, j, k, stringers_x,
                                                self.stringer_id_upper)
                    for k in range(self.n_nodes, 2 * self.n_nodes):
                        self.adjust_lower_nodes(l, i, j, k, stringers_x_par,
                                                self.stringer_par_id_lower)
                    for k in range(0, self.n_nodes):
                        self.adjust_upper_nodes(l, i, j, k, stringers_x_par,
                                                self.stringer_par_id_upper)

        self.Spar_ID_Lower = self.Spar_ID_Lower.astype(int)
        self.Spar_Cap_ID_Lower_Left = self.Spar_Cap_ID_Lower_Left.astype(int)
        self.Spar_Cap_ID_Lower_Right = self.Spar_Cap_ID_Lower_Right.astype(int)
        self.stringer_id_lower = self.stringer_id_lower.astype(int)
        self.stringer_par_id_lower = self.stringer_par_id_lower.astype(int)

        self.Spar_ID_Upper = self.Spar_ID_Upper.astype(int)
        self.Spar_Cap_ID_Upper_Left = self.Spar_Cap_ID_Upper_Left.astype(int)
        self.Spar_Cap_ID_Upper_Right = self.Spar_Cap_ID_Upper_Right.astype(int)
        self.stringer_id_upper = self.stringer_id_upper.astype(int)
        self.stringer_par_id_upper = self.stringer_par_id_upper.astype(int)

    def adjust_lower_nodes(self, l, i, j, k, desired, id_s):
        """
        Put the desired upper coordinates in the XYZ & stores their index:
        """
        if k < 2 * self.n_nodes - 1 and \
                self.coord_x[l, i, k - 1] < desired[l, j, i] < self.coord_x[l, i, k + 1]:
            self.coord_x[l, i, k] = desired[l, j, i]
            self.coord_z[l, i, k] = np.interp(self.coord_x[l, i, k],
                                              [self.coord_x[l, i, k - 1],
                                               self.coord_x[l, i, k + 1]],
                                              [self.coord_z[l, i, k - 1],
                                               self.coord_z[l, i, k + 1]])
            self.coord_y[l, i, k] = np.interp(self.coord_x[l, i, k],
                                              [self.coord_x[l, i, k - 1],
                                               self.coord_x[l, i, k + 1]],
                                              [self.coord_y[l, i, k - 1],
                                               self.coord_y[l, i, k + 1]])
            # Store indices
            # (+1) because of the different indexing of python & HM
            id_s[l, i, j] = (i * 2 * self.n_nodes + k + 1) + self.n_ribs * 240 * l

    def adjust_upper_nodes(self, l, i, j, k, desired, id_s):
        """
        Put the desired upper coordinates in the XYZ & stores their index:
        """
        if k < 2 * self.n_nodes - 1 and \
                self.coord_x[l, i, k - 1] > desired[l, j, i] > self.coord_x[l, i, k + 1]:
            self.coord_x[l, i, k] = desired[l, j, i]
            self.coord_z[l, i, k] = np.interp(self.coord_x[l, i, k],
                                              [self.coord_x[l, i, k + 1],
                                               self.coord_x[l, i, k - 1]],
                                              [self.coord_z[l, i, k + 1],
                                               self.coord_z[l, i, k - 1]])
            self.coord_y[l, i, k] = np.interp(self.coord_x[l, i, k],
                                              [self.coord_x[l, i, k + 1],
                                               self.coord_x[l, i, k - 1]],
                                              [self.coord_y[l, i, k + 1],
                                               self.coord_y[l, i, k - 1]])
            # Store indices
            # (+1) because of the different indexing of python & HM
            id_s[l, i, j] = (i * 2 * self.n_nodes + k + 1) + self.n_ribs * 240 * l
