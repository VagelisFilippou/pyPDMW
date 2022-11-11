import numpy as np


class UpperRibCurve:

    def __init__(self, n_1, n_2, ids, curvecounter):

        self.n_1 = n_1
        self.n_2 = n_2
        self.ids = ids
        self.curves = np.zeros((self.n_1, 3 * self.n_2 + 1))
        self.curvecounter = curvecounter
        self.curves, self.curvecounter = self.write_tcl()
        self.sections_id = RibCurveIDs(self.curves, self.n_1, self.n_2)

    def list_creation(self, i, j):
        my_list = list(range(self.ids[i, j + 1], self.ids[i, j] + 1))
        return my_list

    def write_tcl(self):
        with open('Wing_Geometry_Generation.tcl', 'a+') as file:
            for i in range(0, self.n_1):
                for j in range(0, 3 * self.n_2 + 1):
                    my_list = self.list_creation(i, j)
                    my_str = ' '.join(map(str, my_list))
                    cmd = "*createlist nodes 1 " + my_str
                    file.write(cmd)
                    file.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0"
                               "\n*linecreatespline nodes 1 0 0 1 2\n")
                    self.curvecounter += 1
                    self.curves[i, j] = self.curvecounter
        file.close()
        return self.curves, self.curvecounter


class RibCurveIDs:

    def __init__(self, curves, n_1, n_2):
        # Store the id of each curve type
        self.LE = curves[:, 0]
        self.TE = curves[:, -1]
        self.SC_L = np.zeros((n_1, n_2))
        self.SC_R = np.zeros((n_1, n_2))
        self.spars = np.zeros((n_1, n_2 - 1))
        for i in range(0, n_2):
            if i < n_2 - 1:
                self.SC_L[:, i] = curves[:, 3 * i + 1]
                self.SC_R[:, i] = curves[:, 3 * i + 2]
                self.spars[:, i] = curves[:, 3 * i + 3]
            elif i == n_2 - 1:
                self.SC_L[:, i] = curves[:, 3 * i + 1]
                self.SC_R[:, i] = curves[:, 3 * i + 2]


class LowerRibCurve(UpperRibCurve):
    def list_creation(self, i, j):
        my_list = list(range(self.ids[i, j], self.ids[i, j + 1] + 1))
        return my_list


class LeadingTrailingEdgeCurves:

    def __init__(self, n_1, n_2, ids, curvecounter):

        self.n_1 = n_1
        self.n_2 = n_2
        self.ids = ids
        self.curves = np.zeros((self.n_1 - 1, self.n_2))
        self.curvecounter = curvecounter
        self.curves, self.curvecounter = self.write_tcl()

    def list_creation(self, i):
        my_list = [self.ids[i, 0], self.ids[i + 1, 0]]
        return my_list

    def write_tcl(self):
        with open('Wing_Geometry_Generation.tcl', 'a+') as file:
            for i in range(0, self.n_1 - 1):
                my_list = self.list_creation(i)
                my_str = ' '.join(map(str, my_list))
                cmd = "*createlist nodes 1 " + my_str
                file.write(cmd)
                file.write("\n*linecreatefromnodes 1 0 150 5 179\n")
                self.curvecounter += 1
                self.curves[i, 0] = self.curvecounter
        file.close()
        return self.curves, self.curvecounter


class MultipleCurves:

    def __init__(self, n_1, n_2, ids_1, ids_2, curvecounter):

        self.n_1 = n_1
        self.n_2 = n_2
        self.ids_1 = ids_1
        self.ids_2 = ids_2
        self.curves = np.zeros((self.n_1, self.n_2))
        self.curvecounter = curvecounter
        self.curves, self.curvecounter = self.write_tcl()

    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, j], self.ids_2[i, j]))
        return my_list

    def write_tcl(self):
        with open('Wing_Geometry_Generation.tcl', 'a+') as file:
            for i in range(0, self.n_1):
                for j in range(0, self.n_2):
                    my_list = self.list_creation(i, j)
                    my_str = ' '.join(map(str, my_list))
                    cmd = "*createlist nodes 1 " + my_str
                    file.write(cmd)
                    file.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0"
                               "\n*linecreatespline nodes 1 0 0 1 2\n")
                    self.curvecounter += 1
                    self.curves[i, j] = self.curvecounter
        file.close()
        return self.curves, self.curvecounter


class SparAndSparCapCurves(MultipleCurves):
    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, j], self.ids_2[i + 1, j]))
        return my_list
