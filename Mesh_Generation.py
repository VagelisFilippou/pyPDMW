class MeshProperties:
    def __init__(self):
        self.shape_type = 2
        self.elem_type = 1
        self.alg_type = 0
        self.elem_size = 0  # Don't change it
        self.smooth_method = 1
        self.smooth_tol = 0.5
        self.size_control = 1
        self.skew_control = 1


class GenerateMesh:
    def __init__(self, list_of_components, file):
        self.mesh_properties = MeshProperties()
        self.list_of_components = list_of_components
        self.iterate_for_each_component(file)

    def iterate_for_each_component(self, file):
        for i in range(0, len(self.list_of_components)):
            self.write_tcl(self.list_of_components[i], file)

    def write_tcl(self, component, file):
        str_ids = ' '.join(map(str, component.surfaces))
        file.write(
            '*setedgedensitylinkwithaspectratio -1\n'
            '*elementorder 1\n'
            '*startnotehistorystate {Automesh surfaces}\n'
            '*createmark surfaces 1 ' + str_ids +
            '\n*interactiveremeshsurf 1 %.3f 1 1 2 1 1\n' %
            (component.mesh_size))
        for i in range(0, len(component.surfaces)):
            cmd = MeshPropertiesAssignment(i, self.mesh_properties)
            file.write(cmd)
        file.write(
            '*storemeshtodatabase 1\n'
            '*ameshclearsurface\n'
            '*endnotehistorystate {Automesh surfaces}\n')

class GenerateGlobalMesh:
    def __init__(self, surfaces, file):
        self.mesh_properties = MeshProperties()
        self.write_tcl(surfaces, file)

    def write_tcl(self, surfaces, file):
        str_ids = ' '.join(map(str, surfaces))
        file.write(
            '*setedgedensitylinkwithaspectratio -1\n'
            '*elementorder 1\n'
            '*startnotehistorystate {Automesh surfaces}\n'
            '*createmark surfaces 1 ' + str_ids +
            '\n*interactiveremeshsurf 1 0.2 1 1 2 1 1\n')
        for i in range(0, len(surfaces)):
            cmd = MeshPropertiesAssignment(i, self.mesh_properties)
            file.write(cmd)
        file.write(
            '*storemeshtodatabase 1\n'
            '*ameshclearsurface\n'
            '*endnotehistorystate {Automesh surfaces}\n')

def MeshPropertiesAssignment(index, mesh_properties):

    cmd = ('*set_meshfaceparams %.0f %.0f %.0f %.0f %.0f %.0f %.1f %.0f %.0f\n'
           '*automesh %.0f %.0f %.0f\n'
           % (index,
              mesh_properties.shape_type,
              mesh_properties.elem_type,
              mesh_properties.alg_type,
              mesh_properties.elem_size,
              mesh_properties.smooth_method,
              mesh_properties.smooth_tol,
              mesh_properties.size_control,
              mesh_properties.skew_control,
              index,
              mesh_properties.shape_type,
              mesh_properties.elem_type,)
           )
    return cmd
