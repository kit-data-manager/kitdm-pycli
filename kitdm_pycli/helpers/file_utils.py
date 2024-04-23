import json
import sys
import os


def check_json_file(path, contained_keys=None):
    """
    Helper function to read and validate a content information metadata document. Currently, the validation is quite
    naive so be aware, that the server may still respond with BAD_REQUEST if the metadata contains errors not
    tested here.

    :param path: The path to a local json file.
    :param contained_keys: A list of keys of which at least one is expected in the json file.
    :return: The file content as string or None, if the file was not found or the metadata is invalid.
    """

    result = None
    try:
        # read file as string
        with open(path) as f:
            contents = f.read()

        # convert metadata string to json for format check
        data = json.loads(str(contents))
        if contained_keys and len(contained_keys) > 0:
            for key in contained_keys:
                if key in data:
                    result = contents
                    break
        else:
            # no further check
            result = contents
    except FileNotFoundError as e:
        print("Metadata file not found at " + path + ".", file=sys.stderr)
        raise SystemExit(e)
    except json.JSONDecodeError:
        print("Invalid JSON file.", file=sys.stderr)

    return result


def check_file_exists(file_path: str) -> bool:
    return os.path.exists(file_path)
