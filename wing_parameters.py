""" This is a module that contains the dataclass for the wing's parameters"""
from dataclasses import dataclass
import numpy as np


@dataclass
class Parameters:
    """
    It's a dataclass for storing the values of the parameters of the wing
    """
    semi_span: float
    # Yehudi Break in Percent of Semi-span
    yb_percent: float
    # Define Wing's Structural Derived_Geometry
    n_spars: int
    n_ribs_central: int
    n_ribs_yehudi: int
    n_ribs_semispan: int
    front_spar_position: float  # the location of each spar normalized
    rear_spar_position: float  # the location of each spar normalized
    # Specify the length of the fuselage wing-box
    fslg_section_percent: float
    # Define two widths per spar at the root and at the tip:
    root_l: float
    root_r: float
    tip_l: float
    tip_r: float
    # Stringers number per spar section
    n_stringers: int
    stringers_tolerance: float
    rib_stiffeners_width: float

    # List with the location of each spar
    def spars_position(self):
        """Lin-space for the spars' position"""
        spars_position = np.linspace(self.front_spar_position,
                                     self.rear_spar_position,
                                     num=self.n_spars,
                                     endpoint=True)
        return spars_position

    def sc_widths(self):
        """Array for spar caps widths"""
        sc_widths = np.array([[self.root_l, self.root_r],
                              [self.tip_l, self.tip_r]]) * 0.6
        return sc_widths

    def stringers_pos(self):
        """Lin-space for the spars' position"""
        stringers_position = np.zeros((self.n_spars - 1, self.n_stringers))
        spars_pos = self.spars_position()
        for i in range(0, self.n_spars - 1):
            stringers_position[i, :] =\
                np.linspace(spars_pos[i] + self.stringers_tolerance,
                            spars_pos[i + 1] - self.stringers_tolerance,
                            num=self.n_stringers, endpoint=True)
        stringers_position = np.concatenate(stringers_position)
        return stringers_position
