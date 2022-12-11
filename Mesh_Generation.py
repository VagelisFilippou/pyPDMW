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
    def __init__(self, surfaces):
        self.mesh_properties = MeshProperties()
        self.write_tcl(surfaces)

    def write_tcl(self, surfaces):
        str_ids = ' '.join(map(str, surfaces))
        with open('Wing_Geometry_Generation.tcl', 'a+') as file:
            file.write(
                '*setedgedensitylinkwithaspectratio -1\n'
                '*elementorder 1\n'
                '*startnotehistorystate {Automesh surfaces}\n'
                '*createmark surfaces 1 ' + str_ids +
                '\n*interactiveremeshsurf 1 0.1 1 1 2 1 1\n')
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
