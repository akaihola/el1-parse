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
    Struct,
    this,
)

photo = Struct(
    "magic" / Const("Data Array Manager", PaddedString(0x20, "ascii")),
    "unknown1" / Const(3, Int32ul),
    "unknown2" / Const(0, Int32ul),
    "num_photos" / Int32ul,
    "unknown3" / Int32ul,  # sometimes same as num_photos, sometimes more (6->10)
    "mystery_pointer" / Const(3464, Int32ul),  # some kind of a pointer?
    Check(lambda ctx: this.mystery_pointer < ctx._._.entry_table[ctx._index].size),  # noqa: SLF001
    "software" / Const("Canon Easy-LayoutPrint", PaddedString(0x64, "ascii")),
    "unknown5" / Const(3, Int32ul),
    "unknown6" / Const(2, Int32ul),
    "data_array_type" / Const("RS_PHOTO_OBJ", PaddedString(0x10, "ascii")),
    Padding(0x18C),
    "photos"
    / Array(
        this.num_photos,
        Struct(
            "photo_id" / Int32ul,
            "unknown0"
            / OneOf(
                Int64sl, {-1, 25, 26, 27, 28, 29, 30, 32, 34, 35} | set(range(1, 24))
            ),
            # unknown1 is typically 2 * unknown0 + 4
            "unknown1"
            / OneOf(
                Int32ul,
                set(range(3, 15))
                | set(range(16, 51, 2))
                | set(range(45, 52, 2))
                | {1, 19, 37, 39, 57, 59, 61},
            ),
            # unknown2 is typically unknown0 + 2
            "unknown2" / OneOf(Int32ul, range(1, 24)),
            Check(this.unknown1 >= this.unknown2),
            "unknown3" / Const([1, 1, 0x17], Array(3, Int32ul)),
            "unknown4" / OneOf(Int32ul, {1, 2}),
            "unknown5" / Const([0, 0, 0, 0], Array(4, Int32ul)),
            "unknown6" / Const([1, 0, 1, 4, 2, 0x000200DA, 0x26], Array(7, Int32ul)),
            "unknown7" / Const([0] * 0x1E, Array(0x1E, Int32ul)),
            "unknown8" / Const(0x20C0, Int32ul),
            "unknown9" / Const(0, Int32ul),
            "unknown10" / OneOf(Int32ul, {0, 1}),  # 0 = uncropped, 1 = cropped
            "width_px" / Int32ul,
            "height_px" / Int32ul,
            "crop_left" / OneOf(Int32ul, {0, 4, 244}),  # 0 = uncropped, 4 = cropped),
            "crop_top"
            / OneOf(Int32ul, {0, 14, 41, 46, 413}),  # 0 = uncropped, 41/46 = cropped
            "unknown11" / OneOf(Int32ul, {0, 1}),  # 1 = uncropped, 0 = cropped
            "unknown12" / Const(0x70001000, Int32ul),
            "unknown13" / Const(0, Int32ul),
            "unknown14" / OneOf(Int32ul, [0, 0x70001000]),
            "unknown15" / Const(0, Int32ul),
            "unknown16"
            / OneOf(PaddedString(0x208, "utf16"), {"frame000_preview.bmp", ""}),
            "unknown17" / Const(0xA78 * b"\0", Bytes(0xA78)),
            "unknown19" / OneOf(Int32ul, {0, 3}),
            "unknown20" / Const(0xC * b"\0", Bytes(0xC)),
            "photo_id_repeat" / Int32ul,
            Check(this.photo_id_repeat == this.photo_id),
        ),
    ),
)
