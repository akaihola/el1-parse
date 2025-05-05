"""Test the ``FileTime`` adapter for parsing and building Windows FILETIME values."""

from datetime import UTC, datetime

import pytest

from el1_parse.structures.filetime_adapter import FileTime


def test_parse():
    """Test the parsing of Windows FILETIME bytes into a datetime object."""
    win_timestamp = b"\xe2\xf4B\xfb\xd3\xb6\xdb\x01"

    # Parse the bytes into a datetime object
    parsed_dt = FileTime.parse(win_timestamp)

    # Print the parsed datetime (using the original format for comparison)
    # Note: The parsed_dt will be timezone-aware UTC by default due to the adapter code
    # We'll format it without timezone info for comparison with original script output
    assert parsed_dt == datetime(2025, 4, 26, 17, 52, 30, 738557, tzinfo=UTC)


@pytest.mark.parametrize(
    ("dt", "expected"),
    [
        ((2025, 4, 26, 17, 52, 30, 738557), b"\xf0\xf4B\xfb\xd3\xb6\xdb\x01"),
        ((2023, 10, 27, 10, 30, 0, 500000), b"@\xcf\x20\x8a\xc0\x08\xda\x01"),
    ],
)
def test_build(dt: tuple[int, int, int, int, int, int, int], expected: str) -> None:
    """Test the building of a datetime object into Windows FILETIME bytes."""
    built_bytes = FileTime.build(datetime(*dt, tzinfo=UTC))
    assert built_bytes == expected
