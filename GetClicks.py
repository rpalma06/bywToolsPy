import re
import sys
import datetime

import numpy as np

import Classification
import Click
import Coordinate


from astropy.io import fits
from astropy.wcs import WCS

FRAME_PREFIX = "\"\"frame\"\":"

TOOL_PREFIX = "\"\"tool\"\":"

X_PREFIX = "\"\"x\"\":"

Y_PREFIX = "\"\"y\"\":"

NATURAL_WIDTH_PREFIX = "\"\"naturalWidth\"\":"

NATURAL_HEIGHT_PREFIX = "\"\"naturalHeight\"\":"


def main():
    args = sys.argv[1:]
    wcs = None
    try:
        hdu_list = fits.open("F:\\UCD\\candidates\\astrom-atlas.fits")
        hdu_list_info = hdu_list.info()
        header = hdu_list[0].header
        data = hdu_list[1].data
        tile_list = []
        for row in data:
            naxis_array = [int(row["NAXIS"][0]), int(row["NAXIS"][1])]
            w = WCS(naxis=len(row["NAXIS"]))
            w.wcs.cd = row['CD']
            #w.wcs.cdelt = row['CDELT']
            w.wcs.crpix = row['CRPIX']
            w.wcs.crval = row["CRVAL"]
            w.wcs.ctype = row["CTYPE"]
            w.wcs.latpole = row["LATPOLE"]
            tile_list.append(w)
    finally:
        hdu_list.close()

    read_candidates(tile_list)





def read_candidates(tile_list: list):
    path = "F:\\UCD\\candidates\\backyard-worlds-planet-9-classifications.1.5.24.csv"
    csv = open(path, mode="r", encoding="UTF-8")
    try:
        header = csv.readline()
        line = ''
        count = 0
        while line is not None and count < 12000:
            line = csv.readline()
            classification_data = extract_classification_data(line)
            clicks = extract_clicks(line)
            sub_tile_center = extract_sub_tile_center(line)
            tile_number = extract_tile_number(line)
            if classification_data is not None and clicks is not None and len(clicks) > 0 and sub_tile_center is not None and tile_number is not None:
                for click in clicks:
                    pix = [[click.x, click.y]]
                    world = tile_list[tile_number].wcs_pix2world(pix, 1.0)
                    h = 0
            count += 1
            if count % 1000 == 0:
                print(count)

    except OSError as err:
        print("OS error:", err)
    except ValueError as err:
        print("Could not convert data to an integer.", err)
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise
    except:
        h = 0
    finally:
        csv.close()

def extract_clicks(line: str) -> list[Click.Click]:
    line_aux = line
    max_idx = 0
    next_click = 0
    clicks = []
    while True:
        x, next_idx = read_number_from_key(line_aux, X_PREFIX, next_click)
        if next_idx < 0:
            break
        max_idx = max(max_idx, next_idx)
        y, next_idx = read_number_from_key(line_aux, Y_PREFIX, next_click)
        if next_idx < 0:
            break
        max_idx = max(max_idx, next_idx)
        frame, next_idx = read_number_from_key(line_aux, FRAME_PREFIX, next_click)
        if next_idx < 0:
            break
        max_idx = max(max_idx, next_idx)
        tool, next_idx = read_number_from_key(line_aux, TOOL_PREFIX, next_click)
        if next_idx < 0:
            break
        max_idx = max(max_idx, next_idx)
        if next_idx < 0:
            break
        next_click = max_idx+1

        if (x is not None) and (y is not None) and (frame is not None) and (tool is not None):
            click = Click.Click(int(frame), int(tool), float(x), float(y))
            clicks.append(click)
    return clicks


def read_number_from_key(line: str, key: str, start=0) -> (str | None,int):
    idx = line.find(key, start)

    if (idx >= 0) and (idx + len(key) < len(line)):
        key_aux = line[idx + len(key):]
        comma_idx = key_aux.find(',')
        bracket_idx = key_aux.find('}')
        if comma_idx < 0:
            if bracket_idx < 0:
                end_idx = -1
            else:
                end_idx = bracket_idx
        else:
            if bracket_idx < 0:
                end_idx = comma_idx
            else:
                end_idx = min(bracket_idx, comma_idx)
        next_key = idx + len(key) + end_idx
        if end_idx > 0:
            number_string = key_aux[0:end_idx]
            try:
                return re.search(r"[+-]?\d+(\.\d+)?", number_string).group(), next_key
            except ValueError | AttributeError:
                pass
    return None, -1


def extract_classification_data(line: str) -> Classification.Classification | None:
    columns = line.split(",")

    if columns is None:
        return None

    classification_id = None
    user_name = ""
    user_id = ""
    user_ip = ""
    workflow_id = ""
    workflow_name = ""
    workflow_version = ""
    started_at = None
    gold_standard = ""
    expert = ""
    subject_id = None
    if len(columns) > 0:
        try:
            classification_id = int(columns[0])
        except ValueError:
            pass
    if len(columns) > 1:
        user_name = columns[1]
    if len(columns) > 2:
        user_id = columns[2]
    if len(columns) > 3:
        user_ip = columns[3]
    if len(columns) > 4:
        workflow_id = columns[4]
    if len(columns) > 5:
        workflow_name = columns[5]
    if len(columns) > 6:
        workflow_version = columns[6]
    if len(columns) > 7:
        # e.g.: 2017-01-06 02:02:46 UTC
        created_at_string = columns[7]
        try:
            started_at = datetime.datetime.strptime(created_at_string, "%Y-%m-%d %H:%M:%S %Z")
        except:
            pass
    if len(columns) > 8:
        gold_standard = columns[8]
    if len(columns) > 9:
        expert = columns[9]
    try:
        subject_id = int(columns[len(columns) - 1])
    except ValueError:
        pass
    return Classification.Classification(classification_id, user_name, user_id, user_ip, workflow_id, workflow_name,
                                         workflow_version, started_at, gold_standard, expert, subject_id)


def extract_sub_tile_center(line: str) -> Coordinate.Coordinate | None :
     ra = None
     dec = None
     line_aux = line
     sc_idx = line_aux.find("subtile center")
     if (sc_idx >= 0) and (sc_idx + 14 < len(line_aux)) :
         line_aux = line_aux[sc_idx + 14:]
         ra_idx = line_aux.find("R.A.=")
         dec_idx = line_aux.find("dec=")
         if (ra_idx >= 0) and (dec_idx >= 0):
             ra_string = line_aux[ra_idx + 5:]
             quotes_idx = ra_string.find("\"\"")
             if (quotes_idx >= 0) and (quotes_idx > ra_idx) and (quotes_idx > dec_idx):
                 ra_string = ra_string[0: dec_idx - ra_idx - 5]
                 dec_string = line_aux[dec_idx + 4: ra_idx + 5 + quotes_idx]
                 ra = None
                 dec = None
                 try:
                    ra = float(ra_string)
                    dec = float(dec_string)
                 except ValueError | AttributeError:
                     pass

     if (ra is not None) and (dec is not None):
         return Coordinate.Coordinate(ra, dec)
     else:
         return None


def extract_tile_number(line: str) -> int | None:
    tn_idx = line.find("Tile Number\"\":\"\"")
    if tn_idx >= 0:
        line_aux = line[tn_idx + 16:]
        end_idx = line_aux.find("\"\"")
        if end_idx >= 0:
            line_aux = line_aux[0: end_idx]
            try:
                return int(line_aux)
            except ValueError | AttributeError:
                pass
    return None


if __name__ == "__main__":
    main()