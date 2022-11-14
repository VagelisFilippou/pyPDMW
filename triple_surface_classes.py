# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 17:04:17 2022

@author: EFILIPPO
"""

import numpy as np


class MultipleSurfaces:
    def __init__(self, n_1, n_2, n_3, ids_1, ids_2, ids_3, ids_4,
                 surfacecounter, componentcounter, assemblycounter,
                 components_name):

        self.n_1 = n_1
        self.n_2 = n_2
        self.n_3 = n_3

        self.ids_1 = ids_1
        self.ids_2 = ids_2
        self.ids_3 = ids_3
        self.ids_4 = ids_4

        self.surfaces = np.zeros((self.n_1, self.n_2, self.n_3))
        self.components = np.zeros((self.n_1, 1))
        self.surfacecounter = surfacecounter
        self.componentcounter = componentcounter
        self.assemblycounter = assemblycounter
        self.components_name = components_name
        self.write_tcl()

    def list_creation(self, i, j, k):
        my_list = list((self.ids_1[i, j, k],
                        self.ids_2[i, j, k],
                        self.ids_3[i, j * (self.n_3)],
                        self.ids_4[i, j * (self.n_3) + 1]))
        return my_list

    def write_tcl(self):
        with open('Wing_Geometry_Generation.tcl', 'a+') as file:
            for i in range(0, self.n_1):
                for j in range(0, self.n_2):
                    for k in range(0, self.n_3):
                        if k != 0:
                            my_list = self.list_creation(i, j, k)
                            my_str = ' '.join(map(str, my_list))
                            cmd = "*surfacemode 4\n*createmark lines 1 " + my_str
                            file.write(cmd)
                            file.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
                            self.surfacecounter += 1
                            self.surfaces[i, j] = self.surfacecounter
