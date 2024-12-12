This is a code package used to extract Backyard Worlds Planet 9 user clicks and detect click clusters. Before you start, you need:

1. A folder "input" containing the files with Backyard Worlds Planet 9 clicks. The algorithm expects that the entries in the file are chronologically in order.
2. A folder "work" for intermediate files.
3. A folder "results" to store the click result files. Each file contains the clicks of one month.
4. A folder "regions" to store the clicks by sub-regions.
5. The file containing the atlas FITS sub-tiles.


# HOW TO EXTRACT CLICKS

Execute the file GetClicks.py:

```python GetClicks.py <click_files_input_folder> <work_folder> <result_folder> <result_file_name_prefix> <wcs_file_path>```

or without arguments:

```python GetClicks.py```

This would be equivalent to:

```python GetClicks.py ".\\input\\" ".\\work\\" ".\\results\\" "clicks_ra_dec" ".\\fits\\astrom-atlas.fits"```

The program will generate CSV files with the user clicks in the results folder. The file will contain the following columns:   

- ***classification_id***: classification id.
- ***user_name***: user_name.
- ***user_id***: user id.
- ***user_ip***: user IP address.
- ***workflow_id***: workflow id.
- ***workflow_name***: workflow name.
- ***workflow_version***: workflow version.
- ***started_at***: classification start timestamp.
- ***gold_standard***: Is gold standard?
- ***expert***: Is expert?
- ***subject_id***: subject id.
- ***tile_number***: tile number.
- ***tile_center_ra***, ***tile_center_dec***: tile center.
- ***click_frame***: frame clicked (0, 1, 2, 3). 
- ***click_tool***: click tool id.
- ***click_x***, ***click_y***: click pixel coordinates.
- ***ra***, ***dec***: click coordinates.

# HOW TO DETECT CLUSTERS

In order to detect the clusters, you need first to execute the previous step. 

Then execute the file GetClusters.py:

```python GetClusters.py <click_files_folder> <clicks_region_folder> <cluster_file_path> <region_ra_divisions> <region_dec_division> <cluster_detection_bandwidth>```

or

```python GetClusters.py```

This would be equivalent to:

```python GetClusters.py ".\\results\\" ".\\regions\\" ".\\candidates\\clusters.csv" 360 180 0.02```

For instance, this configuration generates regions of 1 degree and calculates clusters with a bandwidth of 7.2 arcseconds (0.02 degrees).

The program will generate a CSV file with the clusters. The file will contain the following columns:   

Columns of file ***_clusters.csv_***.

- ***center_ra***, ***center_dec***: Cluster center coordinates.
- ***nb_points***: number of points (coordinates) in the cluster.
- ***q***: ranking coefficient (kurtosis / mean_distance)
- ***kurtosis***: kurtosis of the distances between the cluster center and each one of the cluster points
- ***mean_distance***: mean of the distances between the cluster center and each one of the cluster points
- ***points***: list of points (coordinates). '|' separates the points from each other. '$' separates the R.A., in first position, from dec, in second position.  