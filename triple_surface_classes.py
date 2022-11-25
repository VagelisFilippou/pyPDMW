# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 17:04:17 2022

@author: EFILIPPO
"""

import numpy as np


class MultipleSurfaces:
    def __init__(self, n_1, n_2, n_3, ids_1, ids_2, ids_3, ids_4,
                 surface_counter, component_counter, assembly_counter,
                 components_name):

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
        self.write_tcl()

    def list_creation(self, i, j, k):
        my_list = list((self.ids_1[i, j, k],
                        self.ids_2[i, j, k],
                        self.ids_3[i, j, k - 1],
                        self.ids_4[i, j, k]))
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
                            self.surface_counter += 1
                            self.surfaces[i, j, k - 1] = self.surface_counter
                self.component_counter += 1
                self.components[i, 0] = self.component_counter
                file.write('*createentity comps name="'
                           + self.components_name + '_%.0f"\n'
                           % (i + 1))
                file.write(
                    '*startnotehistorystate {Moved surfaces into component "'
                    + self.components_name + '_%.0f"}\n' % (i + 1))
                file.write('*createmark surfaces 1 %.0f-%.0f\n'
                           % (self.surfaces[i, 0, 0], self.surfaces[i, -1, -1]))
                file.write('*movemark surfaces 1 "'
                           + self.components_name + '_%.0f"\n'
                           % (i + 1))
                file.write('*endnotehistorystate {Moved surfaces into component "'
                           + self.components_name + '_%.0f"}\n'
                           % (i + 1))
            file.write(
                '*createentity assems name="'
                + self.components_name + '"\n')
            file.write(
                '*startnotehistorystate {Modified Components of assembly}\n')
            file.write('*setvalue assems id=%.0f components={comps %.0f-%.0f}'
                       % (self.assembly_counter,
                          self.components[0, 0],
                          self.components[-1, 0]))
            file.write(
                '\n*endnotehistorystate {Modified Components of assembly}\n')
        file.close()
        self.assembly_counter += 1


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

    def write_tcl(self):
        with open('Wing_Geometry_Generation.tcl', 'a+') as file:
            for i in range(0, self.n_1):
                for j in range(0, self.n_2):
                    for k in range(0, self.n_3):
                        my_list = self.list_creation(i, j, k)
                        my_str = ' '.join(map(str, my_list))
                        cmd = "*surfacemode 4\n*createmark lines 1 " + my_str
                        file.write(cmd)
                        file.write("\n*surfacesplineonlinesloop 1 1 0 67\n")
                        self.surface_counter += 1
                        self.surfaces[i, j, k] = self.surface_counter
                self.component_counter += 1
                self.components[i, 0] = self.component_counter
                file.write('*createentity comps name="'
                           + self.components_name + '_%.0f"\n'
                           % (i + 1))
                file.write(
                    '*startnotehistorystate {Moved surfaces into component "'
                    + self.components_name + '_%.0f"}\n' % (i + 1))
                file.write('*createmark surfaces 1 %.0f-%.0f\n'
                           % (self.surfaces[i, 0, 0], self.surfaces[i, -1, -1]))
                file.write('*movemark surfaces 1 "'
                           + self.components_name + '_%.0f"\n'
                           % (i + 1))
                file.write('*endnotehistorystate {Moved surfaces into component "'
                           + self.components_name + '_%.0f"}\n'
                           % (i + 1))
            file.write(
                '*createentity assems name="'
                + self.components_name + '"\n')
            file.write(
                '*startnotehistorystate {Modified Components of assembly}\n')
            file.write('*setvalue assems id=%.0f components={comps %.0f-%.0f}'
                       % (self.assembly_counter,
                          self.components[0, 0],
                          self.components[-1, 0]))
            file.write(
                '\n*endnotehistorystate {Modified Components of assembly}\n')
        file.close()
        self.assembly_counter += 1
