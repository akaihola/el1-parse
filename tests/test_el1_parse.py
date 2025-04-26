"""Tests for parsing .el1 files and comparing with expected data."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import BaseModel
from pytest_check import check
from ruamel.yaml import YAML

from el1_parse.structures.el1 import el1


def find_expected_files() -> list[Path]:
    """Find all .expected.yaml files in the current directory."""
    expected_files = []
    # use Python 3.12 pathlib.Path.walk() to find all .expected.yaml files
    # in the current directory and its subdirectories
    samples_dir = Path(__file__).parent.parent / "samples"
    for root, _dirs, _files in samples_dir.walk():
        expected_files.extend(Path(root).glob("*.yaml"))
    return expected_files


class ExpectedFrame(BaseModel):
    """Model for expected frame in the .expected.yaml file."""

    center_x: float
    center_y: float
    filename: str | None = None
    size: str | None = None
    lock_aspect: bool | None = None
    width: float | None = None
    height: float | None = None


class ExpectedEntry(BaseModel):
    """Model for expected entry in the .expected.yaml file."""

    layout: str
    frames: list[ExpectedFrame]


SMALLEST_ENTRY_SIZE = 572


@pytest.mark.parametrize("expected_file", find_expected_files())
def test_parse_el1_file(expected_file: Path) -> None:
    """Test parsing of .el1 files against expected data."""
    # Load the expected data from the .expected.yaml file
    yaml = YAML(typ="safe")
    with expected_file.open("r") as f:
        expected_data = yaml.load(f)

    # Construct the corresponding .el1 file path
    # Note that Path.with_suffix() only strips the last suffix
    el1_file = expected_file.with_suffix("").with_suffix(".el1")

    # Parse the page data
    parsed_data = el1.parse(el1_file.read_bytes())

    # Compare the parsed data with the expected data
    check.equal(len(parsed_data.entry_table), 13)
    check.equal(
        [(entry.entry_type, entry.name) for entry in parsed_data.entry_table],
        [
            (101, "ElpData.dat"),
            (201, "CurrentBase.dat"),
            (202, "Deflay.dat"),
            (203, "Page.dat"),
            (204, "Object.dat"),
            (205, "Photo.dat"),
            (206, "Memo.dat"),
            (207, "Text.dat"),
            (208, "Calender.dat"),
            (209, "CalenderBase.dat"),
            (301, "PhotoList.dat"),
            (302, "PhotoFile.dat"),
            (501, "ExpImg.dat"),
        ],
    )
    # Offsets and sizes should form a gapless sequence
    offsets = [entry.offset for entry in parsed_data.entry_table]
    sizes = [entry.size for entry in parsed_data.entry_table]
    offset_differences = [offsets[i] - offsets[i - 1] for i in range(1, len(offsets))]
    check.equal(offset_differences, sizes[:-1])

    # Lengths of raw unparsed data entries should match sizes from the entry table
    check.equal(len(parsed_data.entries[0]), sizes[0])  # ElpData.dat
    check.equal(len(parsed_data.entries[1]), sizes[1])  # CurrentBase.dat
    check.equal(len(parsed_data.entries[2]), sizes[2])  # Deflay.dat
    page = parsed_data.entries[3]
    layout_entries = page.layout_entries
    check.equal(page.num_entries, len(page.layout_entries))
    check.equal(
        [entry.photo_id for entry in layout_entries],
        list(range(1, page.num_entries + 1)),
    )
    check.equal([entry.unknown1 for entry in layout_entries], [1])
    check.equal(len(parsed_data.entries[4]), sizes[4])  # Object.dat
    check.equal(len(parsed_data.entries[5]), sizes[5])  # Photo.dat
    check.equal(len(parsed_data.entries[6]), sizes[6])  # Memo.dat
    check.equal(len(parsed_data.entries[7]), sizes[7])  # Text.dat
    check.equal(len(parsed_data.entries[8]), sizes[8])  # Calender.dat
    check.equal(len(parsed_data.entries[9]), sizes[9])  # CalenderBase.dat
    check.equal(len(parsed_data.entries[10]), sizes[10])  # PhotoList.dat
    check.equal(len(parsed_data.entries[11]), sizes[11])  # PhotoFile.dat
    check.equal(len(parsed_data.entries[12]), sizes[12])  # ExpImg.dat
