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
    "photo_dat_unknown1" / Const(3, Int32ul),
    "photo_dat_unknown2" / Const(0, Int32ul),
    "num_photos" / Int32ul,
    "photo_dat_unknown3"
    / Int32ul,  # sometimes same as num_photos, sometimes more (6->10)
    "mystery_pointer" / Const(3464, Int32ul),  # some kind of a pointer?
    Check(lambda ctx: this.mystery_pointer < ctx._._._.entry_table[ctx._index].size),  # noqa: SLF001
    "software" / Const("Canon Easy-LayoutPrint", PaddedString(0x64, "ascii")),
    "photo_dat_unknown5" / Const(3, Int32ul),
    "photo_dat_unknown6" / Const(2, Int32ul),
    "data_array_type" / Const("RS_PHOTO_OBJ", PaddedString(0x10, "ascii")),
    Padding(0x18C),
    "photos"
    / Array(
        this.num_photos,
        Struct(
            "photo_id" / Int32ul,
            "photo_unknown0" / OneOf(Int64sl, {-1} | set(range(1, 55))),
            # photo_unknown1 is typically 2 * photo_unknown0 + 4
            "photo_unknown1" / OneOf(Int32ul, range(1, 127)),
            # photo_unknown2 is typically photo_unknown0 + 2, or photo_unknown1 / 2
            "photo_unknown2" / OneOf(Int32ul, range(1, 58)),
            Check(this.photo_unknown1 >= this.photo_unknown2),
            "photo_unknown3" / Const([1, 1, 0x17], Array(3, Int32ul)),
            "photo_unknown4" / OneOf(Int32ul, {1, 2}),
            "photo_unknown5" / Const([0, 0, 0, 0], Array(4, Int32ul)),
            "photo_unknown6" / Const([1, 0, 1, 4, 2], Array(5, Int32ul)),
            "photo_unknown7" / OneOf(Int32ul, {0x000200DA, 0x000600AC, 0x00070050}),
            "photo_unknown8" / OneOf(Int32ul, {6, 31, 38}),
            "photo_unknown9" / Const([0] * 0x1E, Array(0x1E, Int32ul)),
            "photo_unknown10" / Const(0x20C0, Int32ul),
            "photo_unknown11" / Const(0, Int32ul),
            "photo_unknown12" / OneOf(Int32ul, {0, 1}),  # 0 = uncropped, 1 = cropped
            "width_px" / Int32ul,
            "height_px" / Int32ul,
            "crop_left" / Int32ul,  # largest seen = 397
            "crop_top" / Int32ul,  # largest seen = 413
            "photo_unknown13" / OneOf(Int32ul, {0, 1}),  # 1 = uncropped, 0 = cropped
            "photo_unknown14" / Const(0x70001000, Int32ul),
            "photo_unknown15" / Const(0, Int32ul),
            "photo_unknown16" / OneOf(Int32ul, [0, 0x70001000]),
            "photo_unknown17" / Const(0, Int32ul),
            "photo_unknown18"
            / OneOf(PaddedString(0x208, "utf16"), {"frame000_preview.bmp", ""}),
            "photo_unknown19" / Const(0xA78 * b"\0", Bytes(0xA78)),
            "photo_unknown20" / OneOf(Int32ul, {0, 3}),
            "photo_unknown21" / Const(0xC * b"\0", Bytes(0xC)),
            "photo_id_repeat" / Int32ul,
            Check(this.photo_id_repeat == this.photo_id),
        ),
    ),
)
