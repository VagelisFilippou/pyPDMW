# Script for nodal coordinates export
proc exportNodeCoords args {
    set dat [open "nodes.txt" w+]
    *createmarkpanel nodes 1 "Select points:"
	#*createmark nodes 1 1 2 3 4
	foreach nodeId [hm_getmark nodes 1] {
		set x [hm_getentityvalue nodes $nodeId x 0]
		set y [hm_getentityvalue nodes $nodeId y 0]
		set z [hm_getentityvalue nodes $nodeId z 0]
		*tagcreate nodes $nodeId [format "(%.1f  %.1f  %.1f)" $x $y $z] "N$nodeId" 2
		puts $dat [format "%.0f %.8f  %.8f  %.8f" $nodeId $x $y $z]
	}
	*clearmark nodes 1
    close $dat;
}
exportNodeCoords