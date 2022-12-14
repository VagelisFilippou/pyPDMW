""" This is a module that contains the dataclass for the mesh parameters"""
from dataclasses import dataclass


@dataclass
class Parameters:
    """
    It's a dataclass for storing the values of the mesh parameters
    """
    global_size: float  # Global element size
    mesh_refinement: int  # Mesh refinement in the spanwise direction

    def __post_init__(self):
        if self.mesh_refinement == 0 or self.mesh_refinement == 1:
            pass
        else:
            self.error()

    def error(self):
        raise Exception("Error: give a valid number for mesh refinement (0 or 1)")
