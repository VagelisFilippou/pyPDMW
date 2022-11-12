"""A script that contains the SparsAndCapsCoords class."""

import numpy as np


class SparsCapsIDs:
    """A class that inserts the spar and caps coords into the XYZ arrays."""

    def __init__(self,
                 Spars_And_Spar_Caps,
                 X,
                 Y,
                 Z,
                 N_ribs,
                 N_spars,
                 n):

        self.coord_x = X
        self.coord_y = Y
        self.coord_z = Z
        self.n_nodes = n

        spars_nodes_x = Spars_And_Spar_Caps.Spars_nodes_X
        spar_caps_xl = Spars_And_Spar_Caps.Spar_Caps_XL
        spar_caps_xr = Spars_And_Spar_Caps.Spar_Caps_XR

        # Initialize ID lists that spar nodes will be stored
        self.Spar_ID_Lower = np.zeros((N_ribs, N_spars))
        self.Spar_Cap_ID_Lower_Left = np.zeros((N_ribs, N_spars))
        self.Spar_Cap_ID_Lower_Right = np.zeros((N_ribs, N_spars))
        self.Spar_ID_Upper = np.zeros((N_ribs, N_spars))
        self.Spar_Cap_ID_Upper_Left = np.zeros((N_ribs, N_spars))
        self.Spar_Cap_ID_Upper_Right = np.zeros((N_ribs, N_spars))

        # Lower nodes of spars
        for i in range(0, N_ribs):
            for j in range(0, N_spars):
                for k in range(n, 2 * n):
                    self.adjust_lower_nodes(i, j, k, spars_nodes_x,
                                            self.Spar_ID_Lower)
                    self.adjust_lower_nodes(i, j, k, spar_caps_xl,
                                            self.Spar_Cap_ID_Lower_Left)
                    self.adjust_lower_nodes(i, j, k, spar_caps_xr,
                                            self.Spar_Cap_ID_Lower_Right)

        # Upper nodes of spars
        for i in range(0, N_ribs):
            for j in range(0, N_spars):
                for k in range(0, n):
                    self.adjust_upper_nodes(i, j, k, spars_nodes_x,
                                            self.Spar_ID_Upper)
                    self.adjust_upper_nodes(i, j, k, spar_caps_xl,
                                            self.Spar_Cap_ID_Upper_Left)
                    self.adjust_upper_nodes(i, j, k, spar_caps_xr,
                                            self.Spar_Cap_ID_Upper_Right)

    def adjust_lower_nodes(self, i, j, k, desired, id_s):
        """
        Put the desired upper coordinates in the XYZ & stores their index:
        """
        if k < 2 * self.n_nodes - 1 and \
                self.coord_x[i, k - 1] < desired[j, i] < self.coord_x[i, k + 1]:
            self.coord_x[i, k] = desired[j, i]
            self.coord_z[i, k] = np.interp(self.coord_x[i, k],
                                           [self.coord_x[i, k - 1],
                                            self.coord_x[i, k + 1]],
                                           [self.coord_z[i, k - 1],
                                            self.coord_z[i, k + 1]])
            self.coord_y[i, k] = np.interp(self.coord_x[i, k],
                                           [self.coord_x[i, k - 1],
                                            self.coord_x[i, k + 1]],
                                           [self.coord_y[i, k - 1],
                                            self.coord_y[i, k + 1]])
            # Store indices
            # (+1) because of the different indexing of python & HM
            id_s[i, j] = i * 2 * self.n_nodes + k + 1

    def adjust_upper_nodes(self, i, j, k, desired, id_s):
        """
        Put the desired upper coordinates in the XYZ & stores their index:
        """
        if k < 2 * self.n_nodes - 1 and \
                self.coord_x[i, k - 1] > desired[j, i] > self.coord_x[i, k + 1]:
            self.coord_x[i, k] = desired[j, i]
            self.coord_z[i, k] = np.interp(self.coord_x[i, k],
                                           [self.coord_x[i, k + 1],
                                            self.coord_x[i, k - 1]],
                                           [self.coord_z[i, k + 1],
                                            self.coord_z[i, k - 1]])
            self.coord_y[i, k] = np.interp(self.coord_x[i, k],
                                           [self.coord_x[i, k + 1],
                                            self.coord_x[i, k - 1]],
                                           [self.coord_y[i, k + 1],
                                            self.coord_y[i, k - 1]])
            # Store indices
            # (+1) because of the different indexing of python & HM
            id_s[i, j] = i * 2 * self.n_nodes + k + 1
