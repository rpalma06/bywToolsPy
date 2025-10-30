import io
import math
import os
import sys
from typing import Any

import numpy as np
from sklearn.cluster._mean_shift import MeanShift
from scipy.stats import kurtosis
from statistics import mean
from numpy import ndarray, dtype


def get_clicks_coordinates(input_folder: str) -> ndarray[Any, dtype[float]]:
    """
    Gets the coordinates from a series of files containing the user clicks in a csv format
    @param input_folder: the folder containing the files with the clicks
    @return: a list of coordinates in an array ([ra, dec])
    """
    coordinate_list = []
    try:
        files = os.listdir(input_folder)
        csv = None
        count = 0
        for in_file_name in files:
            csv_file_name = input_folder + in_file_name
            line = ' '
            try:
                csv = open(csv_file_name, "r")
                while line is not None and len(line) > 0:
                    line = csv.readline()
                    if len(line) < 2:
                        continue
                    line_split = line[0:len(line) - 1].split(";")
                    try:
                        ra = float(line_split[len(line_split) - 2])
                        dec = float(line_split[len(line_split) - 1])
                    except:
                        continue
                    coordinate_list.append([ra, dec])
                    count += 1
                    if (count % 10000) == 0:
                        print(count)
                if csv is not None:
                    try:
                        csv.close()
                    except:
                        pass
            except OSError as err:
                print("OS error:", err)
            except Exception as err:
                print("Unexpected {err=}, {type(err)=}", err)
                raise
            finally:
                if csv is not None:
                    try:
                        csv.close()
                    except:
                        pass
    except OSError as err:
        print("OS error:", err)
    except ValueError as err:
        print("Could not convert data to an integer.", err)
    except Exception as err:
        print("Unexpected {err=}, {type(err)=}", err)
        raise
    return np.array(coordinate_list)


def init_region_array(region_array, ra_divisions: int = 360, dec_divisions: int = 180):
    """
    Initializes the array with coordinate regions
    @param region_array: the region array to initialize
    @param ra_divisions: number of divisions for ra values
    @param dec_divisions:  number of divisions for dec_values

    """
    for i in range(ra_divisions):
        region_array.append([])
        for j in range(dec_divisions):
            region_array[i].append([])


def store_by_region(clicks_coordinates: ndarray[Any, dtype[float]], region_folder: str, ra_divisions: int = 360,
                    dec_divisions: int = 180, bandwidth: float = 0.02):
    """
    Stores the list of coordinate by region.

    @param clicks_coordinates: list of coordinates in an array ([ra, dec])
    @param region_folder: the regions folder
    @param ra_divisions: number of division for ra
    @param dec_divisions: number of division for dec
    @param bandwidth: the cluster bandwidth
           (we overlap regions by the bandwidth so region-intersecting clusters are not lost)
    """
    region_array = []
    init_region_array(region_array, ra_divisions, dec_divisions)
    for coordinate in clicks_coordinates:
        ra = coordinate[0]
        dec = coordinate[1]
        dec_abs = dec + 90

        x_pos = int(math.floor(ra))
        y_pos = int(math.floor(dec_abs))
        region_array[x_pos % ra_divisions][y_pos % dec_divisions].append([ra, dec])

        x_upper_pos = int(math.floor(ra + bandwidth))
        x_lower_pos = int(math.floor(ra - bandwidth))
        y_upper_pos = int(math.floor(ra + bandwidth))
        y_lower_pos = int(math.floor(ra - bandwidth))

        if x_upper_pos > x_pos:
            region_array[(x_pos + 1) % ra_divisions][y_pos % dec_divisions].append([ra, dec])
            if y_upper_pos > y_pos:
                region_array[(x_pos + 1) % ra_divisions][(y_pos + 1) % dec_divisions].append([ra, dec])
            if y_lower_pos < y_pos:
                region_array[(x_pos + 1) % ra_divisions][(y_pos - 1) % dec_divisions].append([ra, dec])
        if x_lower_pos < x_pos:
            region_array[(x_pos - 1) % ra_divisions][y_pos % dec_divisions].append([ra, dec])
            if y_upper_pos > y_pos:
                region_array[(x_pos - 1) % ra_divisions][(y_pos + 1) % dec_divisions].append([ra, dec])
            if y_lower_pos < y_pos:
                region_array[(x_pos - 1) % ra_divisions][(y_pos - 1) % dec_divisions].append([ra, dec])
        if y_upper_pos > y_pos:
            region_array[x_pos % ra_divisions][(y_pos + 1) % dec_divisions].append([ra, dec])
        if y_lower_pos < y_pos:
            region_array[x_pos % ra_divisions][(y_pos - 1) % dec_divisions].append([ra, dec])

    for i in range(ra_divisions):
        for j in range(dec_divisions):
            if len(region_array[i][j]) > 0:
                file_name = region_folder + str(float(i)).replace(".", "_") + "__" + str(
                    float(j) - 90).replace(".", "_") + ".csv"
                output_file = None
                try:
                    output_file = open(file_name, "w")
                    for coord in region_array[i][j]:
                        line = str(coord[0]) + ";" + str(coord[1]) + "\n"
                        output_file.write(line)
                finally:
                    if output_file is not None:
                        try:
                            output_file.close()
                        except:
                            pass


def main():
    """
    Get the user clicks, sort them by regions and find cluster region by region
    Command line use:
    python GetClusters.py <click_files_folder> <clicks_region_folder> <cluster_file_path> <region_ra_divisions>
                           <region_dec_division> <cluster_detection_bandwidth>

    Without arguments, the command line would be like:
    python GetClusters.py ".\\results\\" ".\\regions\\" ".\\candidates\\clusters.csv" 360 180 0.02

    """
    args = sys.argv[1:]
    try:
        input_folder = ".\\results\\"
        region_folder = ".\\regions\\"
        clusters_file_path = ".\\candidates\\clusters.csv"
        ra_divisions = 360
        dec_divisions = 180
        bandwidth = 0.02
        clusters_file = None
        try:
            if len(args) > 0:
                input_folder = args[0]
            if len(args) > 1:
                region_folder = args[1]
            if len(args) > 2:
                clusters_file_path = args[2]
            if len(args) > 3:
                ra_divisions = type(int(args[3]))
            if len(args) > 4:
                dec_divisions = type(int(args[4]))
            if len(args) > 5:
                bandwidth = type(float(args[5]))
            clusters_file = open(clusters_file_path, "w")
            clusters_file.write("center_ra;center_dec;nb_points;q;kurtosis;mean_distance;points\n")
            clicks_coordinates = get_clicks_coordinates(input_folder)
            store_by_region(clicks_coordinates, region_folder, ra_divisions, dec_divisions, bandwidth)
            region_files = os.listdir(region_folder)
            region_files.sort()
            for region_file_name in region_files:
                print(region_file_name)
                region_file_path = region_folder + region_file_name
                region_file = None
                try:
                    region_file = open(region_file_path, "r")
                    line = ' '
                    points = []
                    while line is not None and len(line) > 0:
                        line = region_file.readline()
                        if len(line) == 0:
                            break
                        line_split = line[0:len(line) - 1].split(";")
                        points.append([float(line_split[0]), float(line_split[1])])

                    points_np_array = np.array(points)

                    # Bandwidth is in sexagesimal degrees
                    ms = MeanShift(bandwidth=bandwidth)
                    ms.fit(points_np_array)
                    labels = ms.labels_
                    cluster_centers = ms.cluster_centers_
                    labels_unique = np.unique(labels)
                    n_clusters_ = len(labels_unique)
                    clusters = []
                    for i in range(n_clusters_):
                        clusters.append([])
                    for i in range(len(labels)):
                        label = labels[i]
                        point = points[i]
                        clusters[label].append(point)
                    for i in range(len(clusters)):
                        cluster_points = clusters[i]
                        if len(cluster_points) < 5:
                            continue
                        cluster_center = cluster_centers[i]
                        distances = []
                        points_l = io.StringIO()
                        for cluster_point in cluster_points:
                            if points_l.tell() > 0:
                                points_l.write("|")
                            points_l.write(str(cluster_point[0]))
                            points_l.write("$")
                            points_l.write(str(cluster_point[1]))
                            x_difference = cluster_center[0] - cluster_point[0]
                            y_difference = cluster_center[1] - cluster_point[1]
                            distance = math.sqrt(x_difference * x_difference + y_difference * y_difference)
                            distances.append(distance)
                        mean_distance = mean(distances)
                        m4 = kurtosis(distances, fisher=True, bias=False)
                        cluster_line = io.StringIO()
                        cluster_line.write(str(cluster_center[0]))
                        cluster_line.write(";")
                        cluster_line.write(str(cluster_center[1]))
                        cluster_line.write(";")
                        cluster_line.write(str(len(cluster_points)))
                        cluster_line.write(";")
                        cluster_line.write(str(m4 / mean_distance))
                        cluster_line.write(";")
                        cluster_line.write(str(m4))
                        cluster_line.write(";")
                        cluster_line.write(str(mean_distance))
                        cluster_line.write(";")
                        cluster_line.write(points_l.getvalue())
                        cluster_line.write("\n")
                        clusters_file.write(cluster_line.getvalue())
                finally:
                    if region_file is not None:
                        try:
                            region_file.close()
                        except:
                            pass
        finally:
            if clusters_file is not None:
                try:
                    clusters_file.close()
                except:
                    pass

    except Exception as err:
        print("Unexpected {err=}, {type(err)=}", err)
        raise


if __name__ == "__main__":
    main()
