import re
import sys

import Classification
import Click
import datetime

import Coordinate

FRAME_PREFIX = "\"\"frame\"\":"

TOOL_PREFIX = "\"\"tool\"\":"

X_PREFIX = "\"\"x\"\":"

Y_PREFIX = "\"\"y\"\":"

NATURAL_WIDTH_PREFIX = "\"\"naturalWidth\"\":"

NATURAL_HEIGHT_PREFIX = "\"\"naturalHeight\"\":"


def main():
    args = sys.argv[1:]


def read_candidates():
    path = "F:\\UCD\\candidates\\backyard-worlds-planet-9-classifications.1.5.24.csv"
    csv = open(path, "r")
    try:
        line = csv.readline()
    except OSError as err:
        print("OS error:", err)
    except ValueError:
        print("Could not convert data to an integer.")
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise


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
            except ValueError:
                pass
            except AttributeError:
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


def extract_sub_tile_center(line: str) -> Coordinate:
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
                 except ValueError:
                     pass
                 except AttributeError:
                     pass

     if (ra is not None) and (dec is not None):
         return Coordinate.Coordinate(ra, dec)
     else:
         return None
