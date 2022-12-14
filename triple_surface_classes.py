# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 17:04:17 2022

@author: EFILIPPO
"""

import numpy as np


class MultipleSurfaces:
    def __init__(self, n_1, n_2, n_3, ids_1, ids_2, ids_3, ids_4,
                 surface_counter, component_counter, assembly_counter,
                 components_name, curve):

        self.n_1 = n_1
        self.n_2 = n_2
        self.n_3 = n_3

        self.ids_1 = ids_1
        self.ids_2 = ids_2
        self.ids_3 = ids_3
        self.ids_4 = ids_4

        self.surfaces = np.zeros((self.n_1, self.n_2, self.n_3 - 1))
        self.components = np.zeros((self.n_1, 1))
        self.surface_counter = surface_counter
        self.component_counter = component_counter
        self.assembly_counter = assembly_counter
        self.components_name = components_name
        self.write_tcl(curve)

    def list_creation(self, i, j, k, zeros):
        my_list = list((self.ids_1[i, j, k],
                        self.ids_2[i, j, k],
                        self.ids_3[i, j, k - 1 + zeros],
                        self.ids_4[i, j, k + zeros]))
        return my_list

    def check_for_zeros(self, i, j, k, zeros):
        check = 0
        if self.ids_1[i, j, k] == 0 or self.ids_2[i, j, k] == 0 or\
                self.ids_3[i, j, k - 1 + zeros] == 0 or\
                self.ids_4[i, j, k + zeros] == 0:
            check = 1
        return check

    def write_tcl(self, curve):
        with open('Wing_Geometry_Generation.tcl', 'a+') as file:
            for i in range(0, self.n_1):
                zeros = return_zeros(curve[i, :])
                for j in range(0, self.n_2):
                    for k in range(0, self.n_3 - zeros):
                        if k != 0 and self.check_for_zeros(i, j, k, zeros) != 1:
                            my_list = self.list_creation(i, j, k, zeros)
                            my_str = ' '.join(map(str, my_list))
                            cmd = "*surfacemode 4\n*createmark lines 1 " + my_str
                            file.write(cmd)
                            file.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
                            self.surface_counter += 1
                            self.surfaces[i, j, k - 1] = self.surface_counter
        file.close()


class StringerSurfaces(MultipleSurfaces):
    def __init__(self, n_1, n_2, n_3, ids_1, ids_2,
                 surface_counter, component_counter, assembly_counter,
                 components_name):

        self.n_1 = n_1
        self.n_2 = n_2
        self.n_3 = n_3

        self.ids_1 = ids_1
        self.ids_2 = ids_2

        self.surfaces = np.zeros((self.n_1, self.n_2, self.n_3))
        self.components = np.zeros((self.n_1, 1))
        self.surface_counter = surface_counter
        self.component_counter = component_counter
        self.assembly_counter = assembly_counter
        self.components_name = components_name
        self.write_tcl()

    def list_creation(self, i, j, k):
        my_list = list((self.ids_1[i, j, k],
                        self.ids_2[i, j, k],
                        ))
        return my_list

    def check_for_zeros(self, i, j, k):
        check = 0
        if self.ids_1[i, j, k] == 0 or self.ids_2[i, j, k] == 0:
            check = 1
        return check

    def write_tcl(self):
        with open('Wing_Geometry_Generation.tcl', 'a+') as file:
            for i in range(0, self.n_1):
                for j in range(0, self.n_2):
                    for k in range(0, self.n_3):
                        if self.check_for_zeros(i, j, k) != 1:
                            my_list = self.list_creation(i, j, k)
                            my_str = ' '.join(map(str, my_list))
                            cmd = "*surfacemode 4\n*createmark lines 1 " + my_str
                            file.write(cmd)
                            file.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
                            self.surface_counter += 1
                            self.surfaces[i, j, k] = self.surface_counter
        file.close()


class RibStiffners:
    def __init__(self, n_1, n_2, ids_1, ids_2, ids_3, ids_4,
                 surface_counter, component_counter, assembly_counter,
                 components_name):

        self.n_1 = n_1
        self.n_2 = n_2

        self.ids_1 = ids_1
        self.ids_2 = ids_2
        self.ids_3 = ids_3
        self.ids_4 = ids_4

        self.surfaces = np.zeros((self.n_1, self.n_2))
        self.components = np.zeros((self.n_1, 1))
        self.surface_counter = surface_counter
        self.component_counter = component_counter
        self.assembly_counter = assembly_counter
        self.components_name = components_name
        self.write_tcl()

    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, j],
                        self.ids_2[i, j],
                        self.ids_3[i, j],
                        self.ids_4[i, j]))
        return my_list

    def check_for_zeros(self, i, j):
        check = 0
        if self.ids_1[i, j] == 0 or self.ids_2[i, j] == 0:
            check = 1
        return check

    def write_tcl(self):
        with open('Wing_Geometry_Generation.tcl', 'a+') as file:
            for i in range(0, self.n_1):
                for j in range(0, self.n_2):
                    if self.check_for_zeros(i, j) != 1:
                        my_list = self.list_creation(i, j)
                        my_str = ' '.join(map(str, my_list))
                        cmd = "*surfacemode 4\n*createlist nodes 1 " + my_str
                        file.write(cmd)
                        file.write("\n*surfacesplineonnodesloop2 1 0\n")
                        self.surface_counter += 1
                        self.surfaces[i, j] = self.surface_counter
        file.close()


def return_ith_from_zero(vec):
    n_1 = len(vec)
    id_1 = 0
    for i in range(0, n_1):
        if vec[i] != 0:
            id_1 = i
            break
        else:
            pass
    return id_1

def return_zeros(vec):
    n_1 = len(vec)
    id_1 = 0
    for i in range(0, n_1):
        if vec[i] == 0:
            id_1 += 1
    return id_1

