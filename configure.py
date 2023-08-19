import sys
import os.path
from pathlib import Path
import json
from enum import Enum
import re
import shutil
from dataclasses import dataclass
import time
from csnake import CodeWriter, Variable, FormattedLiteral, Function, FuncPtr, Struct

"""
    Attribute Name | Data Type | isFile?
"""
CONFIG_WIDGET_SCHEMA = [
    ("displayName", str, False),
    ("headerPath", str, True),
    ("mainPath", str, True),
    ("scripts", str, False),
]

"""
    Function Name | Pattern
"""
FUNCTION_WIDGET_SCHEMA_HEADER = [
    ("display", r"^(voiddisplay\(void\);){1}$"),
    ("thumbnail", r"^(voidthumbnail\(void\);){1}$"),
    ("settings", r"^(voidsettings\(void\);){1}$"),
    ("update", r"^(voidupdate\(void\);){1}$")
]

FUNCTION_WIDGET_SCHEMA_MAIN = [
    ("display", r"^((voiddisplay\(void\)){1}[\{\} ]*)$"),
    ("thumbnail", r"^((voidthumbnail\(void\)){1}[\{\} ]*)$"),
    ("settings", r"^((voidsettings\(void\)){1}[\{\} ]*)$"),
    ("update", r"^((voidupdate\(void\)){1}[\{\} ]*)$")
]

@dataclass
class LinkerWidget:
    target_location: str
    display_name: str
    origin_header_file: str
    origin_main_file: str
    origin_script_file: str
    target_header_file: str
    target_main_file: str
    target_script_file: str 

FUNC_PTR_TYPE = FuncPtr("void")
RETURN_TYPE_STRUCT = Struct("widget_link", typedef=True)
RETURN_TYPE_STRUCT.add_variable(("display", FUNC_PTR_TYPE))
RETURN_TYPE_STRUCT.add_variable(("thumbnail", FUNC_PTR_TYPE))
RETURN_TYPE_STRUCT.add_variable(("settings", FUNC_PTR_TYPE))
RETURN_TYPE_STRUCT.add_variable(("update", FUNC_PTR_TYPE))

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

def extract_file_name(_file_name: str) -> str:
    return _file_name.split("/")[-1]


# ================================================================================================================
# ================================================================================================================


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

def match_pattern_to_list(_list: str, _pattern: str, _pattern_name: str) -> bool:
    for item in _list:
        squash_item = ''.join(item.split())
        if re.search(_pattern, squash_item) != None:
            print_log(f"Found required function \'{_pattern_name}\'.")
            return True
    return False

def verify_widget_contents(_widget_data: list, _directory: str):
    try:
        missing = []
        for widget in _widget_data:
            print_log(f"Verifying widget \'{widget.get('displayName')}\'")
            print_log(f"Checking header file \'{widget.get('headerPath')}\'")
            file_data_header = list(
                filter(
                    None, 
                    read_file_raw(
                        _directory + widget.get("headerPath")
                    ).split("\n")
                 )
            )
            for pattern in FUNCTION_WIDGET_SCHEMA_HEADER:
                if not match_pattern_to_list(file_data_header, pattern[1], pattern[0]):
                    missing.append((pattern[0], widget.get("headerPath")))

            print_log(f"Header File ok.")
            print_log(f"Checking main file \'{widget.get('mainPath')}\'")

            file_data_main = list(
                filter(
                    None, 
                    read_file_raw(
                        _directory + widget.get("mainPath")
                    ).split("\n")
                 )
            )
            for pattern in FUNCTION_WIDGET_SCHEMA_MAIN:
                if not match_pattern_to_list(file_data_main, pattern[1], pattern[0]):
                    missing.append((pattern[0], widget.get("mainPath")))
            print_log(f"Main File ok.")

        if len(missing) != 0:
            raise MissingAttribute(missing)
        print_log(f"Widget Files ok.")
    except MissingAttribute as e:
        attributes = e.args[0]
        for attribute in attributes:
            e.add_note(f" - Could not find function \'{attribute[0]}\' in file \'{attribute[1]}\'")
        raise
    except Exception as e:
        print(e)

# ================================================================================================================
# ================================================================================================================

def make_output_directory(_clear_generated: bool):
    try:
        directory_path = "/generated"
        directory_exists = Path(f"{Path.cwd()}{directory_path}").is_dir()

        if _clear_generated == True and directory_exists:
            for filename in os.listdir(f'.{directory_path}'):
                file_path = os.path.join(f'.{directory_path}')
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            print_log(f"Cleared {directory_path} folder.")

        if not Path(f"{Path.cwd()}{directory_path}").is_dir():
            Path(f"{Path.cwd()}{directory_path}").mkdir(exist_ok=False)
            print_log(f"Created directory \'{directory_path}\'")
    
    except OSError as e:
        e.add_note(f"Couldn't delete file in generated folder.")
        raise
    except FileExistsError as e:
        e.add_note(f"Error creating generated folder.")
        raise
    except Exception as e:
        raise



def compile_linker_widget_data(_widget_data: list, _origin_directory: str, _target_directory: str) -> list[LinkerWidget]:
    data = []
    for widget in _widget_data:
        target_location = os.path.join(_target_directory + "/" + widget.get("displayName"))
        data.append(
            LinkerWidget(
                target_location,
                widget.get("displayName"),
                os.path.join(_origin_directory + widget.get("headerPath")),
                os.path.join(_origin_directory + widget.get("mainPath")),
                os.path.join(_origin_directory + widget.get("scripts")),

                os.path.join(widget.get("displayName") + "/" + extract_file_name(widget.get("headerPath"))),
                os.path.join(widget.get("displayName") + "/" + extract_file_name(widget.get("mainPath"))),
                os.path.join(widget.get("displayName") + "/" + extract_file_name(widget.get("scripts"))),
                # os.path.join(target_location + "/" + extract_file_name(widget.get("headerPath"))),
                # os.path.join(target_location + "/" + extract_file_name(widget.get("mainPath"))),
                # os.path.join(target_location + "/" + extract_file_name(widget.get("scripts"))),
                # os.path.join(_target_directory + "/" + 
                # widget.get("displayName") + "/" +
                # extract_file_name(widget.get("headerPath"))),
                # os.path.join(_target_directory + "/" +
                # widget.get("displayName") + "/" +
                # extract_file_name(widget.get("mainPath"))),
                # os.path.join(_target_directory + "/" +
                # widget.get("displayName") + "/" +
                # extract_file_name(widget.get("scripts")))

            )
        )
    return data

def make_target_directories(_widget_data: list[LinkerWidget], _target_directory: str):
    for widget in _widget_data:
        path = f"{_target_directory}/{widget.display_name}"
        Path(path).mkdir(exist_ok=False)
        print_log(f"Created directory: \'{path}\'")

def modify_target_file(_file_data: str, _widget_display_name: str, _schema: list):
    split_data = _file_data.split("\n")
    line_num = 0
    for line in split_data:
        squash_line = ''.join(line.split())
        for pattern in _schema:
            if re.search(pattern[1], squash_line) != None:
                # SWITCH THIS TO CSNAKE IMPLEMENTATION
                segmented_line = line.split()
                suffix = "" if _schema == FUNCTION_WIDGET_SCHEMA_HEADER else "{"
                split_data[line_num] = segmented_line[0] + " " + _widget_display_name + "_" + segmented_line[1] + suffix
                continue;
        line_num += 1
    return ('\n'.join(split_data))

def translate_target_files(_widget_data: list[LinkerWidget], _target_directory):
    for widget in _widget_data:
        destination = f"{_target_directory}/{widget.display_name}/"
        origin_header = widget.origin_header_file
        origin_main = widget.origin_main_file
        modified_header = modify_target_file(read_file_raw(origin_header), widget.display_name, FUNCTION_WIDGET_SCHEMA_HEADER)
        modified_main = modify_target_file(read_file_raw(origin_main), widget.display_name, FUNCTION_WIDGET_SCHEMA_MAIN)

        with open(os.path.join(_target_directory + "/" + widget.target_header_file), 'w') as header_file:
            header_file.write(str(modified_header))   
        with open(os.path.join(_target_directory + "/" + widget.target_main_file), 'w') as main_file:
            main_file.write(str(modified_main))            


# ================================================================================================================
# ================================================================================================================

def write_linker_file_header(_widget_data: list[LinkerWidget], _target_directory: str):
    cwr = CodeWriter()
    cwr.add_autogen_comment('configure.py')
    cwr.start_if_def("_LINKER_HEADER_", invert=True)
    cwr.add_define("_LINKER_HEADER_")
    for widget in _widget_data:
        cwr.include(widget.target_header_file)
    cwr.add_struct(RETURN_TYPE_STRUCT)

    # return_array = Variable("return_array_variable", "widget_link", array=len(_widget_data))
    main_function = Function(
        "LINKER_FUNCTION_POINTERS",
        return_type="struct widget_link*"

    )
    cwr.add_function_prototype(main_function)
    cwr.end_if_def()
    with open(os.path.join(_target_directory + "/" + "linker.h"), 'w') as header_file:
        header_file.write(str(cwr))

def write_linker_file_main(_widget_data: list[LinkerWidget], _target_directory: str):
    print("WRITE MAIN")
    cwr = CodeWriter()
    cwr.add_autogen_comment('configure.py')
    cwr.start_if_def("_LINKER_MAIN_", invert=True)
    cwr.add_define("_LINKER_MAIN_")
    cwr.include("linker.h")

    for widget in _widget_data:
        cwr.include(widget.target_header_file)

    main_function = Function(
        "LINKER_FUNCTION_POINTERS",
        return_type="widget_link*"

    )
    malloc_statement = f"widget_link* functions = malloc(sizeof(struct widget_link) * {len(_widget_data)});"
    main_function.add_code(malloc_statement)
    cwr.add_function_definition(main_function)
    cwr.end_if_def()
    with open(os.path.join(_target_directory + "/" + "linker.c"), 'w') as main_file:
        main_file.write(str(cwr))


# ================================================================================================================
# ================================================================================================================

def main(_config_file_path: str, _clear_generated: bool, _origin_directory: str="./mods"):
    target_directory = "./generated"
    print_log(f"Using config file: {_config_file_path}")
    json_config_data = load_config_file(_config_file_path, _origin_directory)
    print_log(f"Verified config file")
    print_log(f"Verifying file contents")    
    verify_widget_contents(json_config_data.get("widgets"), _origin_directory)
    print("\n")
    print_log(f"Generating widget bindings...")
    make_output_directory(_clear_generated)
    linker_widget_data = compile_linker_widget_data(json_config_data.get("widgets"), _origin_directory, target_directory)
    make_target_directories(linker_widget_data, target_directory)

    translate_target_files(linker_widget_data, target_directory)

    write_linker_file_header(linker_widget_data, target_directory)
    print_log(f"Generated \'linker.h\'.")
    write_linker_file_main(linker_widget_data, target_directory)
    print_log(f"Generated \'linker.c\'.")


if __name__ == '__main__':
    start_ts = time.time()
    argv_config_file = "./config.json"
    argv_clear_generated = True
    if '-c' in sys.argv:
        argv_index = sys.argv.index('-c')
        if argv_index == (len(sys.argv) - 1):
            print("No value provided for \'Config-File-Path\' argument \'-c\'.")
            sys.exit(0)
        argv_config_file = sys.argv[argv_index + 1];
    
    if '-nc' in sys.argv:
        argv_clear_generated = False        


    main(argv_config_file, argv_clear_generated);
    end_ts = time.time()
    print("\nFinished. Completed in {:2f} seconds.".format(end_ts - start_ts))

