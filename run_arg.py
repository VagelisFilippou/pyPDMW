"""Script that feeds the desired .tcl file to HyperMesh."""

import subprocess
import os.path


def check_path():
    """
    It's a function that checks the existing path and returns desired paths.

    -------
    path : Path of the .tcl script
    hm_loc : Path of HyperMesh GUI
    hm_batch : Path of HyperMesh batch

    """
    path = "C:/Users/efilippo/Documents"
    log = os.path.isdir(path)
    if log is True:
        # Location in Lab
        hm_loc = "C:/Program Files/Altair/2021.2/hwdesktop/hw/bin/win64/"\
            "hw.exe /clientconfig hwfepre.dat"
        hm_batch = "C:/Program Files/Altair/2021.2/hwdesktop/hm/bin/win64/"\
            "hmbatch.exe"

    else:
        # Location of HyperMesh in the System (Vagelis PC)
        hm_loc = "C:/Program Files/Altair/2019/hm/bin/win64/hmopengl.exe"
        path = "C:/Users/Evangelos Filippou/PhD_Projects"
        hm_batch = "C:/Program Files/Altair/2019/hm/bin/win64/hmbatch.exe"
    return path, hm_loc, hm_batch


def run_argument(tcl_script):
    """
    It's a function that constructs the argument to run the tcl script.

    Parameters
    ----------
    tcl_script : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    path, hm_loc, hm_batch = check_path()
    tcl_script = path + tcl_script
    arg = hm_loc + " -tcl " + tcl_script
    subprocess.call(arg)
