import numpy as np


class UpperRibCurve:

    def __init__(self, n_1, n_2, ids, parameters, curve_counter):
        n_stringers = len(parameters.stringers_pos())
        n_stringers_per_sect = parameters.n_stringers
        self.n_1 = n_1
        self.n_2 = n_2
        self.ids = ids
        self.curves = np.zeros((self.n_1, 3 * self.n_2 + 1 + n_stringers))
        self.curve_counter = curve_counter
        self.curves, self.curve_counter = self.write_tcl(n_stringers)
        self.sections_id = RibCurveIDs(self.curves, self.n_1, self.n_2,
                                       n_stringers_per_sect)

    def list_creation(self, i, j):
        my_list = list(range(self.ids[i, j + 1], self.ids[i, j] + 1))
        return my_list

    def check_for_zeros(self, i, j):
        check = 0
        if self.ids[i, j + 1] == 0 or self.ids[i, j] + 1 == 0:
            check = 1
        return check

    def write_tcl(self, n_stringers):
        with open('Wing_Geometry_Generation.tcl', 'a+') as file:
            for i in range(0, self.n_1):
                for j in range(0,  3 * self.n_2 + 1 + n_stringers):
                    if self.check_for_zeros(i, j) != 1:
                        my_list = self.list_creation(i, j)
                        if len(my_list) > 1:
                            my_str = ' '.join(map(str, my_list))
                            cmd = "*createlist nodes 1 " + my_str
                            file.write(cmd)
                            file.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0"
                                       "\n*linecreatespline nodes 1 0 0 1 2\n")
                            self.curve_counter += 1
                            self.curves[i, j] = self.curve_counter
        file.close()
        return self.curves, self.curve_counter


class RibCurveIDs:

    def __init__(self, curves, n_1, n_2, n_stringers_per_sect):
        # Store the id of each curve type
        n_0 = len(curves[:, 0])
        self.LE = curves[:, 0]
        self.TE = self.return_ith_from_zero(curves, 1)
        self.SC_L = np.zeros((n_1, n_2))
        self.SC_R = np.zeros((n_1, n_2))
        self.main_skin = np.zeros((n_1, n_2 - 1, n_stringers_per_sect + 1))
        main_skin_sect = np.zeros((n_1, n_stringers_per_sect + 1))
        for i in range(0, n_2):
            if i < n_2 - 1:
                self.SC_L[:, i] = curves[:, 1]
                self.SC_R[:, i] = curves[:, 2]
            elif i == n_2 - 1:
                self.SC_L[:, i] = self.return_ith_from_zero(curves, 2)
                self.SC_R[:, i] = self.return_ith_from_zero(curves, 3)
        for k in range(0, n_1):
            for i in range(0, n_2 - 1):
                for j in range(0, n_stringers_per_sect + 1):
                    main_skin_sect[:, j] =\
                        curves[:, (3 + n_stringers_per_sect) * i + 3 + j]
                    self.main_skin[:, i, :] = main_skin_sect

    def return_ith_from_zero(self, arr, id_from_zero):
        n_1 = len(arr[:, 0])
        n_2 = len(arr[0, :])
        id_s = []
        id_s_to_return = np.zeros((n_1))
        for i in range(0, n_1):
            if 0 in arr[i, :]:
                for j in range(0, n_2):
                    if arr[i, j] == 0:
                        id_s.append(j - id_from_zero)
                        break
            else:
                id_s.append(- id_from_zero)
            id_s_to_return[i] = arr[i, id_s[i]]
        return id_s_to_return


class LowerRibCurve(UpperRibCurve):
    def list_creation(self, i, j):
        my_list = list(range(self.ids[i, j], self.ids[i, j + 1] + 1))
        return my_list

    def check_for_zeros(self, i, j):
        check = 0
        if self.ids[i, j] == 0 or self.ids[i, j + 1] + 1 == 0:
            check = 1
        return check


class LeadingTrailingEdgeCurves:

    def __init__(self, n_1, n_2, ids, curve_counter):

        self.n_1 = n_1
        self.n_2 = n_2
        self.ids = ids
        self.curves = np.zeros((self.n_1 - 1, self.n_2))
        self.curve_counter = curve_counter
        self.curves, self.curve_counter = self.write_tcl()

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
                self.curve_counter += 1
                self.curves[i, 0] = self.curve_counter
        file.close()
        return self.curves, self.curve_counter


class MultipleCurves:

    def __init__(self, n_1, n_2, ids_1, ids_2, curve_counter):

        self.n_1 = n_1
        self.n_2 = n_2
        self.ids_1 = ids_1
        self.ids_2 = ids_2
        self.curves = np.zeros((self.n_1, self.n_2))
        self.curve_counter = curve_counter
        self.curves, self.curve_counter = self.write_tcl()
        self.reshape_curves()

    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, j], self.ids_2[i, j]))
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
                        cmd = "*createlist nodes 1 " + my_str
                        file.write(cmd)
                        file.write("\n*createvector 1 1 0 0\n*createvector 2 1 0 0"
                                   "\n*linecreatespline nodes 1 0 0 1 2\n")
                        self.curve_counter += 1
                        self.curves_indexing(i, j)
        file.close()
        return self.curves, self.curve_counter

    def curves_indexing(self, i, j):
        self.curves[i, j] = self.curve_counter

    def reshape_curves(self):
        pass


class SparAndSparCapCurves(MultipleCurves):
    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, j], self.ids_2[i + 1, j]))
        return my_list


class StringersInRibsCurves(MultipleCurves):
    def __init__(self, n_1, n_2, n_spars, n_stringers_per_sect,
                 ids_1, ids_2, curve_counter):

        self.n_1 = n_1
        self.n_2 = n_2
        self.ids_1 = ids_1
        self.ids_2 = ids_2
        self.curves = np.zeros((self.n_1, self.n_2))
        self.curve_counter = curve_counter
        self.curves, self.curve_counter = self.write_tcl()
        self.reshape_curves(n_spars, n_stringers_per_sect)

    def reshape_curves(self, n_spars, n_stringers_per_sect):
        self.curves = self.curves[..., np.newaxis]
        self.curves.shape = (self.n_1, n_spars - 1, n_stringers_per_sect)


class StringersCurves(StringersInRibsCurves):
    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, j], self.ids_2[i + 1, j]))
        return my_list

    def check_for_zeros(self, i, j):
        check = 0
        if self.ids_1[i, j] == 0 or self.ids_2[i + 1, j] == 0:
            check = 1
        return check

class CirclesForStringers:
    def __init__(self, n_1, n_2, n_spars, n_stringers_per_sect,
                 ids_1, curve_counter):
        self.n_1 = n_1
        self.n_2 = n_2
        self.ids_1 = ids_1
        self.curves = np.zeros((self.n_1, self.n_2))
        self.curve_counter = curve_counter
        self.curves, self.curve_counter = self.write_tcl()
        self.reshape_curves(n_spars, n_stringers_per_sect)

    def write_tcl(self):
        with open('Wing_Geometry_Generation.tcl', 'a+') as file:
            for i in range(0, self.n_1):
                for j in range(0, self.n_2):
                    cmd = '*createlist nodes 1 %.0f' % (self.ids_1[i, j])
                    file.write(cmd)
                    file.write("\n*createvector 1 0 1 0\n"
                               "*createcirclefromcenterradius 1 1 0.08 360 0\n")
                    self.curve_counter += 1
                    self.curves_indexing(i, j)
        file.close()
        return self.curves, self.curve_counter

    def curves_indexing(self, i, j):
        self.curves[i, j] = self.curve_counter

    def reshape_curves(self, n_spars, n_stringers_per_sect):
        self.curves = self.curves[..., np.newaxis]
        self.curves.shape = (self.n_1, n_spars - 1, n_stringers_per_sect)
