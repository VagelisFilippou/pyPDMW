class AssemblyClass:
    def __init__(self, counter, name, components, file):
        self.id = counter
        self.name = name
        self.components = components

        self.write_tcl(file)

    def write_tcl(self, file):
        file.write(
            '*createentity assems name="'
            + self.name + '"\n')
        file.write(
            '*startnotehistorystate {Modified Components of assembly}\n')
        str_ids = ' '.join(map(str, self.components))
        cmd = '*setvalue assems id=%.0f components={comps ' % (self.id)
        file.write(cmd + str_ids + '}')
        file.write(
            '\n*endnotehistorystate {Modified Components of assembly}\n')


class ComponentClass:

    def __init__(self, counter, name, surfaces, index, mesh_size, file):
        self.id = counter
        self.name = name
        self.surfaces = surfaces.flatten()

        self.mesh_size = mesh_size

        self.write_tcl(index, file)

    def write_tcl(self, index, file):
        file.write('*createentity comps name="'
                   + self.name + '_%.0f"\n'
                   % (index + 1))
        file.write(
            '*startnotehistorystate {Moved surfaces into component "'
            + self.name + '_%.0f"}\n' % (index + 1))
        str_ids = ' '.join(map(str, self.surfaces[self.surfaces != 0]))
        file.write("*createmark surfaces 1 " + str_ids)
        file.write('\n*movemark surfaces 1 "'
                   + self.name + '_%.0f"\n'
                   % (index + 1))
        file.write('*endnotehistorystate {Moved surfaces into component "'
                   + self.name + '_%.0f"}\n'
                   % (index + 1))
        self.name = self.name + '_%.0f' % (index + 1)
