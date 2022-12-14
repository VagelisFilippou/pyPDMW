"""
A script for the geometry data extraction of the uCRM-9 wing.

Advices:
- You must have a Resources/uCRM_9/uCRM_9_Airfoil_Data/' path containing
the airfoil data

"""
import math
import numpy
from scipy import interpolate
from intersect import intersection
from read_oml import read_oml


class Airfoil:
    """
    Airfoil Class.

    Defines a class that contains all the necessary instance attributes and a
    method for reading, translating and rotating the airfoil's coordinates
    """

    def __init__(self, percent, x_origin, y_origin, z_origin, twist, chord):
        self.percent = percent
        self.X = x_origin
        self.Y = y_origin
        self.Z = z_origin
        self.twist = twist
        self.c = chord

    def read_airfoil(self):
        """
        It's a method for the extraction of airfoil's data and transformation.

        -------
        x, y, z: The coordinates after rotation, translation and scaling
        """
        airfoil_path = 'Resources/uCRM_9/uCRM_9_Airfoil_Data/' \
                       'uCRM-9_wr%.0f_profile.txt' % self.percent
        with open(airfoil_path, 'r') as infile:
            x_airfoil, z_airfoil = numpy.loadtxt(infile, unpack=True)
        infile.close()
        # Modify the TE of Lower curve to match the upper (sharp TE)
        x_airfoil[-1] = x_airfoil[0]
        z_airfoil[-1] = z_airfoil[0]
        # Rotate the coordinates of airfoil
        x = x_airfoil * math.cos(self.twist) - z_airfoil * math.sin(self.twist)
        z = z_airfoil * math.cos(self.twist) + x_airfoil * math.sin(self.twist)
        # Transform
        x = x * self.c + self.X
        y = self.Y
        z = z * self.c + self.Z
        return x, y, z


class UCRM:
    """
    uCRM_9 Class.

    It's a class that contains the coordinates of uCRM_9 wing.
    """

    def __init__(self):

        # Read the coordinates
        X, Y, Z, aoa, c = read_oml()
        # Appending airfoil instances to airfoil_list
        airfoil_list = []
        self.x = numpy.zeros((240, 21))
        self.y = numpy.zeros((240, 21))
        self.z = numpy.zeros((240, 21))
        self.chord = numpy.transpose(c)
        self.twist = numpy.transpose(aoa)
        # The percent of airfoils' Y coordinate
        Y_percent = [0, 10, 15, 20, 25, 30, 35, 37, 40, 45, 50,
                     55, 60, 65, 70, 75, 80, 85, 90, 95, 100]

        for i in range(0, 21):
            airfoil_list.append(Airfoil(Y_percent[i], X[i], Y[i], Z[i],
                                        aoa[i], c[i]))
            self.x[:, i], self.y[:, i], self.z[:, i] =\
                airfoil_list[i].read_airfoil()


class RibsOrientation:
    """
    Wing interpolation class.

    It's a class that makes the interpolation of desired Y
    positions to the uCRM_9 wing considering the inclination of ribs.
    """

    def __init__(self, derived_geometry, parameters):

        self.Y_vector = derived_geometry.Y_list
        self.n = len(self.Y_vector)
        spars_position = parameters.spars_position()
        self.Elastic_Axis_X = (spars_position[-1] + spars_position[0]) / 2
        self.X_origin = derived_geometry.Origin[:, 0]
        self.Rib_Sections_ID = derived_geometry.Rib_Sections_ID

        self.X = numpy.zeros((self.n, 240))
        self.Y = numpy.zeros((self.n, 240))
        self.Z = numpy.zeros((self.n, 240))
        self.chords = numpy.zeros((1, self.n))
        self.twist = numpy.zeros((1, self.n))
        self.Rib_line_x = numpy.zeros((self.n, 2))
        self.Rib_line_y = numpy.zeros((self.n, 2))
        self.Inclination = numpy.zeros((self.n, 0))
        # Fill the rest variables
        self.interpolate()

    def rib_intersection(self, Rib_line_x, Rib_line_y, Inclination, LE_x, LE_y,
                         TE_x, TE_y):
        """
        Parameters.

        ----------
        Rib_line_x : Array that contains the x coordinates of rib line.
        Rib_line_y : Array that contains the y coordinates of rib line.
        Inclination : Vector that contains the desired inclination.
        LE_x : Array that contains the x coordinates of LE.
        LE_y : Array that contains the y coordinates of LE.
        TE_x : Array that contains the x coordinates of TE.
        TE_y : Array that contains the y coordinates of TE.

        Returns
        -------
        Rib_x : Array that contains the x coordinates of rib at the LE and TE.
        Rib_y : Array that contains the y coordinates of rib at the LE and TE.
        Rib_line_Rotated_x : Array that contains the x coordinates of
        rotated rib line.
        Rib_line_Rotated_y : Array that contains the y coordinates of
        rotated rib line.
        """
        Rib_line_Rotated_x = numpy.zeros((self.n, 2))
        Rib_line_Rotated_y = numpy.zeros((self.n, 2))
        Rib_x = numpy.zeros((self.n, 2))
        Rib_y = numpy.zeros((self.n, 2))

        # Rotate the rib lines to have the desired inclination
        for i in range(0, self.n):
            for j in range(0, 2):
                # Move the center of rotation
                Rib_line_x[i, j] = Rib_line_x[i, j] - self.Elastic_Axis_X[0, i]
                Rib_line_y[i, j] = Rib_line_y[i, j] - self.Y_vector[i]
                # Rotate x and y
                Rib_line_Rotated_x[i, j] = Rib_line_x[i, j] * math.cos(Inclination[i])\
                    - Rib_line_y[i, j] * math.sin(Inclination[i])\
                    + self.Elastic_Axis_X[0, i]
                Rib_line_Rotated_y[i, j] = Rib_line_y[i, j] * math.cos(Inclination[i])\
                    + Rib_line_x[i, j] * math.sin(Inclination[i])\
                    + self.Y_vector[i]
                # Move the center of rotation
                Rib_line_x[i, j] = Rib_line_x[i, j] + self.Elastic_Axis_X[0, i]
                Rib_line_y[i, j] = Rib_line_y[i, j] + self.Y_vector[i]

        # Find the intersection with LE and TE
        for i in range(0, self.n):
            Rib_x[i, 0], Rib_y[i, 0] = intersection(LE_x, LE_y,
                                                    Rib_line_Rotated_x[i, :],
                                                    Rib_line_Rotated_y[i, :])
            Rib_x[i, 1], Rib_y[i, 1] = intersection(TE_x, TE_y,
                                                    Rib_line_Rotated_x[i, :],
                                                    Rib_line_Rotated_y[i, :])
        return Rib_x, Rib_y, Rib_line_Rotated_x, Rib_line_Rotated_y

    def interpolate(self):
        """
        It's the method that actually does the interpolation given the Y vector.

        Returns
        -------
        X : The matrix of x coordinates in the form (Airfoil Coord ID, Rib ID).
        Y : The matrix of y coordinates in the form (Airfoil Coord ID, Rib ID).
        Z : The matrix of z coordinates in the form (Airfoil Coord ID, Rib ID).

        """
        # Call the UCRM class in order to get the wing data
        Wing = UCRM()

        # Initialization of the desired arrays
        x_ = numpy.zeros((240, self.n))
        z_ = numpy.zeros((240, self.n))
        y_ = numpy.ones((240, self.n)) * self.Y_vector
        self.chords = numpy.zeros((1, self.n))
        self.twist = numpy.zeros((1, self.n))

        # Linear interpolation to find the coordinates at the desired Y
        for j in range(0, self.n):
            self.chords[0, j] = numpy.interp(y_[0, j], Wing.y[0, :],
                                             Wing.chord[0, :])
            self.twist[0, j] = numpy.interp(y_[0, j], Wing.y[0, :],
                                            Wing.twist[0, :])
            for i in range(0, 240):
                x_[i, j] = numpy.interp(self.Y_vector[j], Wing.y[i, :],
                                        Wing.x[i, :])
                z_[i, j] = numpy.interp(x_[i, j], Wing.x[i, :], Wing.z[i, :])

        # Calculation of the elastic axis as
        # the mean between front and rear wing box
        self.Elastic_Axis_X = self.Elastic_Axis_X * self.chords + self.X_origin

        # Calculation of the inclination of the elastic axis:
        # If you want the ribs to be normal to the elastic axis then:
        self.Inclination = - numpy.gradient(self.Elastic_Axis_X[0, :],
                                            self.Y_vector[:])

        # If you want the ribs to be at a specified angle then:
        # Inclination = - numpy.ones((self.n)) * math.radians(0)

        # Set the inclination of ribs before the kink and the last  one to zero
        for i in range(0, self.n):
            if i <= self.Rib_Sections_ID[1] - 1:
                self.Inclination[i] = 0
            elif i == self.Rib_Sections_ID[2] - 1:
                self.Inclination[i] = 0

        # Initialize the arrays that will help us
        # find the intersections of each rib
        Rib_line_x = numpy.zeros((self.n, 2))
        Rib_line_y = numpy.zeros((self.n, 2))
        LE_x = numpy.zeros((21, 1))
        LE_y = numpy.zeros((21, 1))
        TE_x = numpy.zeros((21, 1))
        TE_y = numpy.zeros((21, 1))

        # Set the coordinates of the non-rotated rib line
        for i in range(0, self.n):
            for j in range(0, 2):
                if j == 0:
                    Rib_line_x[i, j] = -10
                else:
                    Rib_line_x[i, j] = 30
                Rib_line_y[i, j] = self.Y_vector[i]

        # Set the coordinates of the LE and TE
        for i in range(0, 21):
            LE_x[i, 0] = Wing.x[119, i]
            LE_y[i, 0] = Wing.y[119, i]
            TE_x[i, 0] = Wing.x[0, i]
            TE_y[i, 0] = Wing.y[0, i]

        # Get the coordinates of the intersections for the 1st rotation
        Rib_x, Rib_y, _, _ = self.rib_intersection(
            Rib_line_x, Rib_line_y,
            self.Inclination, LE_x, LE_y, TE_x,
            TE_y)

        # Calculate the id of the first rib that intersects with the kink's rib
        for i in range(0, self.n):
            int_x, int_y = intersection(Rib_x[i, :], Rib_y[i, :],
                                        Rib_x[self.Rib_Sections_ID[1]
                                              - 1, :],
                                        Rib_y[self.Rib_Sections_ID[1]
                                              - 1, :])
            if len(int_x) == 0 and i > self.Rib_Sections_ID[1] - 1:
                print(int_x, int_y)
                idx = i
                break

        # Adjust the angle of the ribs between the first rib after the
        # intersection and the kink's rib
        New_Angles = numpy.linspace(self.Inclination[self.Rib_Sections_ID[1]
                                                     - 1],
                                    self.Inclination[idx + 4], idx + 4 -
                                    (self.Rib_Sections_ID[1] - 1))
        self.Inclination[self.Rib_Sections_ID[1] - 1: idx + 4] = New_Angles
        self.Inclination[- 2] = self.Inclination[- 2] / 2

        # Get the coordinates of the intersections for the 1st rotation

        Rib_x, Rib_y, self.Rib_line_x, self.Rib_line_y = self.rib_intersection(
            Rib_line_x, Rib_line_y,
            self.Inclination, LE_x, LE_y, TE_x,
            TE_y)
