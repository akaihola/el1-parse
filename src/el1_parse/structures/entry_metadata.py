"""Data structure for entry metadata in the ``.el1`` file."""

from construct import Int32ul, PaddedString, Struct, this

entry_metadata = Struct(
    "entry_type" / Int32ul,  # entry type ID (101, 201, 202, ...)
    "offset" / Int32ul,
    "size" / Int32ul,
    "name" / PaddedString(0x104, "ascii"),  # null-terminated ASCII filename
)
