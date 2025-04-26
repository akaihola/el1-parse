"""Data structure for a ``Page.dat`` entry in the ``.el1`` file."""

from construct import (
    Array,
    Const,
    Int16ul,
    Int32sl,
    Int32ul,
    OneOf,
    PaddedString,
    Padding,
    Struct,
    this,
)

page = Struct(
    "magic" / Const("Data Array Manager", PaddedString(0x20, "ascii")),
    "unknown1" / Const(3, Int32ul),
    "unknown2" / Const(0, Int32ul),
    "num_entries" / Int32ul,
    "num_pages" / Int32ul,
    "unknown4" / Const(13676, Int32ul),
    "layout_name" / Const("Canon Easy-LayoutPrint", PaddedString(0x64, "ascii")),
    "unknown5" / Const(4, Int32ul),
    "unknown6" / Const(0, Int32ul),
    "page_type" / Const("RS_PAGE", PaddedString(0x8, "ascii")),
    Padding(0x194),  # Header padding
    "layout_entries"
    / Array(
        this.num_entries,
        Struct(
            "page_num" / Int32ul,
            "page_num_" / Int32ul,
            "unknown2" / Const(-5, Int32sl),
            "unknown3" / OneOf(Int16ul, {5, 7, 12, 18}),
            "unknown4" / Const(0x402A, Int16ul),
            "num_frames" / Int32ul,
            "unknown6" / Const(0, Int32ul),
            "unknown7" / OneOf(Int32ul, {0x0000B2B6, 0x00003A8F}),
            Padding(0x3570 - 7 * 4),  # Additional metadata
        ),
    ),
)
