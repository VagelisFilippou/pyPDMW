"""A script that contains the class that calculates the IDs that define con."""

import numpy as np


class ConnectionNodes:
    """A class for the calculation of the connection nodes."""

    def __init__(self, Parameters, XYZ, N_spars):
        N_ribs = Parameters.N_ribs
        n = Parameters.n
        Spar_ID_Lower = XYZ.Spar_ID_Lower
        Spar_ID_Upper = XYZ.Spar_ID_Upper
        Spar_Cap_ID_Lower_Left = XYZ.Spar_Cap_ID_Lower_Left
        Spar_Cap_ID_Upper_Left = XYZ.Spar_Cap_ID_Upper_Left
        Spar_Cap_ID_Lower_Right = XYZ.Spar_Cap_ID_Lower_Right
        Spar_Cap_ID_Upper_Right = XYZ.Spar_Cap_ID_Upper_Right

        # Initialize matrices for LE and TE storing
        LE_IDs = np.zeros((N_ribs, 1))
        TE_IDs_u = np.zeros((N_ribs, 1))
        TE_IDs_l = np.zeros((N_ribs, 1))

        # Define their values
        for i in range(0, N_ribs):
            LE_IDs[i, 0] = (2 * i + 1) * n
            TE_IDs_u[i, 0] = (2 * i) * n + 1
            TE_IDs_l[i, 0] = (2 * i + 2) * n

        # Insert them to the arrays
        Curve_IDs_Upper = np.zeros((N_ribs, 3 * N_spars))
        Curve_IDs_Lower = np.zeros((N_ribs, 3 * N_spars))

        for i in range(0, N_ribs):
            Curve_IDs_Upper[i, :] = - np.sort(- np.concatenate(np.array([
                                                        Spar_ID_Upper[i, :],
                                                        Spar_Cap_ID_Upper_Left[i, :],
                                                        Spar_Cap_ID_Upper_Right[i, :]]
                                                        )))
            Curve_IDs_Lower[i, :] = np.sort(np.concatenate(np.array([
                                                        Spar_ID_Lower[i, :],
                                                        Spar_Cap_ID_Lower_Left[i, :],
                                                        Spar_Cap_ID_Lower_Right[i, :]]
                                                        )))


        Curve_IDs_Upper = np.insert(Curve_IDs_Upper, 3 * N_spars, TE_IDs_u[:, 0],
                                    axis=1)
        Curve_IDs_Upper = np.insert(Curve_IDs_Upper, 0, LE_IDs[:, 0], axis=1)
        Curve_IDs_Lower = np.insert(Curve_IDs_Lower, 3 * N_spars, TE_IDs_l[:, 0],
                                    axis=1)
        Curve_IDs_Lower = np.insert(Curve_IDs_Lower, 0, LE_IDs[:, 0], axis=1)

        self.Curve_IDs_Upper = Curve_IDs_Upper.astype(int)
        self.Curve_IDs_Lower = Curve_IDs_Lower.astype(int)
        self.LE_IDs = LE_IDs
        self.TE_IDs_u = TE_IDs_u
        self.TE_IDs_l = TE_IDs_l
