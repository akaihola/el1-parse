"""Data structure for a ``Page.dat`` entry in the ``.el1`` file."""

from construct import (
    Array,
    Check,
    Const,
    Int16ul,
    Int32sl,
    Int32ul,
    OneOf,
    Padded,
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
    "mystery_pointer" / Const(13676, Int32ul),  # some kind of a pointer?
    Check(lambda ctx: this.mystery_pointer < ctx._._.entry_table[ctx._index].size),  # noqa: SLF001
    "software" / Const("Canon Easy-LayoutPrint", PaddedString(0x64, "ascii")),
    "unknown5" / Const(4, Int32ul),
    "unknown6" / Const(0, Int32ul),
    "data_array_type" / Const("RS_PAGE", PaddedString(0x8, "ascii")),
    Padding(0x194),  # Header padding
    "pages"
    / Array(
        this.num_entries,
        Padded(
            0x3570,
            Struct(
                "page_num" / Int32ul,
                "page_num_" / Int32ul,
                "unknown2" / OneOf(Int32sl, {-5, 0}),
                "unknown3" / OneOf(Int16ul, range(59)),
                "mystery_pointer" / OneOf(Int16ul, {0, 0x402A, 16424, 16425}),
                "num_frames" / Int32ul,
                "frames"
                / Array(
                    this.num_frames,
                    Struct(
                        "unknown1" / OneOf(Int32ul, {0, 2}),
                        # X coordinate of the left of the frame, assuming an uncropped
                        # image center aligned in the frame:
                        "left" / Int32ul,
                        # Y coordinate of the top of the frame, assuming an uncropped
                        # image center aligned in the frame:
                        "top" / Int32ul,
                        "width" / Int32ul,
                        "height" / Int32ul,
                        "unknown2" / Const([0] * 6, Array(6, Int32ul)),
                        "unknown3" / OneOf(Int32ul, {0, 540}),
                        "unknown4" / OneOf(Int32ul, {0, 3}),
                        "unknown5" / OneOf(Int32ul, {0, 2}),
                        "unknown6" / Const([0] * 7, Array(7, Int32ul)),
                        "unknown7" / OneOf(Int32ul, {0, 1}),
                        "unknown8" / OneOf(Int32sl, set(range(2, 128)) | {-1}),
                    ),
                ),
            ),
        ),
    ),
)
