import numpy as np


class Curve:

    def __init__(self, N_1, N_2, IDs, curvecounter):

        self.N_1 = N_1
        self.N_2 = N_2
        self.IDs = IDs
        self.curvecounter = curvecounter
        self.Curves = np.zeros((self.N_1, self.N_2))

    def ListCreation(self, i, j):
        my_list = list(range(self.IDs[i, j + 1], self.IDs[i, j] + 1))
        return my_list

    def WriteTcl(self):
        with open('Wing_Geometry_Generation.tcl', 'a+') as f:
            for i in range(0, self.N_1):
                for j in range(0, self.N_2):
                    my_list = self.ListCreation(i, j)
                    my_str = ' '.join(map(str, my_list))
                    cmd = "*createlist nodes 1 " + my_str
                    f.write(cmd)
                    f.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0\n"
                            "*linecreatespline nodes 1 0 0 1 2\n")
                    self.curvecounter += 1
                    self.Curves[i, j] = self.curvecounter


class UpperRibCurve(Curve):
    def ListCreation(self, i, j):
        my_list = list(range(self.IDs[i, j], self.IDs[i, j + 1] + 1))
        return my_list
