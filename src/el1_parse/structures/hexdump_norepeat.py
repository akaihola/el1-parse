"""Hexdump adapter for ``construct`` that suppresses repeated lines."""

from typing import Any

from construct import Container
from construct.core import Adapter

ASCII_PRINTABLE_MIN = 0x20  # Space
ASCII_PRINTABLE_MAX = 0x7E  # Tilde (~)


class HexDumpRepeatSuppressedBytes:
    """Bytes whose string representation suppresses repeated hexdump lines."""

    def __init__(self, obj: bytes, width: int = 16) -> None:
        """Initialize the HexDumpRepeatSuppressedBytes object."""
        self.data = obj
        self._width = width

    def __str__(self) -> str:
        """Return a string representation of the bytes object."""
        return hexdump_repeat_suppressed(self.data, width=self._width)


class HexDumpRepeatSuppressedDict:
    """Dict whose string representation suppresses repeated hexdump lines."""

    def __init__(self, obj: bytes, width: int = 16) -> None:
        """Initialize the HexDumpRepeatSuppressedDict with a dict and width."""
        self.data = obj
        self._width = width

    def __str__(self) -> str:
        """Return a string representation of the data in the dictionary."""
        data = self.data.get("data", b"")
        return hexdump_repeat_suppressed(data, width=self._width)


def hexdump_repeat_suppressed(data: bytes, width: int = 16, group: int = 2) -> str:
    """Produce hexdump, repeated lines as '*', as in the Unix hexdump tool."""
    lines = []
    star = False
    last_row = None
    for offset in range(0, len(data), width):
        row = data[offset : offset + width]
        if row == last_row:
            if not star:
                lines.append("*")
                star = True
            continue
        star = False
        # Hex part
        hexgroups = [
            "".join(f"{b:02x}" for b in row[i : i + group])
            for i in range(0, len(row), group)
        ]
        hexstr = " ".join(hexgroups)
        # Pad hexstr to fixed width
        n_groups = width // group
        hexstr = hexstr.ljust(n_groups * (group * 2 + 1) - 1)
        # ASCII part
        asciistr = "".join(
            (chr(b) if ASCII_PRINTABLE_MIN <= b <= ASCII_PRINTABLE_MAX else ".")
            for b in row
        )
        # Line with offset, hex, and ascii
        lines.append(f"{offset:07x}  {hexstr}  {asciistr}")
        last_row = row
    return "\n".join(lines)


class HexDumpRepeatSuppress(Adapter):
    """Like construct's HexDump adapter, but collapses repeated rows to ``*``."""

    def __init__(self, subcon: Any, width: int = 16) -> None:  # noqa: ANN401
        """Initialize the HexDumpRepeatSuppress adapter."""
        super().__init__(subcon)
        self._width = width

    def _decode(
        self,
        obj: Any,  # noqa: ANN401
        context: Container,  # noqa: ARG002
        path: str,  # noqa: ARG002
    ) -> HexDumpRepeatSuppressedBytes | HexDumpRepeatSuppressedDict:
        if isinstance(obj, bytes):
            return HexDumpRepeatSuppressedBytes(obj, width=self._width)
        if isinstance(obj, dict):
            return HexDumpRepeatSuppressedDict(obj, width=self._width)
        return obj

    def _encode(self, obj: Any, context: Container, path: str) -> Any:  # noqa: ANN401, ARG002
        return obj
