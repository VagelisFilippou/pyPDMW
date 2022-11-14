"""A script that contains the class that calculates the IDs that define con."""

import numpy as np


class ConnectionNodes:
    """A class for the calculation of the connection nodes."""

    def __init__(self, Parameters, XYZ, N_spars, N_stringers):

        # Initialize matrices for LE and TE storing
        self.LE_IDs = np.zeros((Parameters.N_ribs, 1))
        self.TE_IDs_u = np.zeros((Parameters.N_ribs, 1))
        self.TE_IDs_l = np.zeros((Parameters.N_ribs, 1))

        # Define their values
        self.calculate_le_te_ids(Parameters)
        # Put the other node ids in the curve arrays
        self.put_in_arrays(Parameters, XYZ, N_spars, N_stringers)
        # Insert the TE and LE ids to curve arrays
        self.insert_le_te(N_spars, N_stringers)

    def put_in_arrays(self, parameters, xyz, n_spars, n_stringers):
        # Insert them to the arrays
        self.Curve_IDs_Upper =\
            np.zeros((parameters.N_ribs,
                      3 * n_spars + n_stringers))
        self.Curve_IDs_Lower =\
            np.zeros((parameters.N_ribs,
                      3 * n_spars + n_stringers))

        for i in range(0, parameters.N_ribs):
            self.Curve_IDs_Upper[i, :] =\
                - np.sort(- np.concatenate((
                    xyz.Spar_ID_Upper[i, :],
                    xyz.Spar_Cap_ID_Upper_Left[i, :],
                    xyz.Spar_Cap_ID_Upper_Right[i, :],
                    xyz.stringer_id_upper[i, :]
                    )))
            self.Curve_IDs_Lower[i, :] =\
                np.sort(np.concatenate((
                    xyz.Spar_ID_Lower[i, :],
                    xyz.Spar_Cap_ID_Lower_Left[i, :],
                    xyz.Spar_Cap_ID_Lower_Right[i, :],
                    xyz.stringer_id_lower[i, :]
                    )))
        self.Curve_IDs_Upper = self.Curve_IDs_Upper.astype(int)
        self.Curve_IDs_Lower = self.Curve_IDs_Lower.astype(int)

    def calculate_le_te_ids(self, parameters):

        for i in range(0, parameters.N_ribs):
            self.LE_IDs[i, 0] = (2 * i + 1) * parameters.n
            self.TE_IDs_u[i, 0] = (2 * i) * parameters.n + 1
            self.TE_IDs_l[i, 0] = (2 * i + 2) * parameters.n

    def insert_le_te(self, n_spars, n_stringers):

        self.Curve_IDs_Upper =\
            np.insert(self.Curve_IDs_Upper,
                      3 * n_spars + n_stringers, self.TE_IDs_u[:, 0], axis=1)
        self.Curve_IDs_Upper =\
            np.insert(self.Curve_IDs_Upper, 0, self.LE_IDs[:, 0], axis=1)
        self.Curve_IDs_Lower =\
            np.insert(self.Curve_IDs_Lower,
                      3 * n_spars + n_stringers, self.TE_IDs_l[:, 0], axis=1)
        self.Curve_IDs_Lower =\
            np.insert(self.Curve_IDs_Lower, 0, self.LE_IDs[:, 0], axis=1)
        # Make them integers
        self.Curve_IDs_Upper = self.Curve_IDs_Upper.astype(int)
        self.Curve_IDs_Lower = self.Curve_IDs_Lower.astype(int)


def sortRowWise(m):
    # One by one sort individual rows.
    for i in range(len(m)):
        m[i].sort()
        # printing the sorted matrix
        for i in range(len(m)):
            for j in range(len(m[i])):
                print(m[i][j], end=" ")
                print()
    return 0
