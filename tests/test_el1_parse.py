"""Tests for parsing .el1 files and comparing with expected data."""

from __future__ import annotations

from datetime import UTC, datetime
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

    # Check data for Page.dat
    pages_data = parsed_data.entries[3]
    pages = pages_data.pages
    check.equal(pages_data.num_entries, len(pages))
    expected_page_numbers = list(range(1, pages_data.num_entries + 1))
    check.equal([page.page_num for page in pages], expected_page_numbers)
    check.equal([page.page_num_ for page in pages], expected_page_numbers)
    expected_frames_per_page = [len(page["frames"]) for page in expected_data["pages"]]
    check.equal([page.num_frames for page in pages], expected_frames_per_page)

    check.equal(len(parsed_data.entries[4]), sizes[4])  # Object.dat
    check.equal(len(parsed_data.entries[5]), sizes[5])  # Photo.dat
    check.equal(len(parsed_data.entries[6]), sizes[6])  # Memo.dat
    check.equal(len(parsed_data.entries[7]), sizes[7])  # Text.dat
    check.equal(len(parsed_data.entries[8]), sizes[8])  # Calender.dat
    check.equal(len(parsed_data.entries[9]), sizes[9])  # CalenderBase.dat
    check.equal(len(parsed_data.entries[10]), sizes[10])  # PhotoList.dat

    # Check data for PhotoFile.dat
    photo_file_data = parsed_data.entries[11]
    expected_photo_filenames = {
        frame["image"]
        for page in expected_data["pages"]
        for frame in page["frames"]
        if "image" in frame
    }
    expected_num_photos = len(expected_photo_filenames)
    check.equal(len(photo_file_data.photos), expected_num_photos)
    check.equal(photo_file_data.num_photos, expected_num_photos)
    for photo_index, photo in enumerate(photo_file_data.photos, start=1):
        check.equal(photo.photo_id, photo_index)
        check_is_cache_path(photo.cache_dir_path)
        check_is_path(photo.origin_dir_path)
        check_is_cache_path(photo.cache_dir_path2)
        check.between(
            photo.timestamp,
            datetime(2025, 1, 1, tzinfo=UTC),
            datetime(2030, 1, 1, tzinfo=UTC),
        )
        path = el1_file.with_suffix(".el1.Data") / photo.cache_filename
        check.equal(photo.filesize, path.stat().st_size)
    cache_filenames = {photo.cache_filename for photo in photo_file_data.photos}
    origin_filenames = {photo.origin_filename for photo in photo_file_data.photos}
    cache_filenames2 = {photo.cache_filename2 for photo in photo_file_data.photos}
    check.equal(cache_filenames, expected_photo_filenames)
    check.equal(origin_filenames, expected_photo_filenames)
    check.equal(cache_filenames2, expected_photo_filenames)

    check.equal(len(parsed_data.entries[12]), sizes[12])  # ExpImg.dat


@check.check_func
def check_is_path(s: str) -> None:
    """Check if the given string is a valid absolute Windows file or directory path."""
    assert s[0].isascii()
    assert s[0].isupper()
    assert s[1:3] == ":\\"


@check.check_func
def check_is_cache_path(s: str) -> None:
    """Check if the given string is a valid photo cache directory path."""
    check_is_path(s)
    assert s[-1] == "\\"
    parts = s[3:-1].split("\\")
    assert "Canon Easy-PhotoPrint EX" in parts
    assert "Cache" in parts
