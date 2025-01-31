import re

import pytest

from src.configs import WEBSITES
from src.core import APIKeyLeakageScanner
from tests import FILES_DIR


@pytest.mark.parametrize("input_file, expected_file", [
    (FILES_DIR.joinpath("code-list1.html"), FILES_DIR.joinpath("code-list1-expected.txt")),
])
def test_get_keys_from_code_list(input_file, expected_file):
    actual = APIKeyLeakageScanner(WEBSITES[0]).get_keys_from_code_list(
        input_file.read_text(),
        re.compile(WEBSITES[0]["regexes"][0], re.IGNORECASE)
    )
    expected = expected_file.read_text().splitlines()
    actual.sort()
    expected.sort()
    assert actual == expected
