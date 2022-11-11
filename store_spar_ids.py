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

        Spars_nodes_X = Spars_And_Spar_Caps.Spars_nodes_X
        Spar_Caps_XL = Spars_And_Spar_Caps.Spar_Caps_XL
        Spar_Caps_XR = Spars_And_Spar_Caps.Spar_Caps_XR

        """
        ### Put the spars' coordinates in the XYZ arrays and store their index:
        """
        # Initialize ID lists that spar nodes will be stored
        Spar_ID_Lower = []
        Spar_ID_Upper = []
        Spar_Cap_ID_Lower_Left = []
        Spar_Cap_ID_Upper_Left = []
        Spar_Cap_ID_Lower_Right = []
        Spar_Cap_ID_Upper_Right = []

        # Lower nodes of spars
        for i in range(0, N_ribs):
            for j in range(0, N_spars):
                for k in range(n, 2 * n):
                    if k < 2 * n - 1 and \
                            X[i, k - 1] < Spars_nodes_X[j, i] < X[i, k + 1]:
                        X[i, k] = Spars_nodes_X[j, i]
                        Z[i, k] = np.interp(X[i, k], [X[i, k - 1],
                                                      X[i, k + 1]],
                                            [Z[i, k - 1], Z[i, k + 1]])
                        Y[i, k] = np.interp(X[i, k], [X[i, k - 1],
                                                      X[i, k + 1]],
                                            [Y[i, k - 1], Y[i, k + 1]])
                        # Store indices
                        # (+1) because of the different indexing of python & HM
                        Spar_ID_Lower.append(i * 2 * n + k + 1)
                    if k < 2 * n - 1 and \
                            X[i, k - 1] < Spar_Caps_XL[j, i] < X[i, k + 1]:
                        X[i, k] = Spar_Caps_XL[j, i]
                        Z[i, k] = np.interp(X[i, k], [X[i, k - 1],
                                                      X[i, k + 1]],
                                            [Z[i, k - 1], Z[i, k + 1]])
                        Y[i, k] = np.interp(X[i, k], [X[i, k - 1],
                                                      X[i, k + 1]],
                                            [Y[i, k - 1], Y[i, k + 1]])
                        # Store indices
                        # (+1) because of the different indexing of python & HM
                        Spar_Cap_ID_Lower_Left.append(i * 2 * n + k + 1)
                    if k < 2 * n - 1 and \
                            X[i, k - 1] < Spar_Caps_XR[j, i] < X[i, k + 1]:
                        X[i, k] = Spar_Caps_XR[j, i]
                        Z[i, k] = np.interp(X[i, k], [X[i, k - 1],
                                                      X[i, k + 1]],
                                            [Z[i, k - 1], Z[i, k + 1]])
                        Y[i, k] = np.interp(X[i, k], [X[i, k - 1],
                                                      X[i, k + 1]],
                                            [Y[i, k - 1], Y[i, k + 1]])
                        # Store indices
                        # (+1) because of the different indexing of python & HM
                        Spar_Cap_ID_Lower_Right.append(i * 2 * n + k + 1)
        # Reshape to a matrix for easier handling
        Spar_ID_Lower = np.array(Spar_ID_Lower)
        self.Spar_ID_Lower = Spar_ID_Lower.reshape(N_ribs, N_spars)

        Spar_Cap_ID_Lower_Left = np.array(Spar_Cap_ID_Lower_Left)
        self.Spar_Cap_ID_Lower_Left = Spar_Cap_ID_Lower_Left.reshape(N_ribs,
                                                                     N_spars)

        Spar_Cap_ID_Lower_Right = np.array(Spar_Cap_ID_Lower_Right)
        self.Spar_Cap_ID_Lower_Right = Spar_Cap_ID_Lower_Right.reshape(N_ribs,
                                                                       N_spars)

        # Upper nodes of spars
        for i in range(0, N_ribs):
            for j in range(0, N_spars):
                for k in range(0, n):
                    if k < 2 * n - 1 and \
                            X[i, k - 1] > Spars_nodes_X[j, i] > X[i, k + 1]:
                        X[i, k] = Spars_nodes_X[j, i]
                        Z[i, k] = np.interp(X[i, k], [X[i, k + 1],
                                                      X[i, k - 1]],
                                            [Z[i, k + 1], Z[i, k - 1]])
                        Y[i, k] = np.interp(X[i, k], [X[i, k + 1],
                                                      X[i, k - 1]],
                                            [Y[i, k + 1], Y[i, k - 1]])
                        # Store indices
                        # (+1) because of the different indexing of python & HM
                        Spar_ID_Upper.append(i * 2 * n + k + 1)
                    if k < 2 * n - 1 and \
                            X[i, k - 1] > Spar_Caps_XL[j, i] > X[i, k + 1]:
                        X[i, k] = Spar_Caps_XL[j, i]
                        Z[i, k] = np.interp(X[i, k], [X[i, k + 1],
                                                      X[i, k - 1]],
                                            [Z[i, k + 1], Z[i, k - 1]])
                        Y[i, k] = np.interp(X[i, k], [X[i, k + 1],
                                                      X[i, k - 1]],
                                            [Y[i, k + 1], Y[i, k - 1]])
                        # Store indices
                        # (+1) because of the different indexing of python & HM
                        Spar_Cap_ID_Upper_Left.append(i * 2 * n + k + 1)
                    if k < 2 * n - 1 and \
                            X[i, k - 1] > Spar_Caps_XR[j, i] > X[i, k + 1]:
                        X[i, k] = Spar_Caps_XR[j, i]
                        Z[i, k] = np.interp(X[i, k], [X[i, k + 1],
                                                      X[i, k - 1]],
                                            [Z[i, k + 1], Z[i, k - 1]])
                        Y[i, k] = np.interp(X[i, k], [X[i, k + 1],
                                                      X[i, k - 1]],
                                            [Y[i, k + 1], Y[i, k - 1]])
                        # Store indices
                        # (+1) because of the different indexing of python & HM
                        Spar_Cap_ID_Upper_Right.append(i * 2 * n + k + 1)

        # Reshape to a matrix for easier handling
        Spar_ID_Upper = np.array(Spar_ID_Upper)
        self.Spar_ID_Upper = Spar_ID_Upper.reshape(N_ribs, N_spars)

        Spar_Cap_ID_Upper_Left = np.array(Spar_Cap_ID_Upper_Left)
        self.Spar_Cap_ID_Upper_Left = Spar_Cap_ID_Upper_Left.reshape(N_ribs,
                                                                     N_spars)

        Spar_Cap_ID_Upper_Right = np.array(Spar_Cap_ID_Upper_Right)
        self.Spar_Cap_ID_Upper_Right = Spar_Cap_ID_Upper_Right.reshape(N_ribs,
                                                                       N_spars)
        self.X = X
        self.Y = Y
        self.Z = Z
