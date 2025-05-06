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
from el1_parse.structures.hexdump_norepeat import HexDumpRepeatSuppress
from el1_parse.structures.page import page
from el1_parse.structures.photo import photo
from el1_parse.structures.photo_file import photo_file


def hexdump_unparsed(width: int = 16) -> Construct:
    """Create a construct for a user-defined format (UDF)."""
    return HexDumpRepeatSuppress(
        Bytes(lambda ctx: ctx._.entry_table[ctx._index].size),  # noqa: SLF001
        width=width,
    )


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
        {
            "ElpData.dat": hexdump_unparsed(32),
            "CurrentBase.dat": hexdump_unparsed(32),
            "Deflay.dat": hexdump_unparsed(84),
            "Page.dat": page,
            "Object.dat": hexdump_unparsed(88),
            "Photo.dat": photo,
            "Memo.dat": hexdump_unparsed(293),
            "Text.dat": hexdump_unparsed(28),
            "Calender.dat": hexdump_unparsed(37),
            "CalenderBase.dat": hexdump_unparsed(37),
            "PhotoList.dat": hexdump_unparsed(36),
            "PhotoFile.dat": photo_file,
            "ExpImg.dat": hexdump_unparsed(32),
        },
    )
)
el1_dat_extract = make_parser(hexdump_unparsed(32))
