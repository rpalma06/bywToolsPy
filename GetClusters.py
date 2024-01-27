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


def init_region_array(region_array):
    for i in range(360):
        region_array.append([])
        for j in range(180):
            region_array[i].append([])


def store_by_region(clicks_coordinates: ndarray[Any, dtype[float]]):
    region_array = []
    init_region_array(region_array)
    for coordinate in clicks_coordinates:
        ra = coordinate[0]
        dec = coordinate[1]
        dec_abs = dec + 90

        x_pos = int(math.floor(ra))
        y_pos = int(math.floor(dec_abs))
        region_array[x_pos % 360][y_pos % 180].append([ra, dec])

        x_upper_pos = int(math.floor(ra + 0.02))
        x_lower_pos = int(math.floor(ra - 0.02))
        y_upper_pos = int(math.floor(ra + 0.02))
        y_lower_pos = int(math.floor(ra - 0.02))

        if x_upper_pos > x_pos:
            region_array[(x_pos + 1) % 360][y_pos % 180].append([ra, dec])
            if y_upper_pos > y_pos:
                region_array[(x_pos + 1) % 360][(y_pos + 1) % 180].append([ra, dec])
            if y_lower_pos < y_pos:
                region_array[(x_pos + 1) % 360][(y_pos - 1) % 180].append([ra, dec])
        if x_lower_pos < x_pos:
            region_array[(x_pos - 1) % 360][y_pos % 180].append([ra, dec])
            if y_upper_pos > y_pos:
                region_array[(x_pos - 1) % 360][(y_pos + 1) % 180].append([ra, dec])
            if y_lower_pos < y_pos:
                region_array[(x_pos - 1) % 360][(y_pos - 1) % 180].append([ra, dec])
        if y_upper_pos > y_pos:
            region_array[x_pos % 360][(y_pos + 1) % 180].append([ra, dec])
        if y_lower_pos > y_pos:
            region_array[x_pos % 360][(y_pos - 1) % 180].append([ra, dec])

    for i in range(360):
        for j in range(180):
            if len(region_array[i][j]) > 0:
                file_name = "F:\\UCD\\candidates\\regions\\" + str(float(i)).replace(".", "_") + "__" + str(float(j)-90).replace(".", "_") + ".csv"
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
    args = sys.argv[1:]
    try:
        input_folder = "F:\\UCD\\candidates\\results\\"
        region_folder = "F:\\UCD\\candidates\\regions\\"
        clusters_file_path = "F:\\UCD\\candidates\\clusters.csv"
        clusters_file = None
        try:
            clusters_file = open(clusters_file_path, "w")
            clusters_file.write("center_ra;center_dec;nb_points;Q;kurtosis;mean_distance;points\n")
            if len(args) > 0:
                input_folder = args[0]
            if len(args) > 1:
                region_folder = args[1]
            if len(args) > 2:
                clusters_file_path = args[2]
            #clicks_coordinates = get_clicks_coordinates(input_folder)
            #store_by_region(clicks_coordinates)
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
                    ms = MeanShift(bandwidth=0.02)
                    fit_result = ms.fit(points_np_array)
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
                            distance = math.sqrt(x_difference*x_difference + y_difference*y_difference)
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
                        cluster_line.write(str(m4/mean_distance))
                        cluster_line.write(";")
                        cluster_line.write(str(m4))
                        cluster_line.write(";")
                        cluster_line.write(str(mean_distance))
                        cluster_line.write(";")
                        cluster_line.write(points_l.getvalue())
                        cluster_line.write("\n")
                        clusters_file.write(cluster_line.getvalue())
                    h = 0
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
