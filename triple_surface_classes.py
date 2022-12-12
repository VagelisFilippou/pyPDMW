import numpy as np


class MultipleSurfaces:
    def __init__(self, n_1, n_2, n_3, ids_1, ids_2, ids_3, ids_4,
                 surface_counter, file):

        self.n_1 = n_1
        self.n_2 = n_2
        self.n_3 = n_3

        self.ids_1 = ids_1
        self.ids_2 = ids_2
        self.ids_3 = ids_3
        self.ids_4 = ids_4

        self.surfaces = np.zeros((self.n_1, self.n_2, self.n_3 - 1))
        self.surface_counter = surface_counter

        self.write_tcl(file)

    def list_creation(self, i, j, k):
        my_list = list((self.ids_1[i, j, k],
                        self.ids_2[i, j, k],
                        self.ids_3[i, j, k - 1],
                        self.ids_4[i, j, k]))
        return my_list

    def write_tcl(self, file):
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


class StringerSurfaces(MultipleSurfaces):
    def __init__(self, n_1, n_2, n_3, ids_1, ids_2,
                 surface_counter, file):

        self.n_1 = n_1
        self.n_2 = n_2
        self.n_3 = n_3

        self.ids_1 = ids_1
        self.ids_2 = ids_2

        self.surfaces = np.zeros((self.n_1, self.n_2, self.n_3))
        self.surface_counter = surface_counter

        self.write_tcl(file)

    def list_creation(self, i, j, k):
        my_list = list((self.ids_1[i, j, k],
                        self.ids_2[i, j, k],
                        ))
        return my_list

    def write_tcl(self, file):
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


class RibStiffners:
    def __init__(self, n_1, n_2, ids_1, ids_2, ids_3, ids_4,
                 surface_counter, file):

        self.n_1 = n_1
        self.n_2 = n_2

        self.ids_1 = ids_1
        self.ids_2 = ids_2
        self.ids_3 = ids_3
        self.ids_4 = ids_4

        self.surfaces = np.zeros((self.n_1, self.n_2))
        self.components = np.zeros((self.n_1, 1))
        self.surface_counter = surface_counter

        self.write_tcl(file)

    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, j],
                        self.ids_2[i, j],
                        self.ids_3[i, j],
                        self.ids_4[i, j]))
        return my_list

    def write_tcl(self, file):
        for i in range(0, self.n_1):
            for j in range(0, self.n_2):
                my_list = self.list_creation(i, j)
                my_str = ' '.join(map(str, my_list))
                cmd = "*surfacemode 4\n*createlist nodes 1 " + my_str
                file.write(cmd)
                file.write("\n*surfacesplineonnodesloop2 1 0\n")
                self.surface_counter += 1
                self.surfaces[i, j] = self.surface_counter
