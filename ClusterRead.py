import psycopg2 as ps

import ClusterEllipse
import EllipseRegression

def main():
    connection = None
    cursor = None
    try:
        connection = ps.connect(database="clusters", user="postgres", password="admin", host="localhost", port=5432)
        if connection is not None:
            cursor = connection.cursor()
            if cursor is not None:
                cursor.execute("SELECT c.id, c.center_ra, c.center_dec, c.points FROM "
                               "cluster_comover_candidate_no_repeat_smalls s JOIN cluster_small_arcsec_no_repeat c ON "
                               "s.small_ra = c.center_ra and s.small_dec = c.center_dec")
                rows = cursor.fetchall()
                cluster_ellipses = []
                for row in rows:
                    cluster_id = row[0]
                    center_ra = row[1]
                    center_dec = row[2]
                    points_string = row[3]
                    if points_string is not None:
                        cluster_ellipse = ClusterEllipse.ClusterEllipse()
                        cluster_ellipse.id = cluster_id
                        cluster_ellipse.ra = center_ra
                        cluster_ellipse.dec = center_dec
                        coordinates_string = points_string.split("|")
                        for coordinate_string in coordinates_string:
                            if coordinate_string is not None:
                                axes = coordinates_string.split("$")
                                if axes is not None and len(axes) == 2:
                                    ra = float(axes[0])
                                    dec = float(axes[1])
                                    cluster_ellipse.add_point(ra, dec)
                                    ellipse_result = EllipseRegression.fit_ellipse(cluster_ellipse.get_point_matrix())
                                    cluster_ellipse.mean = ellipse_result[0]
                                    cluster_ellipse.major_axis_length = ellipse_result[1]
                                    cluster_ellipse.minor_axis_length = ellipse_result[2]
                                    cluster_ellipse.angle = ellipse_result[3]
                                    cluster_ellipse.eigenvectors = ellipse_result[4]


    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    main()
