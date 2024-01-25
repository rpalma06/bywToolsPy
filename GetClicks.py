import math
import re
import sys
import datetime
import shutil

from astropy.coordinates import SkyCoord


import Classification
import Click
import Coordinate
import io
import os

from astropy.io import fits
from astropy.wcs import WCS
from astropy.wcs import utils

FRAME_PREFIX = "\"\"frame\"\":"

TOOL_PREFIX = "\"\"tool\"\":"

X_PREFIX = "\"\"x\"\":"

Y_PREFIX = "\"\"y\"\":"

NATURAL_WIDTH_PREFIX = "\"\"naturalwidth\"\":"

NATURAL_HEIGHT_PREFIX = "\"\"naturalheight\"\":"


def main():

    args = sys.argv[1:]
    try:
        input_folder = "F:\\UCD\\candidates\\input\\"
        output_filename = "c:\\UCD\\candidates\\"
        wcs_filename = "F:\\UCD\\candidates\\astrom-atlas.fits"
        try:
            if len(args) > 0:
                input_folder = args[0]
            if len(args) > 1:
                output_filename = args[1]
            if len(args) > 2:
                wcs_filename = args[2]
        except:
            pass
        hdu_list = fits.open(wcs_filename)
        data = hdu_list[1].data
        global_wcs = WCS(hdu_list[1].header, fobj=hdu_list)
        tile_list = []
        origin_list = []
        for row in data:
            w = WCS(naxis=2)

            w.wcs.cd = row['CD']

            w.wcs.crpix = row['CRPIX']
            w.wcs.crval = row["CRVAL"]
            w.wcs.ctype = row["CTYPE"]
            w.wcs.latpole = row["LATPOLE"]
            w.wcs.lonpole = row["LONGPOLE"]
            tile_list.append(w)
            origin_list.append(row["CDELT"][0])
    finally:
        hdu_list.close()

    process_candidates(global_wcs, tile_list, origin_list, input_folder, output_filename)


def get_wcs_tiles(wcs_path: str) -> list[WCS]:
    hdu_list = None
    try:
        hdu_list = fits.open(wcs_path)
        data = hdu_list[1].data
        tile_list = []
        origin_list = []
        for row in data:
            naxis_array = [int(row["NAXIS"][0]), int(row["NAXIS"][1])]
            naxis = len(row["NAXIS"])
            w = WCS(naxis=2)

            w.wcs.cd = row['CD']
            # w.wcs.cdelt = row['CDELT']
            w.wcs.crpix = row['CRPIX']
            w.wcs.crval = row["CRVAL"]
            w.wcs.ctype = row["CTYPE"]
            w.wcs.latpole = row["LATPOLE"]
            w.wcs.lonpole = row["LONGPOLE"]
            tile_list.append(w)
            origin_list.append(row["CDELT"][0])
    finally:
        if hdu_list is not None:
            hdu_list.close()
    return tile_list


def process_candidates(original_wcs: WCS, tile_list: list, origin_list: list, input_folder: str, output_path: str):
    #input_path = "F:\\UCD\\candidates\\backyard-worlds-planet-9-classifications.csv"
    files = os.listdir(input_folder)
    out_prefix = "clicks_ra_dec"
    out = None
    csv = None
    count = 0
    file_suffix = None
    out_file_name = ''
    if not input_folder.endswith(os.sep):
        input_folder = input_folder + os.sep

    try:
        for in_file_name in files:
            line = ' '
            try:
                csv_file_name = input_folder + in_file_name
                csv = open(csv_file_name, mode="r", encoding="UTF-8")
                print(in_file_name)
                if not output_path.endswith(os.sep):
                    output_path = output_path + os.sep

                try:
                    while line is not None and len(line) > 0:
                        line = csv.readline().lower()
                        if count % 1000 == 0:
                            print(count)
                        count += 1
                        classification = extract_classification_data(line)
                        clicks = extract_clicks(line)
                        sub_tile_center = extract_sub_tile_center(line)
                        tile_number = extract_tile_number(line)

                        if classification is not None and clicks is not None and len(clicks) > 0 and len(
                                clicks) <= 20 and sub_tile_center is not None and tile_number is not None:
                            common = io.StringIO()
                            common.write(str(classification.classification_id))
                            common.write(";")
                            common.write(classification.user_name)
                            common.write(";")
                            common.write(classification.user_id)
                            common.write(";")
                            common.write(classification.user_ip)
                            common.write(";")
                            common.write(classification.workflow_id)
                            common.write(";")
                            common.write(classification.workflow_name)
                            common.write(";")
                            common.write(classification.workflow_version)
                            common.write(";")

                            if classification.started_at is not None:
                                started_at_string = datetime.datetime.strftime(classification.started_at,
                                                                               "%Y-%m-%d %H:%M:%S") + " UTC"
                                new_file_suffix = "_" + started_at_string[0:7]
                                if file_suffix != new_file_suffix:
                                    old_out_file_name = out_file_name
                                    out_file_name = out_prefix + new_file_suffix + ".csv"

                                    file_suffix = new_file_suffix
                                    if out is not None:
                                        out.close()
                                        shutil.move(output_path + old_out_file_name,
                                                    "F:\\UCD\\candidates\\results\\" + old_out_file_name)
                                    out = open(output_path + out_file_name, "w")
                                    out.write(
                                        "classification_id;user_name;user_id;user_ip;workflow_id;workflow_name;workflow_version;started_at;gold_standard;expert;subject_id;tile_number;tile_center_ra;tile_center_dec;click_frame;click_tool;click_x;click_y;ra;dec\n")
                                common.write(started_at_string)
                                common.write(";")
                            common.write(classification.gold_standard)
                            common.write(";")
                            common.write(classification.expert)
                            common.write(";")
                            common.write(str(classification.subject_id))
                            common.write(";")
                            common.write(str(tile_number))
                            common.write(";")
                            common.write(str(sub_tile_center.ra))
                            common.write(";")
                            common.write(str(sub_tile_center.dec))
                            common.write(";")
                            no_click_line = common.getvalue()
                            for click in clicks:
                                x, y = convert_zoo_to_subtile(click)
                                ll_x, ll_y = get_sub_tile_lower_left(tile_list, origin_list, tile_number,
                                                                     sub_tile_center.ra, sub_tile_center.dec)
                                if (ll_x is None) or (ll_y is None):
                                    continue
                                final_x = ll_x + x
                                final_y = ll_y + y
                                origin = origin_list[tile_number]
                                world = utils.pixel_to_skycoord(final_x + origin, final_y + origin, tile_list[tile_number],
                                                                origin, "wcs")
                                ra = world.ra.value
                                dec = world.dec.value
                                click_sb = io.StringIO()
                                click_sb.write(no_click_line)
                                click_sb.write(str(click.frame))
                                click_sb.write(";")
                                click_sb.write(str(click.tool))
                                click_sb.write(";")
                                click_sb.write(str(click.x))
                                click_sb.write(";")
                                click_sb.write(str(click.y))
                                click_sb.write(";")
                                click_sb.write(str(ra))
                                click_sb.write(";")
                                click_sb.write(str(dec))
                                click_sb.write("\n")
                                out_line = click_sb.getvalue()
                                out.write(out_line)

                except OSError as err:
                    print("OS error:", err)
                except ValueError as err:
                    print("Could not convert data to an integer.", err)
                except Exception as err:
                    print(f"Unexpected {err=}, {type(err)=}")
                    raise

            finally:
                if csv is not None:
                    csv.close()

    finally:
        if csv is not None:
            csv.close()
        if out is not None:
            out.close()

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
         ra_idx = line_aux.find("r.a.=")
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
    tn_idx = line.find("tile number\"\":\"\"")
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


def convert_zoo_to_subtile(click: Click) -> (float, float):
    x = (click.x - 20.0) * 0.5
    y = 256.0 - 0.5 * click.y

    return x, y


def get_sub_tile_lower_left(wcs_list: list[WCS], origin: list[int], tile_number: int, ra_center: float, dec_center: float) -> (float, float):
    sky_coordinates = SkyCoord(ra=ra_center, dec=dec_center, frame="icrs", unit="deg")
    pixel = utils.skycoord_to_pixel(sky_coordinates, wcs_list[tile_number], origin[tile_number], "wcs")
    pos_horizontal = math.floor((round(pixel[0].item(0))/128.0 - 1) * 0.5)
    pos_vertical = math.floor((round(pixel[1].item(0))/128.0 - 1) * 0.5)
    if (pos_horizontal < 0) or (pos_horizontal > 7) or (pos_vertical < 0) or (pos_vertical > 7):
        return None, None
    ll_x = 256 * pos_horizontal
    ll_y = 256 * pos_vertical
    return ll_x, ll_y

if __name__ == "__main__":
    main()