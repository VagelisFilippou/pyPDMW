class AssemblyClass:
    def __init__(self, counter, name, components):
        self.id = counter
        self.name = name
        self.components = components

        self.write_tcl()

    def write_tcl(self):
        with open('Wing_Geometry_Generation.tcl', 'a+') as file:
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
        file.close()


class ComponentClass:

    def __init__(self, counter, name, surfaces, index):
        self.id = counter
        self.name = name
        self.surfaces = surfaces.flatten()

        self.write_tcl(index)

    def write_tcl(self, index):
        with open('Wing_Geometry_Generation.tcl', 'a+') as file:

            file.write('*createentity comps name="'
                       + self.name + '_%.0f"\n'
                       % (index + 1))
            file.write(
                '*startnotehistorystate {Moved surfaces into component "'
                + self.name + '_%.0f"}\n' % (index + 1))
            str_ids = ' '.join(map(str, self.surfaces))
            file.write("*createmark surfaces 1 " + str_ids)
            file.write('\n*movemark surfaces 1 "'
                       + self.name + '_%.0f"\n'
                       % (index + 1))
            file.write('*endnotehistorystate {Moved surfaces into component "'
                       + self.name + '_%.0f"}\n'
                       % (index + 1))
        file.close()
        self.name = self.name + '_%.0f' % (index + 1)