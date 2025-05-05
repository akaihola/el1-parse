"""Data structure for ``.el1`` files."""

from construct import (
    Array,
    Bytes,
    Const,
    Construct,
    FocusedSeq,
    Int32ul,
    PaddedString,
    Seek,
    Struct,
    Switch,
    Terminated,
    this,
)

from el1_parse.structures.entry_metadata import entry_metadata
from el1_parse.structures.page import page
from el1_parse.structures.photo import photo
from el1_parse.structures.photo_file import photo_file

unparsed_dat_file = Bytes(lambda ctx: ctx._.entry_table[ctx._index].size)


def make_parser(entry_struct: Construct) -> Struct:
    """Create a parser for the ``.el1`` file format."""
    return Struct(
        "magic" / Const("File Catalog Manager", PaddedString(0x20, "ascii")),
        "unknown1" / Const(2, Int32ul),
        "unknown2" / Const(0, Int32ul),
        "num_entries" / Const(13, Int32ul),
        "entry_table" / Array(this.num_entries, entry_metadata),
        "entries"
        / Array(
            this.num_entries,
            FocusedSeq(
                "data",
                Seek(lambda ctx: ctx._.entry_table[ctx._index].offset),  # noqa: SLF001
                "data" / entry_struct,
            ),
        ),
        "end" / Terminated,
    )


el1 = make_parser(
    Switch(
        lambda ctx: ctx._.entry_table[ctx._index].name,  # noqa: SLF001
        {"Page.dat": page, "Photo.dat": photo, "PhotoFile.dat": photo_file},
        default=unparsed_dat_file,
    )
)
el1_dat_extract = make_parser(unparsed_dat_file)
