class MeshEquivalence:

    def __init__(self, group_1, group_2, tolerance, file):
        self.group_1 = group_1
        self.group_2 = group_2
        self.tolerance = tolerance

*createmark components 1 "Comp_1" "Comp_2" "Comp_3" 
*equivalence components 1 0.01 1 0 0 0
