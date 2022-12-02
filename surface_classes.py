import numpy as np

class MultipleSurfacesThreeCurves:

    def __init__(self, n_1, n_2, ids_1, ids_2, ids_3,
                 surface_counter, component_counter, assembly_counter,
                 components_name):

        self.n_1 = n_1
        self.n_2 = n_2

        self.ids_1 = ids_1
        self.ids_2 = ids_2
        self.ids_3 = ids_3

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
                        self.ids_3[i, j]))
        return my_list

    def check_for_zeros(self, i, j):
        check = 0
        if self.ids_1[i, j] == 0:
            check = 1
        return check

    def write_tcl(self):
        with open('Wing_Geometry_Generation.tcl', 'a+') as file:
            for i in range(0, self.n_1):
                for j in range(0, self.n_2):
                    if self.check_for_zeros(i, j) != 1:
                        my_list = self.list_creation(i, j)
                        my_str = ' '.join(map(str, my_list))
                        cmd = "*surfacemode 4\n*createmark lines 1 " + my_str
                        file.write(cmd)
                        file.write("\n*surfacesplineonlinesloop 1 1 0 65\n")
                        self.surface_counter += 1
                        self.surfaces[i, j] = self.surface_counter
                self.component_counter += 1
                self.components[i, 0] = self.component_counter
                file.write('*createentity comps name="'
                           + self.components_name + '_%.0f"\n'
                           % (i + 1))
                file.write(
                    '*startnotehistorystate {Moved surfaces into component "'
                    + self.components_name + '_%.0f"}\n' % (i + 1))
                file.write('*createmark surfaces 1 %.0f-%.0f\n'
                           % (self.surfaces[i, 0], self.surfaces[i, return_first_zero(self.surfaces[i, :]) - 1]))
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

class MultipleSurfaces:
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

    def write_tcl(self):
        with open('Wing_Geometry_Generation.tcl', 'a+') as file:
            for i in range(0, self.n_1):
                for j in range(0, self.n_2):
                    my_list = self.list_creation(i, j)
                    my_str = ' '.join(map(str, my_list))
                    cmd = "*surfacemode 4\n*createmark lines 1 " + my_str
                    file.write(cmd)
                    file.write("\n*surfacesplineonlinesloop 1 1 0 65\n")
                    self.surface_counter += 1
                    self.surfaces[i, j] = self.surface_counter
                self.component_counter += 1
                self.components[i, 0] = self.component_counter
                file.write('*createentity comps name="'
                           + self.components_name + '_%.0f"\n'
                           % (i + 1))
                file.write(
                    '*startnotehistorystate {Moved surfaces into component "'
                    + self.components_name + '_%.0f"}\n' % (i + 1))
                file.write('*createmark surfaces 1 %.0f-%.0f\n'
                           % (self.surfaces[i, 0], self.surfaces[i, -1]))
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

class SingleSurfacesFourCurves:

    def __init__(self, n_1, ids_1, ids_2, ids_3, ids_4,
                 surface_counter, component_counter, assembly_counter,
                 components_name):

        self.n_1 = n_1

        self.ids_1 = ids_1
        self.ids_2 = ids_2
        self.ids_3 = ids_3
        self.ids_4 = ids_4

        self.surfaces = np.zeros((self.n_1, 1))
        self.components = np.zeros((self.n_1, 1))
        self.surface_counter = surface_counter
        self.component_counter = component_counter
        self.assembly_counter = assembly_counter
        self.components_name = components_name
        self.write_tcl()

    def list_creation(self, i):
        my_list = list((self.ids_1[i],
                        self.ids_2[i],
                        self.ids_3[i, 0],
                        self.ids_4[i, 0]))
        return my_list

    def write_tcl(self):
        with open('Wing_Geometry_Generation.tcl', 'a+') as file:
            for i in range(0, self.n_1):
                my_list = self.list_creation(i)
                my_str = ' '.join(map(str, my_list))
                cmd = "*surfacemode 4\n*createmark lines 1 " + my_str
                file.write(cmd)
                file.write("\n*surfacesplineonlinesloop 1 1 0 65\n")
                self.surface_counter += 1
                self.surfaces[i, 0] = self.surface_counter
                self.component_counter += 1
                self.components[i, 0] = self.component_counter
                file.write('*createentity comps name="'
                           + self.components_name + '_%.0f"\n'
                           % (i + 1))
                file.write(
                    '*startnotehistorystate {Moved surfaces into component "'
                    + self.components_name + '_%.0f"}\n' % (i + 1))
                file.write('*createmark surfaces 1 %.0f-%.0f\n'
                           % (self.surfaces[i, 0], self.surfaces[i, -1]))
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


class MainRibSurfaces(MultipleSurfaces):
    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, j],
                        self.ids_2[i, j],
                        self.ids_3[i, j],
                        self.ids_4[i, j + 1]))
        return my_list


class SparSurfaces(MultipleSurfaces):
    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, j],
                        self.ids_2[i, j],
                        self.ids_3[i, j],
                        self.ids_4[i + 1, j]))
        return my_list


class SkinSurfaces(MultipleSurfaces):
    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, j],
                        self.ids_2[i + 1, j],
                        self.ids_3[i, j + 1],
                        self.ids_4[i, j]))
        return my_list


class SparCapsSurfaces(MultipleSurfaces):
    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, j],
                        self.ids_2[i, j],
                        self.ids_3[i + 1, j],
                        self.ids_4[i, j]))
        return my_list


class LeftSideOfMainRibSurfaces(MultipleSurfaces):
    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, j, 0],
                        self.ids_2[i, j, 0],
                        self.ids_3[i, j],
                        self.ids_4[i, j, 0]))
        return my_list


class RightSideOfMainRibSurfaces(MultipleSurfaces):
    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, return_ith_from_zero(self.ids_1[i, :], 4)],
                        self.ids_2[i, return_ith_from_zero(self.ids_2[i, :], 4)],
                        self.ids_3[i, j + 1],
                        self.ids_4[i, j, -1]))
        return my_list


class LeftSideOfSkins(MultipleSurfaces):
    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, j, 0],
                        self.ids_2[i + 1, j, 0],
                        self.ids_3[i, j],
                        self.ids_4[i, j, 0]))
        return my_list
    # def list_creation(self, i, j):
    #     # print(return_zeros(self.ids_1[i, :]))
    #     if return_zeros(self.ids_1[i, :]) == return_zeros(self.ids_1[i + 1, :]):
    #         my_list = list((self.ids_1[i, 3],
    #                         self.ids_2[i + 1, 3],
    #                         self.ids_3[i, j],
    #                         self.ids_4[i, j, 0]))
    #     else:
    #         # space = int(abs(return_zeros(self.ids_1[i, :]) - return_zeros(self.ids_1[i - 1, :])))
    #         my_list = list((self.ids_1[i, 3],
    #                         self.ids_1[i, 3 + 1],
    #                         self.ids_2[i + 1, 3],
    #                         self.ids_3[i, j],
    #                         self.ids_4[i, j, 0]))
            # for k in range(0, space):
            #     my_list.append(self.ids_1[i, 3 + i])
        # my_list = list((self.ids_1[i, 3],
        #                 self.ids_2[i + 1, 3],
        #                 self.ids_3[i, j],
        #                 self.ids_4[i, j, 0]))
        # return my_list



class RightSideOfSkins(MultipleSurfaces):
    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, return_ith_from_zero(self.ids_1[i, :], 4)],
                        self.ids_2[i + 1, return_ith_from_zero(self.ids_2[i + 1, :], 4)],
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


class SingleSurfacesThreeCurves(SingleSurfacesFourCurves):

    def __init__(self, n_1, ids_1, ids_2, ids_3,
                 surface_counter, component_counter, assembly_counter,
                 components_name):

        self.n_1 = n_1

        self.ids_1 = ids_1
        self.ids_2 = ids_2
        self.ids_3 = ids_3

        self.surfaces = np.zeros((self.n_1, 1))
        self.components = np.zeros((self.n_1, 1))
        self.surface_counter = surface_counter
        self.component_counter = component_counter
        self.assembly_counter = assembly_counter
        self.components_name = components_name
        self.write_tcl()

    def list_creation(self, i):
        my_list = list((self.ids_1[i],
                        self.ids_2[i],
                        self.ids_3[i, 0],
                        ))
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


class CutRibHoles:
    def __init__(self, ids_1, ids_2, n_1, n_2):
        self.ids_1 = ids_1.astype(int)
        self.ids_2 = ids_2.astype(int)
        self.write_tcl(n_1, n_2)

    def list_creation_1(self, i, j):
        my_list = range(self.ids_1[i, j, 0],
                        self.ids_1[i, j, -1] + 1)
        return my_list

    def list_creation_2(self, i, j):
        my_list = range(self.ids_2[i, j, 0],
                        self.ids_2[i, j, -1] + 1)
        return my_list

    def write_tcl(self, n_1, n_2):
        with open('Wing_Geometry_Generation.tcl', 'a+') as file:
            for i in range(0, n_1):
                for j in range(0, n_2 - 1):
                    my_list = self.list_creation_1(i, j)
                    my_str = ' '.join(map(str, my_list))
                    cmd = "*createmark surfaces 1 " + my_str
                    my_list = self.list_creation_2(i, j)
                    my_str = ' '.join(map(str, my_list))
                    file.write(cmd)
                    file.write('\n*createmark lines 2 ' + my_str +
                               '\n*createvector 1 0 1 0\n'
                               '*surfacemarksplitwithlines 1 2 1 9 0\n'
                               'set surfslist [hm_latestentityid surfaces]\n'
                               '*deleteelementsmode 0\n'
                               '*createmark surfaces 1 surfsList\n'
                               '*deletemark surfaces 1\n')
        file.close()

class RibCaps(MultipleSurfacesThreeCurves):
    def list_creation(self, i, j):
        my_list = list((self.ids_1[i, j],
                        self.ids_2[i, j + 1],
                        self.ids_3[i, j]))
        return my_list

    def check_for_zeros(self, i, j):
        check = 0
        if self.ids_1[i, j] == 0 or self.ids_2[i, j + 1] == 0:
            check = 1
        return check

def return_zers(vec, id_from_zero):
    n_1 = len(vec)
    id_1 = 0
    for i in range(0, n_1):
        if vec[i] == 0:
            id_1 = i - id_from_zero
            break
        else:
            id_1 = - id_from_zero
    return id_1

def return_ith_from_zero(vec, id_from_zero):
    n_1 = len(vec)
    id_1 = 0
    for i in range(0, n_1):
        if vec[i] == 0:
            id_1 = i - id_from_zero
            break
        else:
            id_1 = - id_from_zero
    return id_1

def return_zeros(vec):
    n_1 = len(vec)
    id_1 = 0
    for i in range(0, n_1):
        if vec[i] == 0:
            id_1 += 1
    return id_1

def return_first_zero(vec):
    n_1 = len(vec)
    id_1 = 0
    for i in range(0, n_1):
        if vec[i] == 0:
            id_1 = i
            break
        else:
            pass
    return id_1