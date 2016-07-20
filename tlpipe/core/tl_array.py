"""Tianlai dish and cylinder array."""

import numpy as np
import aipy as ap

import constants as const


class DsihBeam(ap.fit.Beam2DGaussian):
    """Circular beam of a dish antenna."""

    def __init__(self, freqs, diameter=6.0):
        """Initialize the beam.

        Parameters
        ----------
        freqs : array like
            Frequencies in MHz.
        diameter : float, optional
            Diameter of the dish in m. Default is 6.0.

        """

        freqs = 1.0e-3 * np.array([freqs])  # in GHz
        lmbda = const.c / (1.0e9 * freqs) # in m
        xwidth = 1.22 * lmbda / diameter
        ywidth = xwidth
        ap.fit.Beam2DGaussian.__init__(self, freqs, xwidth, ywidth)


class CylinderBeam(ap.fit.Beam):
    """Beam of a cylinder feed."""

    def __init__(self, freqs, width=15.0, length=40.0):
        """Initialize the beam.

        Parameters
        ----------
        freqs : array like
            Frequencies in MHz.
        width : float, optional
            Cylinder width. Default is 15.0.
        length : float, optional
            Cylinder length. Default is 40.0.

        """

        freqs = 1.0e-3 * np.array([freqs])  # in GHz
        ap.fit.Beam.__init__(self, freqs)
        self.width = width
        self.length = length

    def response(self, xyz):
        """Beam response across active band for specified topocentric coordinates.

        This is just a simple beam model as the product of 2 sinc function.

        Parameters
        ----------
        xzy : array like
            Unit direction vector in topocentric coordinates (x=E, y=N, z=UP).
            `xyz` may be arrays of multiple coordinates.


        Returns
        -------
        Returns 'x' linear polarization (rotate pi/2 for 'y').

        """

        vec_n = np.array(xyz)
        vec_z = np.array([0.0, 0.0, 1.0]) # unit vector pointing to the zenith
        nz = np.dot(vec_n, vec_z)

        vec_u = np.array([1.0, 0.0, 0.0]) # unit vector pointing East in the ground-plane
        vec_v = np.array([0.0, 1.0, 0.0]) # unit vector pointing North in the ground-plane
        nu = np.dot(vec_n, vec_u)
        nv = np.dot(vec_n, vec_v)

        lmbda = const.c / (1.0e9 * self.freqs) # in m

        nz = np.where(nz<=0.0, 0.0, nz) # mask respose under horizon

        factor = 1.0e-60

        return np.sinc(self.width * nu / lmbda) * np.sinc(factor * nv / lmbda) * nz



if __name__ == '__main__':
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    plt.figure()
    xs = np.linspace(-1.0, 1.0, 2000)
    xz = np.array([ np.array([x, 0.0, (1.0-x**2)**0.5]) for x in xs ])
    x_ang = np.degrees(np.arctan2(xz[:, 2], xz[:, 0]))

    ys = np.linspace(-1.0, 1.0, 2000)
    yz = np.array([ np.array([0.0, y, (1.0-y**2)**0.5]) for y in ys ])
    y_ang = np.degrees(np.arctan2(yz[:, 2], yz[:, 1]))

    cyl_beam = CylinderBeam([750.0], 15.0, 40.0)
    x_resp = cyl_beam.response(xz)
    y_resp = cyl_beam.response(yz)

    x_inds = np.where(x_resp>=0.5)[1]
    x_ind1, x_ind2 = x_inds[0], x_inds[-1]
    y_inds = np.where(y_resp>=0.5)[1]
    y_ind1, y_ind2 = y_inds[0], y_inds[-1]

    print x_resp.shape
    print y_resp.shape
    print x_ang[x_ind1], x_ang[x_ind2]
    print y_ang[y_ind1], y_ang[y_ind2]

    plt.plot(x_ang, x_resp[0], 'r', label='East-West')
    # plt.axvline(x=x_ang[x_ind1], linewidth=0.5, color='r')
    # plt.axvline(x=x_ang[x_ind2], linewidth=0.5, color='r')
    plt.plot(y_ang, y_resp[0], 'g', label='North-South')
    plt.axvline(x=y_ang[y_ind1], linewidth=0.5, color='g')
    plt.axvline(x=y_ang[y_ind2], linewidth=0.5, color='g')
    plt.legend()
    plt.savefig('cy.png')
