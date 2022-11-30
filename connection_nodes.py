"""A script that contains the class that calculates the IDs that define con."""

import numpy as np


class ConnectionNodes:
    """A class for the calculation of the connection nodes."""

    def __init__(self, parameters, x_y_z, n_spars, n_stringers):

        # Initialize matrices for LE and TE storing
        self.LE_IDs = np.zeros((3, parameters.N_ribs, 1))
        self.TE_IDs_u = np.zeros((3, parameters.N_ribs, 1))
        self.TE_IDs_l = np.zeros((3, parameters.N_ribs, 1))

        # Define their values
        self.calculate_le_te_ids(parameters)
        # Put the other node ids in the curve arrays
        self.put_in_arrays(parameters, x_y_z, n_spars, n_stringers)
        # Insert the TE and LE ids to curve arrays
        self.insert_le_te(n_spars, n_stringers, parameters.N_ribs)

        for i in range(0, 3):
            for j in range(0, parameters.N_ribs):
                self.Curve_IDs_Upper[i, j, :] =\
                    self.pushZerosToEnd(self.Curve_IDs_Upper[i, j, :])
                self.Curve_IDs_Lower[i, j, :] =\
                    self.pushZerosToEnd(self.Curve_IDs_Lower[i, j, :])
    def put_in_arrays(self, parameters, x_y_z, n_spars, n_stringers):
        # Insert them to the arrays
        self.Curve_IDs_Upper =\
            np.zeros((3, parameters.N_ribs,
                      3 * n_spars + n_stringers))
        self.Curve_IDs_Lower =\
            np.zeros((3, parameters.N_ribs,
                      3 * n_spars + n_stringers))

        for i in range(0, parameters.N_ribs):
            for k in range(0, 3):
                self.Curve_IDs_Upper[k, i, :] =\
                    - np.sort(- np.concatenate((
                        x_y_z.Spar_ID_Upper[k, i, :],
                        x_y_z.Spar_Cap_ID_Upper_Left[k, i, :],
                        x_y_z.Spar_Cap_ID_Upper_Right[k, i, :],
                        x_y_z.stringer_par_id_upper[k, i, :]
                        )))
                self.Curve_IDs_Lower[k, i, :] =\
                    np.sort(np.concatenate((
                        x_y_z.Spar_ID_Lower[k, i, :],
                        x_y_z.Spar_Cap_ID_Lower_Left[k, i, :],
                        x_y_z.Spar_Cap_ID_Lower_Right[k, i, :],
                        x_y_z.stringer_par_id_lower[k, i, :]
                        )))
        self.Curve_IDs_Upper = self.Curve_IDs_Upper.astype(int)
        self.Curve_IDs_Lower = self.Curve_IDs_Lower.astype(int)

    def calculate_le_te_ids(self, parameters):

        for i in range(0, parameters.N_ribs):
            for k in range(0, 3):
                self.LE_IDs[k, i, 0] = ((2 * i + 1) * parameters.n) + parameters.N_ribs * 240 * k
                self.TE_IDs_u[k, i, 0] = ((2 * i) * parameters.n + 1) + parameters.N_ribs * 240 * k
                self.TE_IDs_l[k, i, 0] = ((2 * i + 2) * parameters.n) + parameters.N_ribs * 240 * k

    def insert_le_te(self, n_spars, n_stringers, n_ribs):
        Curve_IDs_Upper_all =np.zeros((3, n_ribs, 3 * n_spars + n_stringers + 2))
        Curve_IDs_Lower_all =np.zeros((3, n_ribs, 3 * n_spars + n_stringers + 2))

        for k in range(0, 3):
            Curve_IDs_Upper =\
                np.insert(self.Curve_IDs_Upper[k, :, :],
                          3 * n_spars + n_stringers, self.TE_IDs_u[k, :, 0], axis=1)
            Curve_IDs_Upper =\
                np.insert(Curve_IDs_Upper, 0, self.LE_IDs[k, :, 0], axis=1)

            Curve_IDs_Lower =\
                np.insert(self.Curve_IDs_Lower[k, :, :],
                          3 * n_spars + n_stringers, self.TE_IDs_l[k, :, 0], axis=1)
            Curve_IDs_Lower =\
                np.insert(Curve_IDs_Lower, 0, self.LE_IDs[k, :, 0], axis=1)

            Curve_IDs_Upper_all[k, :, :] = Curve_IDs_Upper
            Curve_IDs_Lower_all[k, :, :] = Curve_IDs_Lower

        # Make them integers
        self.Curve_IDs_Upper = Curve_IDs_Upper_all.astype(int)
        self.Curve_IDs_Lower = Curve_IDs_Lower_all.astype(int)

    def pushZerosToEnd(self, arr):
        n = len(arr)
        count = 0 # Count of non-zero elements
    
        # Traverse the array. If element
        # encountered is non-zero, then
        # replace the element at index
        # 'count' with this element
        for i in range(n):
            if arr[i] != 0:
    
                # here count is incremented
                arr[count] = arr[i]
                count+=1
    
        # Now all non-zero elements have been
        # shifted to front and 'count' is set
        # as index of first 0. Make all
        # elements 0 from count to end.
        while count < n:
            arr[count] = 0
            count += 1
        return arr