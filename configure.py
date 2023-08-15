import sys
import os.path
from pathlib import Path

class InvalidFilePath(Exception):
    def __init__(self, _file_path_str: str):
        super().__init__(f"Couldn't find file: \'{_file_path_str}\'")

def print_log(_message: str):
    print(f" - {_message}");

def verify_file_path(_file_path: str) -> bool:
    path = Path(f"{_file_path}")
    if path.is_file():
        return True
    return False

def load_config_file(_config_file_path: str) -> dict:
    try:
        if not verify_file_path(_config_file_path):
            raise InvalidFilePath(_config_file_path)
        print_log(f"Found: {_config_file_path}")
    except SyntaxError as e:
        e.add_note("Invalid JSON in config file.")        
        raise    
    except InvalidFilePath as e:
        raise

def main(_config_file_path: str):
    print_log(f"Using config file: {_config_file_path}")
    json_config_data = load_config_file(_config_file_path)
    print(f"Data: {json_config_data}")



if __name__ == '__main__':
    argv_config_file = "./config.json"
    if '-c' in sys.argv:
        argv_index = sys.argv.index('-c')
        if argv_index == (len(sys.argv) - 1):
            print("No value provided for \'Config-File-Path\' argument \'-c\'.")
            sys.exit(0)
        
        argv_config_file = sys.argv[argv_index + 1];


    main(argv_config_file);


