from dataclasses import dataclass
from Coordinate import Coordinate


@dataclass
class ClusterEllipse:

    def __init__(self):
        self._id = 0
        self._ra = 0.0
        self._dec = 0.0
        self._points = []
        self._mean = 0.0
        self._major_axis_length = 0.0
        self._minor_axis_length = 0.0
        self._angle = 0.0
        self._eigenvectors = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, new_id):
        self._id = new_id

    @property
    def ra(self):
        return self._ra

    @ra.setter
    def ra(self, new_ra):
        self._ra = new_ra

    @property
    def dec(self):
        return self._dec

    @dec.setter
    def dec(self, new_dec):
        self._dec = new_dec

    @property
    def points(self):
        return self._points

    @property
    def mean(self):
        return self._mean

    @mean.setter
    def mean(self, new_mean):
        self._mean = new_mean

    @property
    def major_axis_length(self):
        return self._major_axis_length

    @major_axis_length.setter
    def major_axis_length(self, new_major_axis_length):
        self._major_axis_length = new_major_axis_length

    @property
    def minor_axis_length(self):
        return self._minor_axis_length

    @minor_axis_length.setter
    def minor_axis_length(self, new_minor_axis_length):
        self._minor_axis_length = new_minor_axis_length

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, new_angle):
        self._angle = new_angle

    @property
    def eigenvectors(self):
        return self._eigenvectors

    @eigenvectors.setter
    def eigenvectors(self, new_eigenvectors):
        self._eigenvectors = new_eigenvectors

    def add_point(self, ra, dec):
        return self._points.append(Coordinate.Coordinate(ra, dec))

    def get_point_matrix(self):
        point_matrix = []
        if self._points is not None:
            for point in self._points:
                point_matrix.append((point.ra, point.dec))
        return point_matrix
