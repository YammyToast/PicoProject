import sys
import os.path
from pathlib import Path
import json
from enum import Enum

"""
    Attribute Name | Data Type | isFile?
"""
CONFIG_WIDGET_SCHEMA = [
    ("displayName", str, False),
    ("headerPath", str, True),
    ("mainPath", str, True),
    ("scripts", str, False),
    # ("bean", str, True)
]


class InvalidFilePath(Exception):
    def __init__(self, _file_path_str: str):
        super().__init__(f"Couldn't find file: \'{_file_path_str}\'")


class MissingAttribute(Exception):
    pass

class MissingAttributeType(Enum):
    MISSING = 0
    TYPE = 1
    NOFILE = 2


def print_log(_message: str):
    print(f" - {_message}");

def read_file_raw(_file_path) -> str:
    with open(_file_path) as f:
        return f.read()

def verify_file_path(_file_path: str) -> bool:
    path = Path(f"{_file_path}")
    if path.is_file():
        return True
    return False

def verify_config_part(_part: dict, _schema: list, _directory: str) -> list[tuple[str, MissingAttributeType]]:
    missing = []
    for attribute in _schema:
        if (x:=_part.get(attribute[0])) is None:
            missing.append((attribute[0], MissingAttributeType.MISSING))
            continue
        if type(x) != attribute[1]:
            missing.append((f"{attribute[0]} ({attribute[1].__name__})", MissingAttributeType.TYPE))
            continue

        if attribute[2] == True and not verify_file_path(path:=(_directory + _part.get(attribute[0]))):
            missing.append((f"{attribute[0]} -> {path}", MissingAttributeType.NOFILE))
        
        print_log(f"Parameter \'{attribute[0]}: {_part.get(attribute[0])}\' ok.")
    return missing

def verify_file_data(_data: str, _schema: list) -> list[tuple[str, str]]:
    print("VERIFY")

def load_config_file(_config_file_path: str, _directory: str) -> dict:
    try:
        if not verify_file_path(_config_file_path):
            raise InvalidFilePath(_config_file_path)
        print_log(f"Found: {_config_file_path}")
        parsed_data = json.loads(read_file_raw(_config_file_path))
        print_log(f"Parsed: {_config_file_path}")
        
        print_log(f"Verifying Data...")
        if parsed_data.get("widgets") is None:
            raise MissingAttribute(["widgets", MissingAttributeType.MISSING])

        print_log(f"Found Attribute \'widgets\'")
        for widget in parsed_data.get("widgets"):
            if len(x:= verify_config_part(widget, CONFIG_WIDGET_SCHEMA, _directory)) != 0:
                raise MissingAttribute(x)
        return parsed_data

    except MissingAttribute as e:
        attributes = e.args[0]
        if type(attributes) == str:
            attributes = [attributes]
        for attribute in attributes:
            print("ATTR ", attribute[1])
            if attribute[1] == MissingAttributeType.MISSING:
                e.add_note(f" - \'{attribute[0]}\' is missing.")
            if attribute[1] == MissingAttributeType.TYPE:
                e.add_note(f" - Type of \'{attribute[0]}\' is invalid.")
            if attribute[1] == MissingAttributeType.NOFILE:
                e.add_note(f" - Could not find file: \'{attribute[0]}\'.")
        raise

    except SyntaxError as e:
        e.add_note("Invalid JSON in config file.")        
        raise    

    except InvalidFilePath as e:
        raise

def verify_widget_contents(_widget_data: list, _directory: str):
    try:
        for widget in _widget_data:
            file_data = read_file_raw(_directory + widget.get("headerPath"))
            print("Data: ", file_data)
    except Exception as e:
        print(e)


def main(_config_file_path: str, _directory: str="./mods"):
    print_log(f"Using config file: {_config_file_path}")
    json_config_data = load_config_file(_config_file_path, _directory)
    # print(f"Data: {json_config_data}")
    print_log(f"Verified config file")
    print_log(f"Verifying file contents")    
    verify_widget_contents(json_config_data.get("widgets"), _directory)



if __name__ == '__main__':
    argv_config_file = "./config.json"
    if '-c' in sys.argv:
        argv_index = sys.argv.index('-c')
        if argv_index == (len(sys.argv) - 1):
            print("No value provided for \'Config-File-Path\' argument \'-c\'.")
            sys.exit(0)
        
        argv_config_file = sys.argv[argv_index + 1];


    main(argv_config_file);


