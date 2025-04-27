"""Data structure for a ``PhotoFile.dat`` entry in the ``.el1`` file."""

from construct import (
    Array,
    Bytes,
    Check,
    Const,
    Int32ul,
    Int64sl,
    OneOf,
    PaddedString,
    Padding,
    Probe,
    Struct,
    this,
)

from el1_parse.structures.filetime_adapter import FileTime

photo = Struct(
    "magic" / Const("Data Array Manager", PaddedString(0x20, "ascii")),
    "unknown1" / Const(3, Int32ul),
    "unknown2" / Const(0, Int32ul),
    "num_frames" / Int32ul,
    "unknown3" / Int32ul,  # sometimes same as num_frames, sometimes more (6->10)
    "mystery_pointer" / Const(3464, Int32ul),  # some kind of a pointer?
    Check(lambda ctx: this.mystery_pointer < ctx._._.entry_table[ctx._index].size),  # noqa: SLF001
    "software" / Const("Canon Easy-LayoutPrint", PaddedString(0x64, "ascii")),
    "unknown5" / Const(3, Int32ul),
    "unknown6" / Const(2, Int32ul),
    "data_array_type" / Const("RS_PHOTO_OBJ", PaddedString(0x10, "ascii")),
    Padding(0x18C),
    "frames"
    / Array(
        this.num_frames,
        Struct(
            "frame_id" / Int32ul,
            "unknown0" / OneOf(Int64sl, {-1, 1, 2}),
            "unknown1" / OneOf(Int32ul, {1, 3, 5, 7, 9, 11, 13, 19}),
            "unknown2" / OneOf(Int32ul, {1, 2, 3, 4, 5, 6, 7, 10}),
            Check(this.unknown1 == 1 + 2 * (this.unknown2 - 1)),
            Const([1, 1, 0x17, 1], Array(4, Int32ul)),
            Const([0, 0, 0, 0], Array(4, Int32ul)),
            Const([1, 0, 1, 4, 2, 0x000200DA, 0x26], Array(7, Int32ul)),
            Const([0] * 0x1E, Array(0x1E, Int32ul)),
            Const(0x20C0, Int32ul),
            Const([0, 0], Array(2, Int32ul)),
            "width_px" / Int32ul,
            "height_px" / Int32ul,
            Const([0, 0, 1, 0x70001000, 0, 0x70001000, 0], Array(7, Int32ul)),
            Const("frame000_preview.bmp", PaddedString(0x208, "utf16")),
            Const(0xA78 * b"\0", Bytes(0xA78)),
            Const(3, Int32ul),
            Const(0xC * b"\0", Bytes(0xC)),
            "frame_id_repeat" / Int32ul,
            Check(this.frame_id_repeat == this.frame_id),
        ),
    ),
)
