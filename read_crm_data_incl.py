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
        x, y, z, aoa, c = read_oml()
        # Appending airfoil instances to airfoil_list
        airfoil_list = []
        self.x = numpy.zeros((240, 21))
        self.y = numpy.zeros((240, 21))
        self.z = numpy.zeros((240, 21))
        self.chord = numpy.transpose(c)
        self.twist = numpy.transpose(aoa)
        # The percent of airfoils' Y coordinate
        y_percent = [0, 10, 15, 20, 25, 30, 35, 37, 40, 45, 50,
                     55, 60, 65, 70, 75, 80, 85, 90, 95, 100]

        for i in range(0, 21):
            airfoil_list.append(Airfoil(y_percent[i], x[i], y[i], z[i],
                                        aoa[i], c[i]))
            self.x[:, i], self.y[:, i], self.z[:, i] =\
                airfoil_list[i].read_airfoil()


class RibsInclined:
    """
    wing interpolation class.

    It's a class that makes the interpolation of desired Y
    positions to the uCRM_9 wing considering the inclination of ribs.
    """

    def __init__(self, derived_geometry, parameters):

        self.Y_vector = derived_geometry.Y_list
        self.n = len(self.Y_vector)
        spars_position = parameters.spars_position()
        self.Elastic_Axis_X = (spars_position[-1] + spars_position[0]) / 2
        self.X_origin = derived_geometry.Origin[:, :, 0]
        self.Rib_Sections_ID = derived_geometry.Rib_Sections_ID

        self.X = numpy.zeros((3, self.n, 240))
        self.Y = numpy.zeros((3, self.n, 240))
        self.Z = numpy.zeros((3, self.n, 240))
        self.chords = numpy.zeros((3, 1, self.n))
        self.twist = numpy.zeros((3, 1, self.n))
        self.rib_line_x = numpy.zeros((3, self.n, 2))
        self.rib_line_y = numpy.zeros((3, self.n, 2))
        self.inclination = numpy.zeros((3, self.n))
        # Fill the rest variables
        self.interpolate()

    def rib_intersection(self, rib_line_x, rib_line_y, inclination, le_x, le_y,
                         te_x, te_y):
        """
        Parameters.

        ----------
        rib_line_x : Array that contains the x coordinates of rib line.
        rib_line_y : Array that contains the y coordinates of rib line.
        inclination : Vector that contains the desired inclination.
        le_x : Array that contains the x coordinates of LE.
        le_y : Array that contains the y coordinates of LE.
        te_x : Array that contains the x coordinates of TE.
        te_y : Array that contains the y coordinates of TE.

        Returns
        -------
        rib_x : Array that contains the x coordinates of rib at the LE and TE.
        rib_y : Array that contains the y coordinates of rib at the LE and TE.
        rib_line_rotated_x : Array that contains the x coordinates of
        rotated rib line.
        rib_line_rotated_y : Array that contains the y coordinates of
        rotated rib line.
        """
        rib_line_rotated_x = numpy.zeros((3, self.n, 2))
        rib_line_rotated_y = numpy.zeros((3, self.n, 2))
        rib_x = numpy.zeros((3, self.n, 2))
        rib_y = numpy.zeros((3, self.n, 2))

        # Rotate the rib lines to have the desired inclination
        for i in range(0, self.n):
            for j in range(0, 2):
                for k in range(0, 3):
                    # Move the center of rotation
                    rib_line_x[k, i, j] = rib_line_x[k, i, j] - self.Elastic_Axis_X[k, i]
                    rib_line_y[k, i, j] = rib_line_y[k, i, j] - self.Y_vector[i, k]
                    # Rotate x and y
                    rib_line_rotated_x[k, i, j] = rib_line_x[k, i, j] * math.cos(inclination[k, i])\
                        - rib_line_y[k, i, j] * math.sin(inclination[k, i])\
                        + self.Elastic_Axis_X[k, i]
                    rib_line_rotated_y[k, i, j] = rib_line_y[k, i, j] * math.cos(inclination[k, i])\
                        + rib_line_x[k, i, j] * math.sin(inclination[k, i])\
                        + self.Y_vector[i, k]
                    # Move the center of rotation
                    rib_line_x[k, i, j] = rib_line_x[k, i, j] + self.Elastic_Axis_X[k, i]
                    rib_line_y[k, i, j] = rib_line_y[k, i, j] + self.Y_vector[i, k]

        # Find the intersection with LE and TE
        for i in range(0, self.n):
            for k in range(0, 3):
                x_0, y_0 =\
                    intersection(le_x, le_y,
                                 rib_line_rotated_x[k, i, :],
                                 rib_line_rotated_y[k, i, :])
                x_1, y_1 =\
                    intersection(te_x, te_y,
                                 rib_line_rotated_x[k, i, :],
                                 rib_line_rotated_y[k, i, :])

                if len(x_0) == 0:
                    pass
                else:
                    rib_x[k, i, 0] = x_0[0]
                    rib_y[k, i, 0] = y_0[0]

                if len(x_1) == 0:
                    pass
                else:
                    rib_x[k, i, 1] = x_1[0]
                    rib_y[k, i, 1] = y_1[0]

        return rib_x, rib_y, rib_line_rotated_x, rib_line_rotated_y

    def interpolate(self):
        """
        It's the method that actually does the interpolation given the Y vector.

        Returns
        -------
        X : The matrix of x coordinates in the form (Airfoil Coord ID, Rib ID).
        Y : The matrix of y coordinates in the form (Airfoil Coord ID, Rib ID).
        Z : The matrix of z coordinates in the form (Airfoil Coord ID, Rib ID).

        """
        # Call the U-CRM class in order to get the wing data
        wing = UCRM()

        # Initialization of the desired arrays
        x_ = numpy.zeros((3, 240, self.n))
        z_ = numpy.zeros((3, 240, self.n))
        y_ = numpy.zeros((3, 240, self.n))

        for i in range(0, 3):
            y_[i, :, :] = numpy.ones((240, self.n)) * self.Y_vector[:, i]

        self.chords = numpy.zeros((3, self.n))
        self.twist = numpy.zeros((3, self.n))

        # Linear interpolation to find the coordinates at the desired Y
        for j in range(0, self.n):
            self.chords[:, j] = numpy.interp(y_[:, 0, j], wing.y[0, :],
                                             wing.chord[0, :])
            self.twist[:, j] = numpy.interp(y_[:, 0, j], wing.y[0, :],
                                            wing.twist[0, :])
            for i in range(0, 240):
                x_[:, i, j] = numpy.interp(self.Y_vector[j, :], wing.y[i, :],
                                           wing.x[i, :])
                z_[:, i, j] = numpy.interp(x_[:, i, j], wing.x[i, :],
                                           wing.z[i, :])

        # Calculation of the elastic axis as
        # the mean between front and rear wing box
        self.Elastic_Axis_X = self.Elastic_Axis_X * self.chords + self.X_origin

        # Calculation of the inclination of the elastic axis:
        # If you want the ribs to be normal to the elastic axis then:
        inclination = - numpy.gradient(self.Elastic_Axis_X[0, :],
                                       self.Y_vector[:, 0])

        # If you want the ribs to be at a specified angle then:
        # inclination = - numpy.ones((self.n)) * math.radians(0)

        # Set the inclination of ribs before the kink and the last  one to zero
        for i in range(0, self.n):
            if i <= self.Rib_Sections_ID[1] - 1:
                inclination[i] = 0
            elif i == self.Rib_Sections_ID[2] - 1:
                inclination[i] = 0
        for i in range(0, 3):
            self.inclination[i, :] = numpy.transpose(inclination)

        # Initialize the arrays that will help us
        # find the intersections of each rib
        rib_line_x = numpy.zeros((3, self.n, 2))
        rib_line_y = numpy.zeros((3, self.n, 2))
        le_x = numpy.zeros((21, 1))
        le_y = numpy.zeros((21, 1))
        te_x = numpy.zeros((21, 1))
        te_y = numpy.zeros((21, 1))

        # Set the coordinates of the non-rotated rib line
        for i in range(0, self.n):
            for j in range(0, 2):
                if j == 0:
                    rib_line_x[:, i, j] = -10
                else:
                    rib_line_x[:, i, j] = 30
                rib_line_y[:, i, j] = self.Y_vector[i, :]

        # Set the coordinates of the LE and TE
        for i in range(0, 21):
            le_x[i, 0] = wing.x[119, i]
            le_y[i, 0] = wing.y[119, i]
            te_x[i, 0] = wing.x[0, i]
            te_y[i, 0] = wing.y[0, i]

        # Get the coordinates of the intersections for the 1st rotation
        rib_x, rib_y, _, _ = self.rib_intersection(
            rib_line_x, rib_line_y,
            self.inclination, le_x, le_y, te_x,
            te_y)

        # Calculate the id of the first rib that intersects with the kink's rib
        idx = 0
        for i in range(0, self.n):
            int_x, int_y =\
                intersection(rib_x[0, i, :], rib_y[0, i, :],
                             rib_x[0, self.Rib_Sections_ID[1] - 1, :],
                             rib_y[0, self.Rib_Sections_ID[1] - 1, :])
            if len(int_x) == 0 and i > self.Rib_Sections_ID[1] - 1:
                print(int_x, int_y)
                idx = i
                break

        # Adjust the angle of the ribs between the first rib after the
        # intersection and the kink's rib
        new_angles =\
            numpy.linspace(self.inclination[0, self.Rib_Sections_ID[1] - 1],
                           self.inclination[0, idx + 4], idx + 4 -
                           (self.Rib_Sections_ID[1] - 1))
        self.inclination[:, self.Rib_Sections_ID[1] - 1: idx + 4] =\
            new_angles
        self.inclination[:, - 2] = self.inclination[0, - 2] / 2

        # Get the coordinates of the intersections for the 1st rotation

        rib_x, rib_y, self.rib_line_x, self.rib_line_y = self.rib_intersection(
            rib_line_x, rib_line_y,
            self.inclination, le_x, le_y, te_x,
            te_y)

        # Define the arrays for the coordinates of the rotated ribs n_points
        # must be equal to the those of the database (120 for each curve)
        n_points = 120
        x_new_all = numpy.zeros((3, self.n, n_points))
        y_new_all = numpy.zeros((3, self.n, n_points))

        # Use linear interpolation to find the coordinates of the lin-spaced x
        for i in range(0, self.n):
            for k in range(0, 3):
                x = [rib_x[k, i, 0], rib_x[k, i, 1]]
                y = [rib_y[k, i, 0], rib_y[k, i, 1]]
                f = interpolate.interp1d(x, y)
                x_new_all[k, i, :] = numpy.linspace(rib_x[k, i, 0], rib_x[k, i, 1], n_points)
                y_new_all[k, i, :] = f(x_new_all[k, i, :])

        self.X = numpy.zeros((3, self.n, 2 * n_points))
        self.Y = numpy.zeros((3, self.n, 2 * n_points))
        self.Z = numpy.zeros((3, self.n, 2 * n_points))
        w_list = [0, 0.03, - 0.03]
        for k in range(0, 3):
            # Now concatenate the values
            x_new = numpy.concatenate(x_new_all[k, :, :])
            y_new = numpy.concatenate(y_new_all[k, :, :])
            # Concatenate the known coordinates in upper and lower arrays
            x_upper = numpy.concatenate(x_[k, 0:119, :])
            y_upper = numpy.concatenate(y_[k, 0:119, :])
            z_upper = numpy.concatenate(z_[k, 0:119, :])
            x_lower = numpy.concatenate(x_[k, 120:239, :])
            y_lower = numpy.concatenate(y_[k, 120:239, :])
            z_lower = numpy.concatenate(z_[k, 120:239, :])

            # Define the request array that contains the XY pairs where we want
            # to find the Z
            request = numpy.transpose(numpy.array([x_new, y_new]))

            # Find the desired data for the upper points with griddata function
            points_upper = numpy.transpose(numpy.array([x_upper, y_upper]))
            values_upper = numpy.transpose(z_upper)
            Z_upper = interpolate.griddata(points_upper, values_upper, request)

            # Find the desired data for the lower points with griddata function
            points_lower = numpy.transpose(numpy.array([x_lower, y_lower]))
            values_lower = numpy.transpose(z_lower)
            Z_lower = interpolate.griddata(points_lower, values_lower, request)

            # Now reshape to an array form
            X = x_new.reshape(len(self.Y_vector), n_points)
            Y = y_new.reshape(len(self.Y_vector), n_points)
            Z_upper = Z_upper.reshape(len(self.Y_vector), n_points)
            Z_lower = Z_lower.reshape(len(self.Y_vector), n_points)

            # Construct the total arrays
            self.X[k, :, :] = numpy.concatenate((numpy.flip(X, 1), X), axis=1)
            self.Y[k, :, :] = numpy.concatenate((numpy.flip(Y, 1), Y), axis=1)
            self.Z[k, :, :] = numpy.concatenate((numpy.flip(Z_upper, 1), Z_lower), axis=1)

            # Replace the XYZ values of the straight ribs with the non-interpolated
            self.X[k, 0: self.Rib_Sections_ID[1], :] = numpy.transpose(
                x_[k, :, 0: self.Rib_Sections_ID[1]])
            self.Y[k, 0: self.Rib_Sections_ID[1], :] = numpy.transpose(
                y_[k, :, 0: self.Rib_Sections_ID[1]])
            self.Z[k, 0: self.Rib_Sections_ID[1], :] = numpy.transpose(
                z_[k, :, 0: self.Rib_Sections_ID[1]])

            self.X[k, - 1, :] = numpy.transpose(wing.x[:, - 1])
            self.Y[k, - 1, :] = numpy.transpose(wing.y[:, - 1]) + w_list[k]
            self.Z[k, - 1, :] = numpy.transpose(wing.z[:, - 1])

            # Sharp TE
            self.Z[k, :, 0] = self.Z[k, :, -1]
