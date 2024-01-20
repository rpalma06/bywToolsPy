import re
import sys
import Click

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


def extract_clicks(self, line: str):
    return []


def read_number_from_key(line: str, key: str, start=0):
    idx = line.find(key, start)

    if idx + len(key) < len(line):
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
    return None

