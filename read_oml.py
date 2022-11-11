"""
A script for the OML calculation of the uCRM-9 wing.

Advices:
- You must have a 'Resources/uCRM_9/uCRM_9_Coord.txt' path containing the
the coordinates that I have calculate for the leading and trailing edge

"""
import math
import numpy


def read_oml():
    """
    It's a function for retrieving the origins, calculation of chord and twist.

    -------
    x_origin, y_origin, z_origin: The origin of each airfoil's LE
    twist: The twist of each airfoil
    chord: The chord of each airfoil
    """
    airfoil_path = 'Resources/uCRM_9/uCRM_9_Coord.txt'  # Must have!!!!

    with open(airfoil_path, 'r') as infile:
        ignore, id_x, id_y, id_z = numpy.loadtxt(infile, unpack=True)

    # Distinguish the LE and TE coordinates
    front = numpy.dstack((id_x, id_y, id_z)).squeeze()[0:21, :]
    rear = numpy.dstack((id_x, id_y, id_z)).squeeze()[21:42, :]

    # Initialization of matrices
    chord = numpy.zeros((21, 1))
    twist = numpy.zeros((21, 1))
    xinit = numpy.zeros((21, 1))
    zinit = numpy.zeros((21, 1))

    for i in range(0, 21):
        chord[i, 0] = math.sqrt((front[i, 2] - rear[i, 2]) ** 2 +
                                (front[i, 0] - rear[i, 0]) ** 2)
        twist[i, 0] = - math.atan(-(front[i, 2] - rear[i, 2]) /
                                  (front[i, 0] - rear[i, 0]))
        d = chord[i, 0] * 0.25 * math.cos(twist[i, 0])
        dx = chord[i, 0] * 0.25 - d
        dz = chord[i, 0] * 0.25 * math.sin(twist[i, 0])
        zinit[i, 0] = front[i, 2] - dz
        xinit[i, 0] = front[i, 0] + dx

    z_origin = zinit - zinit[0]
    x_origin = xinit - xinit[0]
    y_origin = front[:, 1]
    return x_origin, y_origin, z_origin, twist, chord
