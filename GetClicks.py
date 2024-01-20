import re
import sys
import Click

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
        columns = line.split(",")
    except OSError as err:
        print("OS error:", err)
    except ValueError:
        print("Could not convert data to an integer.")
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise


def extract_clicks(line: str):
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


def read_number_from_key(line: str, key: str, start=0):
    idx = line.find(key, start)

    if (idx >= 0) and (idx + len(key) < len(line)):
        key_aux = line[idx + len(key):]
        comma_idx = key_aux.find(',')
        bracket_idx = key_aux.find('}')
        end_idx = -1
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

