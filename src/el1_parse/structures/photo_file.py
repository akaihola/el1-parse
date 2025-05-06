"""Data structure for a ``PhotoFile.dat`` entry in the ``.el1`` file."""

from construct import (
    Array,
    Check,
    Const,
    Int32ul,
    OneOf,
    PaddedString,
    Padding,
    Struct,
    this,
)

from el1_parse.structures.filetime_adapter import FileTime

photo_file = Struct(
    "magic" / Const("Data Array Manager", PaddedString(0x20, "ascii")),
    "photo_file_dat_unknown1" / Const(3, Int32ul),
    "photo_file_dat_unknown2" / Const(0, Int32ul),
    "num_photos" / Int32ul,
    "photo_file_dat_unknown3" / Int32ul,
    Check(this.num_photos <= this.photo_file_dat_unknown3),
    "mystery_pointer" / Const(3152, Int32ul),  # some kind of a pointer?
    Check(lambda ctx: this.mystery_pointer < ctx._._._.entry_table[ctx._index].size),  # noqa: SLF001
    "software" / Const("Canon Easy-LayoutPrint", PaddedString(0x64, "ascii")),
    "photo_file_dat_unknown5" / Const(3, Int32ul),
    "photo_file_dat_unknown6" / Const(0, Int32ul),
    "data_array_type" / Const("ADD_PHOTO", PaddedString(0x9, "ascii")),
    Padding(0x193),  # Padding until 0x023c
    "photo_files"
    / Array(
        this.num_photos,
        Struct(
            "photo_file_id" / Int32ul,
            "num_extra_paths" / Const(2, Int32ul),
            "cache_dir_path" / PaddedString(0x208, "utf16"),
            "cache_filename" / PaddedString(0x208, "utf16"),
            "origin_dir_path" / PaddedString(0x208, "utf16"),
            "origin_filename" / PaddedString(0x208, "utf16"),
            "timestamp" / FileTime,
            "photo_file_unknown1" / Const(0, Int32ul),
            "filesize" / Int32ul,
            "cache_dir_path2" / PaddedString(0x208, "utf16"),
            "cache_filename2" / PaddedString(0x208, "utf16"),
            "photo_file_unknown2" / OneOf(Int32ul, {0, 1}),
            "more_images" / Int32ul,
            Check(lambda ctx: this.more_images == this._index < ctx._.num_photos - 1),  # noqa: SLF001
            "photo_file_id_repeat" / Int32ul,
            Check(this.photo_file_id_repeat == this.photo_file_id),
        ),
    ),
)
