class MeshEquivalence:

    def __init__(self, group_1, group_2, tolerance, file):
        self.group_1 = group_1
        self.group_2 = group_2
        self.tolerance = tolerance

        self.write_tcl(file, tolerance)

    def write_tcl(self, file, tolerance):
        names_1 = ' '.join(f'"{w}"' for w in self.group_1)
        names_2 = ' '.join(f'"{w}"' for w in self.group_2)

        file.write('*createmark components 1 ' + names_1 + names_2)
        file.write('\n*equivalence components 1 %.3f 1 0 0 0\n' % tolerance)
