"""
Parameters extraction and Coordinates.

A script that contains the class for the derivation of necessary parameters
and XYZ coordinates of the wing's ribs
"""
import numpy as np
from read_oml import read_oml


class DerivedGeometry:
    """Class for geometric parametrs of the wing ribs' coords."""

    def __init__(self,
                 SemiSpan,
                 YB_percent,
                 N_spars,
                 N_ribs_central,
                 N_ribs_yehudi,
                 N_ribs_semispan,
                 Spars_position,
                 Fuselage_section_percent,
                 SC_width):
        """################## Derived Parameters: ##################."""
        # Half of the number of airfoil points to use it in indexing
        self.n = 120

        # Number of ribs in total
        self.N_ribs = N_ribs_central + N_ribs_yehudi + N_ribs_semispan
        self.Rib_Sections_ID = [N_ribs_central, N_ribs_central + N_ribs_yehudi,
                                self.N_ribs]

        # Yehudi Break
        self.Yehudi = SemiSpan * YB_percent

        # Fuselage_rib :The index of the rib that is near the fuselage
        # Until this rib, spars are aligned with the Y axis
        self.FSL = Fuselage_section_percent * SemiSpan

        # Define ribs spacing or ribs number
        self.Ribs_Spacing_central = self.FSL / (N_ribs_central - 1)
        self.Ribs_Spacing_yehudi = (self.Yehudi - self.FSL) / N_ribs_yehudi
        self.Ribs_Spacing_semispan = (SemiSpan - self.Yehudi) / N_ribs_semispan

        """
        ### Calculate positions in Y and the origins: ###
        """
        # Initialize a list to put the Y positions of each rib
        self.Y_list = []

        # Calculate the positions and append them to the list
        for i in range(0, N_ribs_central):
            self.Y_list.append(i * self.Ribs_Spacing_central)
        for i in range(0, N_ribs_yehudi):
            self.Y_list.append((i + 1) * self.Ribs_Spacing_yehudi +
                               self.Y_list[self.Rib_Sections_ID[0] - 1])
        for i in range(0, N_ribs_semispan):
            self.Y_list.append((i + 1) * self.Ribs_Spacing_semispan +
                               self.Y_list[self.Rib_Sections_ID[1] - 1])

        # Read the origins of each airfoil (from the data)
        x_origin, y_origin, z_origin, _, _ = read_oml()

        # Initialize an array that will contain the origins of the ribs
        self.Origin = np.zeros((self.N_ribs, 3))
        self.Origin[:, 2] = self.Y_list

        # Find their x and z coordinates by interpolation
        self.Origin[:, 0] = np.interp(self.Origin[:, 2],
                                      y_origin[:],
                                      x_origin[:, 0])
        self.Origin[:, 1] = np.interp(self.Origin[:, 2],
                                      y_origin[:],
                                      z_origin[:, 0])
