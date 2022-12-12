import numpy as np


class MultipleSurfacesThreeCurves:

    def __init__(self, n_1, n_2, ids_1, ids_2, ids_3, surface_counter, file):

        self.n_1 = n_1
        self.n_2 = n_2

        self.ids_1 = ids_1
        self.ids_2 = ids_2
        self.ids_3 = ids_3

        self.surfaces = np.zeros((self.n_1, self.n_2))

        self.surface_counter = surface_counter

        self.write_tcl(file)

    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, j],
                        self.ids_2[i, j],
                        self.ids_3[i, j]))
        return my_list

    def write_tcl(self, file):
        for i in range(0, self.n_1):
            for j in range(0, self.n_2):
                my_list = self.list_creation(i, j)
                my_str = ' '.join(map(str, my_list))
                cmd = "*surfacemode 4\n*createmark lines 1 " + my_str
                file.write(cmd)
                file.write("\n*surfacesplineonlinesloop 1 1 0 65\n")
                self.surface_counter += 1
                self.surfaces[i, j] = self.surface_counter


class MultipleSurfacesFourCurves(MultipleSurfacesThreeCurves):
    def __init__(self, n_1, n_2, ids_1, ids_2, ids_3, ids_4, surface_counter,
                 file):

        self.n_1 = n_1
        self.n_2 = n_2

        self.ids_1 = ids_1
        self.ids_2 = ids_2
        self.ids_3 = ids_3
        self.ids_4 = ids_4

        self.surfaces = np.zeros((self.n_1, self.n_2))
        self.surface_counter = surface_counter

        self.write_tcl(file)

    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, j],
                        self.ids_2[i, j],
                        self.ids_3[i, j],
                        self.ids_4[i, j]))
        return my_list


class SingleSurfacesFourCurves:

    def __init__(self, n_1, ids_1, ids_2, ids_3, ids_4, surface_counter, file):

        self.n_1 = n_1

        self.ids_1 = ids_1
        self.ids_2 = ids_2
        self.ids_3 = ids_3
        self.ids_4 = ids_4

        self.surfaces = np.zeros((self.n_1, 1))
        self.surface_counter = surface_counter

        self.write_tcl(file)

    def list_creation(self, i):
        my_list = list((self.ids_1[i],
                        self.ids_2[i],
                        self.ids_3[i, 0],
                        self.ids_4[i, 0]))
        return my_list

    def write_tcl(self, file):
        for i in range(0, self.n_1):
            my_list = self.list_creation(i)
            my_str = ' '.join(map(str, my_list))
            cmd = "*surfacemode 4\n*createmark lines 1 " + my_str
            file.write(cmd)
            file.write("\n*surfacesplineonlinesloop 1 1 0 65\n")
            self.surface_counter += 1
            self.surfaces[i, 0] = self.surface_counter


class SingleSurfacesThreeCurves(SingleSurfacesFourCurves):

    def __init__(self, n_1, ids_1, ids_2, ids_3, surface_counter, file):

        self.n_1 = n_1

        self.ids_1 = ids_1
        self.ids_2 = ids_2
        self.ids_3 = ids_3

        self.surfaces = np.zeros((self.n_1, 1))
        self.components = np.zeros((self.n_1, 1))
        self.surface_counter = surface_counter

        self.write_tcl(file)

    def list_creation(self, i):
        my_list = list((self.ids_1[i],
                        self.ids_2[i],
                        self.ids_3[i, 0],
                        ))
        return my_list


class MainRibSurfaces(MultipleSurfacesFourCurves):
    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, j],
                        self.ids_2[i, j],
                        self.ids_3[i, j],
                        self.ids_4[i, j + 1]))
        return my_list


class SparSurfaces(MultipleSurfacesFourCurves):
    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, j],
                        self.ids_2[i, j],
                        self.ids_3[i, j],
                        self.ids_4[i + 1, j]))
        return my_list


class SkinSurfaces(MultipleSurfacesFourCurves):
    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, j],
                        self.ids_2[i + 1, j],
                        self.ids_3[i, j + 1],
                        self.ids_4[i, j]))
        return my_list


class SparCapsSurfaces(MultipleSurfacesFourCurves):
    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, j],
                        self.ids_2[i, j],
                        self.ids_3[i + 1, j],
                        self.ids_4[i, j]))
        return my_list


class LeftSideOfMainRibSurfaces(MultipleSurfacesFourCurves):
    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, j, 0],
                        self.ids_2[i, j, 0],
                        self.ids_3[i, j],
                        self.ids_4[i, j, 0]))
        return my_list


class RightSideOfMainRibSurfaces(MultipleSurfacesFourCurves):
    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, j, -1],
                        self.ids_2[i, j, -1],
                        self.ids_3[i, j + 1],
                        self.ids_4[i, j, -1]))
        return my_list


class LeftSideOfSkins(MultipleSurfacesFourCurves):
    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, j, 0],
                        self.ids_2[i + 1, j, 0],
                        self.ids_3[i, j],
                        self.ids_4[i, j, 0]))
        return my_list


class RightSideOfSkins(MultipleSurfacesFourCurves):
    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, j, -1],
                        self.ids_2[i + 1, j, -1],
                        self.ids_3[i, j + 1],
                        self.ids_4[i, j, -1]))
        return my_list


class FrontSkins(SingleSurfacesFourCurves):

    def list_creation(self, i):
        my_list = list((self.ids_1[i],
                        self.ids_2[i + 1],
                        self.ids_3[i, 0],
                        self.ids_4[i, 0]))
        return my_list


class RearSkins(SingleSurfacesFourCurves):

    def list_creation(self, i):
        my_list = list((self.ids_1[i],
                        self.ids_2[i + 1],
                        self.ids_3[i, -1],
                        self.ids_4[i, 0]))
        return my_list


class FrontRib(SingleSurfacesThreeCurves):
    pass


class RearRib(SingleSurfacesThreeCurves):
    def list_creation(self, i):
        my_list = list((self.ids_1[i],
                        self.ids_2[i],
                        self.ids_3[i, -1],
                        ))
        return my_list


class RibCaps(MultipleSurfacesThreeCurves):
    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, j],
                        self.ids_2[i, j + 1],
                        self.ids_3[i, j]))
        return my_list
