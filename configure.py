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
from mdutils.mdutils import MdUtils
import uuid
from PIL import Image
import math
import argparse

"""
    Attribute Name | Data Type | isFile?
"""
CONFIG_WIDGET_SCHEMA = [
    ("headerPath", str, True),
    ("headerPath", str, True),
    ("mainPath", str, True),
    ("bindings", str, False),
]

CONFIG_BINDONLY_SCHEMA = [
    ("displayName", str, False),
    ("bindings", str, True)
]

CONFIG_PERSONALITY_SCHEMA = [
    ("displayName", str, False),
    ("scriptBindings", str, True)
]


"""
    Function Name | Pattern
"""
FUNCTION_WIDGET_SCHEMA_HEADER = [
    ("display", r"^(voiddisplay\(UWORD\*\);){1}$"),
    ("thumbnail", r"^(voidthumbnail\(UWORD\*\);){1}$"),
    ("settings", r"^(voidsettings\(UWORD\*\);){1}$"),
    ("update", r"^(voidupdate\(UWORD\*\);){1}$")
]

FUNCTION_WIDGET_SCHEMA_MAIN = [
    ("display", r"^((voiddisplay\(UWORD\*.+\)){1}[\{\} ]*)$"),
    ("thumbnail", r"^((voidthumbnail\(UWORD\*.+\)){1}[\{\} ]*)$"),
    ("settings", r"^((voidsettings\(UWORD\*.+\)){1}[\{\} ]*)$"),
    ("update", r"^((voidupdate\(UWORD\*.+\)){1}[\{\} ]*)$")
]

BINDING_FUNCTION_PATTERN = r"(.+[ ]+[\w]+\(.*\)[ ]*[;{]{1})$"
BINDING_PARAM_DESCRIPTION_PATTERN = r"(.[\s])*\*.*[\s]*(@param) ([a-zA-Z*])+ ([\w])+:((.|\n)(?!(@param)|(@name))(?!\*\/))+"

MAP_INCLUDE_PATTERN = r"\s*(#include){1}([\s\t ])+(\"[\w]+(\.h|\.c)\"){1}[\s\n ]*"

TRANSLATE_IMAGE_DEFINITION_PATTERN = r"(image_link){1}([\t\s]+[\w]+[\t\s]*=[\t\s]*){1}({(.|\n)+};)"
TRANSLATE_IMAGE_REF_PATTERN = r"(.ref){1}([\w\t ]*=[\w\t ]*){1}((?!,).)+"
TRANSLATE_IMAGE_PATH_PATTERN = r'^"(\.\.)*(\/|(?!\.\.)[a-zA-Z0-9_\-\/\.]+)+(\.[\w]+)"$'
TRANSLATE_IMAGE_WIDTH_PATTERN = r'(.width){1}([\s\t\n ]*=[\s\t\n ]*){1}([0-9]+){1}([\s\t\n ]*)(?!,}){1}'
TRANSLATE_IMAGE_HEIGHT_PATTERN = r'(.height){1}([\s\t\n ]*=[\s\t\n ]*){1}([0-9]+){1}([\s\t\n ]*)(?!,}){1}'
TRANSLATE_IMAGE_VARIABLE = r'([ \s\n\t])*(\w)+([ \s\n\t])+(\w)+(?!=)+'

class FileTypes(Enum):
    HEADER = 0
    MAIN = 1

@dataclass
class LinkerWidget:
    target_location: str
    origin_location: str
    display_name: str
    origin_header_file: str    
    origin_main_file: str
    origin_binding_file: str
    target_header_file: str
    target_main_file: str
    target_binding_file: str

@dataclass
class BindingFunctionParam:
    name: str
    type_name: str
    description: str

@dataclass
class BindingFunction:
    name: str
    params: list[BindingFunctionParam]
    return_type_name: str
    raw_function_def: str
    description: str

@dataclass
class BindingFileGrouping:
    file_display_name: str
    file_path: str
    functions: list[BindingFunction]

@dataclass
class MapItem:
    file_type: FileTypes
    path_source: str
    path_stripped: str
    searched: bool

@dataclass
class MapGrouping:
    rel_widget: LinkerWidget
    root_header_path: str
    root_main_path: str
    internal_map: list[MapItem]

@dataclass
class ImageLink:
    ref: str
    uuid: str
    height: int
    width: int

BLACK_IMG_PTR = Variable("black_image", "UWORD*")
FUNC_PTR_TYPE = FuncPtr("void", arguments=([BLACK_IMG_PTR]))
RETURN_TYPE_STRUCT = Struct("widget_link", typedef=True)
RETURN_TYPE_STRUCT.add_variable(("display", "API_FUNC"))
RETURN_TYPE_STRUCT.add_variable(("thumbnail", "API_FUNC"))
RETURN_TYPE_STRUCT.add_variable(("settings", "API_FUNC"))
RETURN_TYPE_STRUCT.add_variable(("update", "API_FUNC"))
IMG_BUFFER_TYPE = "const UWORD"

class InvalidFilePath(Exception):
    def __init__(self, _file_path_str: str):
        super().__init__(f"Couldn't find file: \'{_file_path_str}\'")

class MissingAttribute(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class MissingAttributeType(Enum):
    MISSING = 0
    TYPE = 1
    NOFILE = 2

class ImageRefErrorType(Enum):
    NOREF = 0
    NOHEIGHT = 1
    NOWIDTH= 2
    REFISVAR = 3
    REFINVALID = 4
    REFNOTFOUND = 5


class ImageRefError(Exception):
    def __init__(self, _message: str, _type: ImageRefErrorType):
        if _type == ImageRefErrorType.NOREF:
            super().__init__(f"Image Definition does not contain a '.ref' attribute: \n{_message}.")
        elif _type == ImageRefErrorType.NOWIDTH:
            super().__init__(f"Image Definition does not contain a '.width' attribute: \n{_message}.")
        elif _type == ImageRefErrorType.NOHEIGHT:
            super().__init__(f"Image Definition does not contain a '.height' attribute: \n{_message}.")
        elif _type == ImageRefErrorType.REFISVAR:
            super().__init__(f"'.ref' value is non-constant (variable): \n{_message}")
        elif _type == ImageRefErrorType.REFINVALID:
            super().__init__(f"Value given for '.ref' is invalid: \n{_message}")
        elif _type == ImageRefErrorType.REFNOTFOUND:
            super().__init__(f"Could not find image pointed to by ref: \n{_message}")


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



def load_config_file(_config_file_path: str, _origin_directory: str, _schema = CONFIG_WIDGET_SCHEMA) -> dict:
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
            if len(x:= verify_config_part(widget, _schema, _origin_directory)) != 0:
                raise MissingAttribute(x)
            
        if parsed_data.get("personality") is None:
            raise MissingAttribute(["personality", MissingAttributeType.MISSING])
        print_log(f"Found Attribute \'personality\'")
        
        if len(y:= verify_config_part(parsed_data.get("personality"), CONFIG_PERSONALITY_SCHEMA, _origin_directory)) != 0:
            raise MissingAttribute(y)

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

def get_image_file_data(_file_path: str) -> list[str]:
    im = Image.open(_file_path)
    # https://rgbcolorpicker.com/565
    # 16 Bit Image Format
    # R - 5 - 31
    # G - 6 - 63
    # B - 5 - 31
    pixel_values: list[str] = []
    for r, g, b in list(im.getdata()):
        new_r = math.floor((r / 255) * 31)
        new_g = math.floor((g / 255) * 63)
        new_b = math.floor((b / 255) * 31)
        shift_r = new_r << 11
        shift_g = new_g << 5
        rgb565 = shift_r | shift_g | new_b
        # bug around here with small hex values being generated.
        rgb565_hex = hex(rgb565).upper().rjust(6, "0")
        pixel_values.append(rgb565_hex)
    return pixel_values

# ================================================================================================================
# ================================================================================================================

def make_output_directory(_clear_generated: bool, _directory_path: str = "/generated"):
    try:
        directory_path = _directory_path
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

def compile_config_widget_files(_widget_data: list, _origin_directory: str, _target_directory: str) -> list[LinkerWidget]:
    data = []
    for widget in _widget_data:
        target_location = os.path.join(_target_directory + "/" + widget.get("displayName"))
        origin_top_directory = list(
            filter(
                None,
                widget.get("mainPath").split("/")
            )
        )
        squashed_display_name = widget.get("displayName").replace(" " , "_")
        data.append(
            LinkerWidget(
                target_location=target_location,
                origin_location=os.path.join(_origin_directory, origin_top_directory[0]),
                display_name=squashed_display_name,
                origin_header_file=os.path.join(_origin_directory + widget.get("headerPath")),
                origin_main_file=os.path.join(_origin_directory + widget.get("mainPath")),
                origin_binding_file=os.path.join(_origin_directory + widget.get("bindings")),

                target_header_file=os.path.join(squashed_display_name + "/" + extract_file_name(widget.get("headerPath"))),
                target_main_file=os.path.join(squashed_display_name + "/" + extract_file_name(widget.get("mainPath"))),
                target_binding_file=os.path.join(squashed_display_name + "/" + extract_file_name(widget.get("bindings")))
            )
        )
    return data

def make_target_directories(_widget_data: list[LinkerWidget], _target_directory: str):
    assets_path = os.path.join(_target_directory, "assets")
    Path(assets_path).mkdir(exist_ok=True)
    for widget in _widget_data:
        path = os.path.join(_target_directory, widget.display_name)
        Path(path).mkdir(exist_ok=False)
        print_log(f"Created directory: \'{path}\'")


def uniquify_root_file(_file_data: str, _widget_display_name: str, _schema: list):
    split_data = _file_data.split("\n")
    line_num = 0
    for line in split_data:
        squash_line = ''.join(line.split())
        for pattern in _schema:
            if re.search(pattern[1], squash_line) != None:
                # SWITCH THIS TO CSNAKE IMPLEMENTATION
                segmented_line = line.split()
                split_data[line_num] = (segmented_line[0] + 
                " " + _widget_display_name +
                "_" + ''.join(segmented_line[1:]))
                continue;
        line_num += 1
    return ('\n'.join(split_data))

def replace_image_declarations(_file_data: str, _source_directory: str) -> str:
    try:
        working_file_data = _file_data
        data_buf = [_file_data]
        translated_files = []
        while (x := re.search(TRANSLATE_IMAGE_DEFINITION_PATTERN, working_file_data)):
            image_slice = working_file_data[x.span()[0]:x.span()[1]].replace("\n", "")
            if (h := re.search(TRANSLATE_IMAGE_HEIGHT_PATTERN, image_slice)) == None:
                raise ImageRefError(image_slice, ImageRefErrorType.NOHEIGHT)
            image_height = image_slice[h.span()[0]:h.span()[1]].replace(" ", "").split("=")[-1]

            if (w := re.search(TRANSLATE_IMAGE_WIDTH_PATTERN, image_slice)) == None:
                raise ImageRefError(image_slice, ImageRefErrorType.NOWIDTH)
            image_width = image_slice[w.span()[0]:w.span()[1]].replace(" ", "").split("=")[-1]

            if (y := re.search(TRANSLATE_IMAGE_REF_PATTERN, image_slice)) == None:
                raise ImageRefError(image_slice, ImageRefErrorType.NOREF)
            ref_slice = image_slice[y.span()[0]:y.span()[1]].replace(" ", "")
            ref_value = ref_slice.split("=")[1].strip("\"")
            

            image_path = os.path.join(_source_directory, os.path.normpath(ref_value))

            if os.path.isfile(image_path) == False:
                raise ImageRefError(image_path, ImageRefErrorType.REFNOTFOUND)

            if (s := re.search(TRANSLATE_IMAGE_VARIABLE, image_slice)) == None:
                raise ImageRefError(image_slice, ImageRefErrorType.REFINVALID)
            var_name = image_slice[s.span()[0]:s.span()[1]].split(" ")[-1].strip(" \n")
            
            image_uuid = f"img_{str(uuid.uuid4()).replace('-', '_')}"
            translated_files.append(ImageLink(
                ref=image_path,
                uuid=image_uuid,
                height=image_height,
                width=image_width
            ))


            data_buf_len = len(data_buf)
            data_buf[data_buf_len - 1] = working_file_data[:x.span()[0]]
            data_buf.append(f"""{IMG_BUFFER_TYPE} {var_name} = {image_uuid};""")
            data_buf.append(working_file_data[x.span()[1]:])

            working_file_data = _file_data[x.span()[1]:]
    
        new_file_data = "".join(data_buf)

        for include in translated_files:
            new_file_data = f"#include \"{include.uuid}.c\"\n{new_file_data}"

        return (new_file_data, translated_files)
    except ImageRefError as e:
        print(e)
        raise

def write_image_data_files(_translated_files: list[ImageLink], _assets_directory: str = "./generated/assets"):
    try:
        for file in _translated_files:
            img_size = int(file.width) * int(file.height)
            img_data = get_image_file_data(file.ref)
            with open(os.path.join(_assets_directory, f"{file.uuid}.c"), 'w') as header_file:
                cwr = CodeWriter()
                cwr.include("DEV_Config.h")
                cwr.include("GUI_Paint.h")
                cwr.add_autogen_comment('configure.py')
                cwr.start_if_def(f"_{file.uuid}_", invert=True)
                cwr.add_define(f"_{file.uuid}_")
                
                # WHY IS ESCAPE {} TO ADD 2 MORE {} ???
                cwr.add_lines("{0} {1}[{2}] = {{\n{3}\n}}".format(
                    IMG_BUFFER_TYPE,
                    file.uuid,
                    img_size,
                    ', '.join(img_data)

                ))
                # img = Variable(
                #     file.uuid,
                #     IMG_BUFFER_TYPE,
                #     array=img_size,
                #     value=img_data
                # )
                # cwr.add_variable_initialization(img)

                cwr.end_if_def()
                
                
                header_file.write(str(cwr))
    except FileExistsError as e:
        e.add_note(f"File already exists: {e.args[0]}")
        raise
    except OSError:
        raise

def transpile_target_files(_file_map: list[MapGrouping], _origin_directory: str, _target_directory: str):
    for widget_name, widget_file_map in _file_map.items():
        image_source_directory = os.path.normpath(widget_file_map.rel_widget.origin_location)
        # image_target_directory = os.path.join(_target_directory, widget_file_map.rel_widget.display_name)
        for file in widget_file_map.internal_map:
            print_log(f"Transpiling file: {file.path_source}")
            file_data = read_file_raw(file.path_source)
            if file.path_source == widget_file_map.root_header_path:
                file_data = uniquify_root_file(file_data, widget_name, FUNCTION_WIDGET_SCHEMA_HEADER)
            if file.path_source == widget_file_map.root_main_path:
                file_data = uniquify_root_file(file_data, widget_name, FUNCTION_WIDGET_SCHEMA_MAIN)
            # if file.path_source == widget_file_map.rel_widget.origin_binding_file:
            #     continue;
            
            file_data, translated_files = replace_image_declarations(file_data, image_source_directory)

            if len(translated_files) > 0:
                write_image_data_files(translated_files)

            target_path = os.path.join(_target_directory, widget_name, file.path_stripped)
            with open(target_path, 'w') as file_writer:
                file_writer.write(str(file_data))

def collect_binding_files(_file_map: list[MapGrouping]) -> list[tuple[str, str, str]]:
        paths = []
        for widget_name, map_grouping in _file_map.items():
            for file in map_grouping.internal_map:
                if map_grouping.rel_widget.origin_binding_file == file.path_source:
                    paths.append((
                        file.path_source,
                        map_grouping.rel_widget.target_binding_file,
                        widget_name
                    ))
        return paths

def collect_binding_funcs(_file_data: str):
    funcs = []
    # THIS IS NOT SAFE AS FUNCTION DECLS CAN SPAN OVER MULTIPLE LINES.
    for line in _file_data:
        if re.search(BINDING_FUNCTION_PATTERN, line) == None:
            continue;
        split_function_def = re.split("\(|\)|\s",line)
        if len(split_function_def) < 3:
            raise SyntaxError(line)
        funcs.append(
            line.strip(" }{;")
        )
    return funcs

def capture_binding_func(_file_data: str, _function_form: str):
    try:
        if (func_begin:= _file_data.find(_function_form)) == -1:
            # this should never throw but just in case.
            raise
        # Scope to the beginning of the searched function so we search against the correct '{'.
        search_slice = _file_data[func_begin:]
        if (closure_start:= search_slice.find("{")) == -1:
            raise

        # Increase index by 1, as .find returns an index that includes the 'root' closure for the function.
        # this offset the closure count by 1 and the while loop couldn't work.
        search_index = closure_start + 1
        # Start at 1, to account for the root closure.
        # Once the closing '}' is found, the closure count will equal 0.
        closure_count = 1;
        while closure_count > 0:
            if (search_index == len(search_slice)):
                raise

            search_val = search_slice[search_index]
            
            if search_val == "{":
                closure_count += 1
            if search_val == "}":
                closure_count -= 1
            
            search_index += 1
        return _file_data[func_begin:func_begin+search_index]
        # print(search_slice[closure_start:search_index])
    except Exception as e:
        raise



def transpile_binding_files(_file_map: list[MapGrouping], _binding_impl_file_path: str, _target_directory: str):
    try:
        # compile binding hooks created by widget
        # compile binding impls by personality
        # find union in sets
        # transpile bindings to target file(s?)
        # EXT ------
        # Remove unneccessary calls to bindings that have no impl
        # in widget files.
        binding_impl_file_data = list(
                filter(
                    None, 
                    read_file_raw(
                        _binding_impl_file_path
                    ).split("\n")
                )
        )

        print_log(f"Collecting implemented binding functions.")
        binding_impl_funcs = collect_binding_funcs(binding_impl_file_data)

        print_log(f"Collecting widget binding-file paths.")
        binding_file_paths = collect_binding_files(_file_map)
        binding_funcs = []
        for binding_file in binding_file_paths:
            file_data = list(
                filter(
                    None, 
                    read_file_raw(
                        binding_file[0]
                    ).split("\n")
                )
            )
            print_log(f"Collecting bindings from \'{binding_file[1]}\'")
            binding_funcs = collect_binding_funcs(file_data)
            # Find intersection of widget bindings and implemented bindings.
            binding_funcs_matches = [value for value in binding_funcs if value in binding_impl_funcs]
            
            matches_captures = []
            for func in binding_funcs_matches:
                # Look at impl file data to find implementation
                # We've already done the existence checks at this point so we can just do it.
                matches_captures.append(capture_binding_func("\n".join(binding_impl_file_data), func))

            print_log(f"Transpiling to file: \'{os.path.join(_target_directory, binding_file[1])}\'")
            # WRITE HEADER
            write_binding_file(
                binding_funcs_matches,
                os.path.join(_target_directory, binding_file[1]),
                binding_file[2],
                True
            )
            print_log(f"Transpiling to file: \'{os.path.join(_target_directory, binding_file[1]).replace('.h', '.c')}\'")
            #WRITE MAIN
            write_binding_file(
                matches_captures,
                os.path.join(_target_directory, binding_file[1]).replace(".h", ".c"),
                binding_file[2],
                False
            )                                          

    except Exception as e:
        raise

# ================================================================================================================
# ================================================================================================================

def write_linker_file_header(_widget_data: list[LinkerWidget], _target_directory: str):
    cwr = CodeWriter()
    cwr.add_autogen_comment('configure.py')
    cwr.start_if_def("_LINKER_HEADER_", invert=True)
    cwr.add_define("_LINKER_HEADER_")

    cwr.add_line(f"typedef {FUNC_PTR_TYPE.get_declaration('API_FUNC')};")
    cwr.add_struct(RETURN_TYPE_STRUCT)
    
    for widget in _widget_data:
        cwr.include(widget.target_header_file)
        cwr.include(widget.target_main_file)
        widget_var = Variable(
            widget.display_name,
            RETURN_TYPE_STRUCT.name,
            qualifiers=(["const"])
        )
        cwr.add_variable_declaration(widget_var)

    widget_list_var = Variable(
        "widget_links",
        RETURN_TYPE_STRUCT.name,
        qualifiers=(["const"]),
        array=len(_widget_data)
    )
    cwr.add_variable_declaration(widget_list_var)
    
    widget_count_var = Variable("widget_count", "int", qualifiers=(["const"]))
    cwr.add_variable_declaration(widget_count_var)

    cwr.end_if_def()
    with open(os.path.join(_target_directory + "/" + "linker.h"), 'w') as header_file:
        header_file.write(str(cwr))

def write_linker_file_main(_widget_data: list[LinkerWidget], _target_directory: str):
    cwr = CodeWriter()
    cwr.add_autogen_comment('configure.py')
    cwr.start_if_def("_LINKER_MAIN_", invert=True)
    cwr.add_define("_LINKER_MAIN_")
    cwr.include("linker.h")
    
    widget_links_var = f"const widget_link widget_links[{len(_widget_data)}] ="
    widget_links_var += "{" 
    for widget in _widget_data:
        cwr.include(widget.target_header_file)
        cwr.include(widget.target_main_file)
        widget_var = f"const widget_link {widget.display_name} ="
        widget_var += "{"
        widget_var += f".display = *{widget.display_name}_display,"
        widget_var += f".thumbnail = *{widget.display_name}_thumbnail,"
        widget_var += f".settings = *{widget.display_name}_settings,"
        widget_var += f".update = *{widget.display_name}_update,"
        widget_var += "};"
        cwr.add_line(widget_var)

        widget_links_var += f"{widget.display_name},"
    widget_links_var += "};"
    cwr.add_line(widget_links_var)
    
    widget_count_var = Variable("widget_count", "int", value=len(_widget_data), qualifiers=(["const"]))
    cwr.add_variable_initialization(widget_count_var)


    cwr.end_if_def()

    with open(os.path.join(_target_directory + "/" + "linker.c"), 'w') as main_file:
        main_file.write(str(cwr))

def write_binding_file(_binding_data: list[str], _target_file_path: str, _display_name: str, _header: bool):
    cwr = CodeWriter()

    cwr.add_autogen_comment('configure.py')
    suffix = "H" if _header == True else "C" 
    cwr.start_if_def(f"_LINKER_BINDINGS_{_display_name}_{suffix}_", invert=True)
    cwr.add_define(f"_LINKER_BINDINGS_{_display_name}_{suffix}_")

    for func in _binding_data:
        cwr.add_lines(f"{func}{';' if _header == True else ''}")

    cwr.end_if_def()
    with open(_target_file_path, 'w') as header_file:
        header_file.write(str(cwr))

# ================================================================================================================
# ================================================================================================================

def compile_widget_include_files(_file_data: list[str], _widget_files: list[str], _directory_path: str) -> list[str]:
    include_list = []
    for line in _file_data:
        if (x := re.search(MAP_INCLUDE_PATTERN, line)) != None:
            include_list.append(
                line[x.span()[0]:x.span()[1]].split("#include")[1].strip(" \"")
            )

    match_list = []
    for iter in range(len(include_list)):
        if include_list[iter] in _widget_files:
            match_list.append((include_list[iter], os.path.join(_directory_path, include_list[iter])))


    return match_list

def build_widget_file_map(_widget_data: list[LinkerWidget], _allow_include_errors: bool = True):
    file_map: list[MapGrouping] = {}
    for widget in _widget_data:
        widget_directory_files = []
        # This needs a look at, constant slicing is probably a bad idea.
        widget_directory_path = "/".join(widget.origin_main_file.split("/")[:3])
        for (_, _, file_names) in os.walk(widget_directory_path):
            widget_directory_files.extend(file_names)

        internal_map: list[MapItem] = []
        internal_map.append(MapItem(
            file_type=FileTypes.HEADER,
            path_source=widget.origin_header_file,
            path_stripped=widget.origin_header_file.split("/")[-1],
            searched=False
        ))
        internal_map.append(MapItem(
            file_type=FileTypes.MAIN,
            path_source=widget.origin_main_file,
            path_stripped=widget.origin_main_file.split("/")[-1],
            searched=False
        ))

        index = 0
        # List of path names, to make 'searched' checking easier and quicker.
        reduced_path_list = [widget.origin_header_file, widget.origin_main_file]

        while (x:= internal_map[index]).searched == False:
            index_file_data = read_file_raw(x.path_source).split("\n")
            include_list = compile_widget_include_files(index_file_data, widget_directory_files, widget_directory_path)
            for path in include_list:
                # Check against reduced_path_list for quicker and easier duplicate checking.    
                if path[1] not in reduced_path_list:
                    reduced_path_list.append(path)
                    extension = path[0].split(".")[-1]
                    internal_map.append(MapItem(
                        file_type=FileTypes.HEADER if extension == "h" else FileTypes.MAIN,
                        path_source=path[1],
                        path_stripped=path[0],
                        searched=False
                    ))
            x.searched = True
            if (index + 1) > (len(internal_map) - 1):
                break;
            index += 1
        grouping = MapGrouping(
            rel_widget=widget,
            root_header_path=widget.origin_header_file,
            root_main_path=widget.origin_main_file,
            internal_map=internal_map
        )

        file_map.update({widget.display_name:grouping})
    return file_map


# ================================================================================================================
# ================================================================================================================

def try_capture_comment(_file_data: str, _comment_index_end: int):
    lines = []
    index = _comment_index_end
    while (re.search(r"\/\*", _file_data[index]) == None) and index > 0:
        lines.extend([_file_data[index].strip()])
        index -= 1
    lines.extend([_file_data[index].strip()])
    return lines

def match_comment_vars(_comment_data: list[str], _parameter: str):
    for index in range(len(_comment_data)):
        accumulative_text = "\n".join(_comment_data[index:])
        if (x:= re.search(BINDING_PARAM_DESCRIPTION_PATTERN, accumulative_text)) == None:
            continue
        text_param_name = (
                        accumulative_text
                            [x.span()[0]:x.span()[1]]
                            .split(":")[0]
                            .strip()
                        ).split(" ")[-1]
        if(text_param_name == _parameter):
            # Joining on ":" is probably not the best solution to fixing extra ":" in text that are removed in the description extraction.
            # it do work doe
            # this is so dumb
            return (":".join(accumulative_text
                            [x.span()[0]:x.span()[1]]
                            .split(":")[1:])
                    ).strip("* \n").replace("*", "").replace("\n", "")

    return "N/A"

def compile_file_bindings(_file_data: str) -> list[BindingFunction]:
    try:
        funcs = []
        for line in _file_data:
            if re.search(BINDING_FUNCTION_PATTERN, line) == None:
                continue;
            split_function_def = re.split("\(|\)|\s",line)
            if len(split_function_def) < 3:
                raise SyntaxError(line)

            binding_params = []
            params = (
                ';'.join(split_function_def[2:-1])
            ).split(",")

            index = _file_data.index(line)
            comment_index_end = index - 1 if index > 0 else index

            comment_text = "N/A"
            if (re.search(r"\*\/", _file_data[comment_index_end]).span()[1]) != None:
                comment_text = try_capture_comment(_file_data, comment_index_end)
                
            for param in params:
                parsed_param = param.replace(";", " ").strip().split(" ")
                param_description = comment_text if comment_text == "N/A" else match_comment_vars(comment_text, parsed_param[1])
                binding_params.append(
                    BindingFunctionParam(
                        parsed_param[1],
                        parsed_param[0],
                        param_description
                    )
                )

            funcs.append(
                BindingFunction(
                # CHANGE THIS TO COMMENT NAME
                name=split_function_def[1],
                params=binding_params,
                return_type_name=split_function_def[0],
                raw_function_def=line,
                description="TODO"
                )
            )
        return funcs
    except SyntaxError as e:
        e.add_note(f"Invalid function prototype: {e.args}")
        raise

def compile_bindings(_widget_data: list, _origin_directory: str) -> list[BindingFileGrouping]:
    binding_groups = []
    for widget in _widget_data:
        path = os.path.join(_origin_directory + widget.get("bindings"))
        print_log(f"Reading Bindings from: {path}")
        file_data = list(
                filter(
                    None, 
                    read_file_raw(
                        path
                    ).split("\n")
                )
        )
        file_bindings = compile_file_bindings(file_data)
        binding_groups.append(
            BindingFileGrouping(
                file_display_name=widget.get("displayName"),
                file_path=path,
                functions=file_bindings    
            )
        )
    return binding_groups

def build_param_table(_param_list: list[BindingFunctionParam]) -> str:
    table_str = "<table>"
    table_str += "<tr><th>Name</th><th>Type</th><th>Description</th></tr>"
    for param in _param_list:
        table_str += "<tr>"
        table_str += f"<td>{param.name}</td>"
        table_str += f"<td>{param.type_name}</td>"
        table_str += f"<td>{param.description}</td>"
        table_str += "</tr>"
    table_str += "</table>"
    return table_str

def write_markdown_file(_binding_data: list[BindingFileGrouping], _target_directory: str):
    file_path = os.path.join(_target_directory + "/" + "Bindings")
    print_log(f"Writing binding file: \'{file_path}.md\'")
    md_file = MdUtils(file_name=file_path)
    md_file.new_header(level=1, title="Binding Preview Tables")
    for file_grouping in _binding_data:
        header_text = f"{file_grouping.file_display_name}: {file_grouping.file_path}"
        print_log(f"Writing table: \'{header_text}\'")
        # Table of contents attribute is required for a level 2 header
        md_file.new_header(level=2, title=header_text, add_table_of_contents="n")

        arranged_bindings = ["Name", "Parameters", "Return Type", "Raw Function"]
        for func in file_grouping.functions:
            param_table = build_param_table(func.params)
            arranged_bindings.extend([
                func.name,
                param_table,
                func.return_type_name,
                func.raw_function_def
            ])

        md_file.new_table(
            columns=4,
            rows=len(file_grouping.functions) + 1,
            text=arranged_bindings,
            text_align="center"
        )

    md_file.new_paragraph(text="Generated using mdutils", bold_italics_code='i')
    md_file.create_md_file()
    print_log(f"Done writing file: \'{file_path}.md\'")


# ================================================================================================================
# ================================================================================================================

def generate_preview_bindings(_config_file_path: str, _target_directory: str, _origin_directory: str):
    json_config_data = load_config_file(_config_file_path, _origin_directory, CONFIG_BINDONLY_SCHEMA)
    widget_data = json_config_data.get("widgets")
    print("\n")
    print_log(f"Compiling Bindings from Widgets...")
    
    binding_data = compile_bindings(widget_data, _origin_directory)
    write_markdown_file(binding_data, _target_directory)

def main(_config_file_path: str, _target_directory: str, _origin_directory: str, _clear_generated: bool):
    print_log(f"Using config file: {_config_file_path}")
    json_config_data = load_config_file(_config_file_path, _origin_directory)
    print_log(f"Verified config file")
    print_log(f"Verifying file contents")    
    verify_widget_contents(json_config_data.get("widgets"), _origin_directory)
    print("\n")
    print_log(f"Generating widget bindings...")
    make_output_directory(_clear_generated)
    linker_widget_data = compile_config_widget_files(json_config_data.get("widgets"), _origin_directory, _target_directory)
    make_target_directories(linker_widget_data, _target_directory)
    file_map = build_widget_file_map(linker_widget_data)
    
    transpile_target_files(file_map, _origin_directory, _target_directory)

    transpile_binding_files(
        file_map,
        _origin_directory + json_config_data.get("personality").get("scriptBindings"),
        _target_directory
    )

    write_linker_file_header(linker_widget_data, _target_directory)
    print_log(f"Generated \'linker.h\'.")
    write_linker_file_main(linker_widget_data, _target_directory)
    print_log(f"Generated \'linker.c\'.")

# ================================================================================================================
# ================================================================================================================


if __name__ == '__main__':
    start_ts = time.time()

    parser = argparse.ArgumentParser(description='Configuration Tool for WaifuWatch V.1')
    parser.add_argument(
        '-c', '--config',
        help="Path pointing to a custom JSON config file.",
        action="store",
        default="./config.json",
    )
    parser.add_argument(
        '-p', '--preview-bindings',
        help="Run generate-preview-bindings subprogram.",
        action="store_const",
        const=True,
        default=False
    )
    parser.add_argument(
        '-t', '--target-dir',
        help="Specify the directory in which configured files will be written.",
        action="store",
        default="./generated"
    )
    parser.add_argument(
        '-o', '--origin-dir',
        help="Specify the directory in which the mod directories are located.",
        action="store",
        default="./mods"
    )
    parser.add_argument(
        '-nct', '--no-clear-target',
        help="Indicate that the target directory should NOT be cleared of existing files by the tool.",
        action="store_const",
        const=False,
        default=True
    )

    args = parser.parse_args()

    if args.preview_bindings == True:
        generate_preview_bindings(args.config, args.target_dir, args.origin_dir)
    else:
        main(args.config, args.target_dir, args.origin_dir, args.no_clear_target)

    end_ts = time.time()
    print("\nFinished. Completed in {:2f} seconds.".format(end_ts - start_ts))

