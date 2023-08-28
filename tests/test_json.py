from pathlib import Path
import sys
import os
import re

import pytest

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent) 

import configure
from configure import MissingAttributeType, MissingAttribute

EXPECTED_FN_NAMES_ONE = [
        r"^(.+[ ]+Test_One_display\(.*\)[ ]*[;{]{1})$",
        r"^(.+[ ]+Test_One_thumbnail\(.*\)[ ]*[;{]{1})$",
        r"^(.+[ ]+Test_One_settings\(.*\)[ ]*[;{]{1})$",
        r"^(.+[ ]+Test_One_update\(.*\)[ ]*[;{]{1})$"
]

EXPECTED_FN_NAMES_TWO = [
        r"^(.+[ ]+Test_Two_display\(.*\)[ ]*[;{]{1})$",
        r"^(.+[ ]+Test_Two_thumbnail\(.*\)[ ]*[;{]{1})$",
        r"^(.+[ ]+Test_Two_settings\(.*\)[ ]*[;{]{1})$",
        r"^(.+[ ]+Test_Two_update\(.*\)[ ]*[;{]{1})$"
]



def apply_schema_to_file(_file_data: str, _schema: list[str]) -> list[MissingAttributeType]:
    split_data = _file_data.split("\n")
    for pattern in _schema:
        flag = False
        for line in split_data:
            if re.search(pattern, line) != None:
                flag = True
                break;
        if flag == False:
            return False
    return True

# ================================================================================================================
# ================================================================================================================

"""
Uses test_one.json
Correct File Translation Test
"""
def test_valid_config_file_one():
    data = configure.load_config_file("tests/test_one.json", "tests/mods")
    configure.verify_widget_contents(data.get("widgets"), "tests/mods")
    configure.make_output_directory(True, "/tests/generated")
    widget_data = configure.compile_linker_widget_data(data.get("widgets"), "tests/mods", "tests/generated")
    configure.make_target_directories(widget_data, "tests/generated")
    configure.translate_target_files(widget_data, "tests/generated")

    assert Path("tests/generated/Test_One").is_dir()
    assert Path("tests/generated/Test_Two").is_dir()

    assert Path("tests/generated/Test_One/testone.h").is_file()
    assert Path("tests/generated/Test_One/testone.c").is_file()

    assert Path("tests/generated/Test_Two/testtwo.h").is_file()
    assert Path("tests/generated/Test_Two/testtwo.c").is_file()

    data_one_h = configure.read_file_raw("tests/generated/Test_One/testone.h")
    data_one_c = configure.read_file_raw("tests/generated/Test_One/testone.c")
    data_two_h = configure.read_file_raw("tests/generated/Test_Two/testtwo.h")
    data_two_c = configure.read_file_raw("tests/generated/Test_Two/testtwo.c")

    assert apply_schema_to_file(data_one_h, EXPECTED_FN_NAMES_ONE)
    assert apply_schema_to_file(data_one_c, EXPECTED_FN_NAMES_ONE)
    assert apply_schema_to_file(data_two_h, EXPECTED_FN_NAMES_TWO)
    assert apply_schema_to_file(data_two_c, EXPECTED_FN_NAMES_TWO)

# ================================================================================================================
# ================================================================================================================

"""
Uses test_two.json
Missing Attributes Test
Missing attribute -> displayName
"""
def test_bad_config_one():
    with pytest.raises(MissingAttribute) as attr:
        data = configure.load_config_file("tests/test_two.json", "tests/mods")
    