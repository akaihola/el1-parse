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
            "unknown0" / OneOf(Int64sl, {-1} | set(range(1, 55))),
            # unknown1 is typically 2 * unknown0 + 4
            "unknown1" / OneOf(Int32ul, range(1, 127)),
            # unknown2 is typically unknown0 + 2, or unknown1 / 2
            "unknown2" / OneOf(Int32ul, range(1, 58)),
            Check(this.unknown1 >= this.unknown2),
            "unknown3" / Const([1, 1, 0x17], Array(3, Int32ul)),
            "unknown4" / OneOf(Int32ul, {1, 2}),
            "unknown5" / Const([0, 0, 0, 0], Array(4, Int32ul)),
            "unknown6" / Const([1, 0, 1, 4, 2], Array(5, Int32ul)),
            "unknown7" / OneOf(Int32ul, {0x000200DA, 0x000600AC, 0x00070050}),
            "unknown8" / OneOf(Int32ul, {6, 31, 38}),
            "unknown9" / Const([0] * 0x1E, Array(0x1E, Int32ul)),
            "unknown10" / Const(0x20C0, Int32ul),
            "unknown11" / Const(0, Int32ul),
            "unknown12" / OneOf(Int32ul, {0, 1}),  # 0 = uncropped, 1 = cropped
            "width_px" / Int32ul,
            "height_px" / Int32ul,
            "crop_left" / Int32ul,  # largest seen = 397
            "crop_top" / Int32ul,  # largest seen = 413
            "unknown13" / OneOf(Int32ul, {0, 1}),  # 1 = uncropped, 0 = cropped
            "unknown14" / Const(0x70001000, Int32ul),
            "unknown15" / Const(0, Int32ul),
            "unknown16" / OneOf(Int32ul, [0, 0x70001000]),
            "unknown17" / Const(0, Int32ul),
            "unknown18"
            / OneOf(PaddedString(0x208, "utf16"), {"frame000_preview.bmp", ""}),
            "unknown19" / Const(0xA78 * b"\0", Bytes(0xA78)),
            "unknown20" / OneOf(Int32ul, {0, 3}),
            "unknown21" / Const(0xC * b"\0", Bytes(0xC)),
            "photo_id_repeat" / Int32ul,
            Check(this.photo_id_repeat == this.photo_id),
        ),
    ),
)
