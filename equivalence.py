class MeshEquivalence:

    def __init__(self, tolerance, file, *groups):
        self.groups = []
        for group in groups:
            self.groups += group

        self.tolerance = tolerance

        self.write_tcl(file, tolerance)

    def write_tcl(self, file, tolerance):
        names_1 = ' '.join(f'"{w}"' for w in self.groups)

        file.write('*createmark components 1 ' + names_1)
        file.write('\n*equivalence components 1 %.3f 1 0 0 0\n' % tolerance)
