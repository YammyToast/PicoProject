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

# ================================================================================================================
# ================================================================================================================

def test_valid_image_replacement_one():
    c_file = configure.read_file_raw("tests/data/image_replace_one.c")
    new_c_file = configure.replace_image_declarations(c_file, "tests/data")
    print(new_c_file)
