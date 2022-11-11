"""Function that deletes some files from the directory."""

import os


def delete_file(file_path):
    """
    It's a function that determines if a directory exists and deletes it.

    Parameters
    ----------
    file_path : The desired directory.

    Returns
    -------
    None.

    """
    if os.path.isfile(file_path):
        os.remove(file_path)
        print("File "+file_path+" has been deleted")
    else:
        print("File "+file_path+" does not exist")


def delete_files():
    """
    It's a function that deletes some specified files that aint useful.

    Returns
    -------
    None.

    """
    delete_file('Wing_Geometry_Generation.tcl')
    delete_file('HM_Files/command1.tcl')
    delete_file('HM_Files/wing.hm')
    delete_file('batchmesher_config_2019.cfg')
    delete_file('batchmesher_config.cfg')
    delete_file('command1.tcl')
    delete_file('command2.tcl')
    delete_file('hmmenu.set')
