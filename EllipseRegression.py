import collections

import numpy as np
import matplotlib.pyplot as plt
import math


def fit_ellipse(points):
    # Step 1: Center the points
    points = np.array(points)
    mean = np.mean(points, axis=0)
    centered_points = points - mean

    # Step 2: Calculate the covariance matrix
    covariance_matrix = np.cov(centered_points, rowvar=False)

    # Step 3: Perform eigenvalue decomposition
    eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)

    # Step 4: Sort eigenvalues and eigenvectors in descending order
    order = eigenvalues.argsort()[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]

    # Step 5: Calculate the axes lengths (semi-major and semi-minor axes)
    major_axis_length = 2 * np.sqrt(eigenvalues[0])
    minor_axis_length = 2 * np.sqrt(eigenvalues[1])

    # Step 6: Determine the orientation of the ellipse (angle of rotation)
    angle = np.arctan2(eigenvectors[1, 0], eigenvectors[0, 0])

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

# # Example usage with random data points
# np.random.seed(0)
# # Create a set of points roughly forming an ellipse
# points = np.random.randn(200, 2)
# points[:, 0] = points[:, 0] * 3  # Stretch along x-axis
# points[:, 1] = points[:, 1] * 1.5  # Stretch along y-axis
# points = np.dot(points,
#                 np.array([[np.cos(np.pi / 4), -np.sin(np.pi / 4)], [np.sin(np.pi / 4), np.cos(np.pi / 4)]]))  # Rotate
#
# # Fit ellipse
# mean, major_axis_length, minor_axis_length, angle, eigenvectors = fit_ellipse(points)
#
# # Plot result
# plot_ellipse(mean, major_axis_length, minor_axis_length, angle)

# Explanation of the Code:
# fit_ellipse function:
#
# Step 1: Centers the points by subtracting the mean of the points.
# Step 2: Calculates the covariance matrix of the centered points.
# Step 3: Performs eigenvalue decomposition to get the eigenvalues and eigenvectors.
# Step 4: Sorts the eigenvalues and eigenvectors in descending order (this ensures the largest eigenvalue corresponds to the semi-major axis).
# Step 5: Calculates the lengths of the semi-major and semi-minor axes based on the eigenvalues.
# Step 6: Calculates the angle of rotation (orientation) of the ellipse from the first eigenvector.
# plot_ellipse function:
#
# Uses the parametric form of the ellipse to generate the points along the ellipse.
# Rotates and translates the ellipse to fit the data.
# Plots both the original points and the fitted ellipse using matplotlib.
# Example usage:
#
# Generates a set of random points forming an ellipse and applies the fit_ellipse and plot_ellipse functions to visualize the result.
# Result:
# When you run the code, it will display a plot with the point cloud (blue) and the fitted ellipse (red). The algorithm should fit the ellipse that best represents the data.
#
# Let me know if you'd like to adjust this for specific datasets or need any further explanation!
