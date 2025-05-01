"""Data structure for entry metadata in the ``.el1`` file."""

from construct import Int32ul, PaddedString, Probe, Struct, this

entry_metadata = Struct(
    "entry_type" / Int32ul,  # entry type ID (101, 201, 202, ...)
    #Probe(this.entry_type),
    "offset" / Int32ul,
    #Probe(this.offset),
    "size" / Int32ul,
    "name" / PaddedString(0x104, "ascii"),  # null-terminated ASCII filename
)
