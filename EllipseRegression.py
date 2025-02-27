import collections

import numpy as np
import matplotlib.pyplot as plt
import scipy
import math


def fit_ellipse(points , confidence):

    points = np.array(points)
    mean = np.mean(points, axis=0)
    centered_points = points - mean

    covariance_matrix = np.cov(centered_points, rowvar=False)

    eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)

    chi2_99 = scipy.stats.chi2.ppf(confidence, (len(points) - 1) * (len(points[0]) - 1))

    major_axis_length = np.sqrt(eigenvalues[0] * chi2_99)
    minor_axis_length = np.sqrt(eigenvalues[1] * chi2_99)
    if major_axis_length < minor_axis_length:
        aux = minor_axis_length
        minor_axis_length = major_axis_length
        major_axis_length = aux

    angle =  math.atan2(covariance_matrix[0, 1], eigenvalues[0] - covariance_matrix[0, 0])

    return mean, major_axis_length, minor_axis_length, angle, eigenvectors


def plot_ellipse(points, mean: float, major_axis_length: float, minor_axis_length: float, angle: float) -> object:
    # Step 7: Create a parametric representation of the ellipse
    t = np.linspace(0, 2 * np.pi, 100)
    cos_t = np.cos(t)
    sin_t = np.sin(t)

    # Parametric form of the ellipse
    ellipse_x = major_axis_length * cos_t
    ellipse_y = minor_axis_length * sin_t

    radian_angle = angle  # angle * math.pi / 180.0

    # Rotate the ellipse based on the angle
    rotation_matrix = np.array(
        [[np.cos(radian_angle), -np.sin(radian_angle)], [np.sin(radian_angle), np.cos(radian_angle)]])
    ellipse_coords = np.dot(np.vstack((ellipse_x, ellipse_y)).T, rotation_matrix)

    # Translate ellipse to the mean center
    ellipse_coords += mean

    # Plot the points and the fitted ellipse
    ras = []
    decs = []
    for point in points:
        ras.append(point[0])
        decs.append(point[1])
    plt.scatter(np.array(ras), np.array(decs), color='blue', label='Data points')
    plt.plot(ellipse_coords[:, 0], ellipse_coords[:, 1], color='red', label='Fitted ellipse')
    plt.gca().set_aspect('equal', adjustable='box')
    #plt.legend()
    plt.show()





