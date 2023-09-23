from pathlib import Path
import sys
import os
import re

import pytest

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent) 

import configure
from configure import ImageLink

test_valid_image_replacement_one_image_links =  [
    # ref, height, width
    (
        'tests/data/imageone.png',
        '84',
        '84'
    ),
    (
        'tests/data/imageone.png',
        '84',
        '84'
    )

]

REPLACED_IMAGE_PATTERN = r"const([\s\t]+)UWORD([\s\t]+)\w+([\s\t]+)=([\s\t]+)([\w]+)(;){1}" 


def verify_images_replaced(_image_var_names: list[str]):
    print(_image_var_names)

def collect_images_replaced(_file_data: str) -> list[str]:
    var_list = []
    working_data = _file_data
    while(x:=re.search(REPLACED_IMAGE_PATTERN, working_data)) != None:
        var_slice = working_data[x.span()[0]:x.span()[1]]
        var_name = var_slice.split("=")[-1].strip(" ;")
        var_list.append(var_name)
        working_data = working_data[x.span()[1]:]
    
    return var_list

# ================================================================================================================
# ================================================================================================================

def test_valid_image_replacement_one():
    c_file = configure.read_file_raw("tests/data/image_replace_one.c")
    new_c_file, _ = configure.replace_image_declarations(c_file, "tests/data")
    assert re.search(configure.TRANSLATE_IMAGE_DEFINITION_PATTERN, new_c_file) == None
    # verify_images_replaced(new_c_file)
    image_names = collect_images_replaced(new_c_file)
