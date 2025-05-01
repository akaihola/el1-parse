"""Convert Windows FILETIME to/from Python datetime."""

from datetime import UTC, datetime

from construct import Adapter, Container, Int64ul, Subconstruct, ValidationError

WINDOWS_TICKS = 10_000_000  # 100 nanoseconds or .1 microseconds
WINDOWS_EPOCH = datetime(1601, 1, 1, 0, 0, 0, tzinfo=UTC)
POSIX_EPOCH = datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC)

EPOCH_DIFF_SECS = (POSIX_EPOCH - WINDOWS_EPOCH).total_seconds()

WINDOWS_TICKS_TO_POSIX_EPOCH_TICKS = int(EPOCH_DIFF_SECS * WINDOWS_TICKS)

FILETYPE_SIZE_BYTES = 8


class FileTimeAdapter(Adapter):
    """Convert between Windows FILETIME and Python ``datetime``.

    Windows FILETIME is 64-bit little-endian unsigned long long.

    Assumes the FILETIME represents UTC time, consistent with datetime.timestamp().
    Converts the raw 64-bit integer (representing 100-nanosecond intervals
    since Jan 1, 1601 UTC) to/from a datetime object.
    """

    def __init__(self, subcon: Subconstruct) -> None:
        """Initialize the ``FileTimeAdapter`` object."""
        super().__init__(subcon)
        if subcon.sizeof() != FILETYPE_SIZE_BYTES:
            msg = "FileTimeAdapter must wrap an 8-byte construct (e.g., Int64ul)"
            raise ValueError(msg)

    def _decode(self, obj: int, context: Container, path: str) -> datetime:  # noqa: ARG002
        """Convert Windows FILETIME integer (obj) to datetime.

        :param obj: the integer parsed by the underlying construct (Int64ul).
        """
        winticks = obj
        seconds_since_posix_epoch = (
            winticks - WINDOWS_TICKS_TO_POSIX_EPOCH_TICKS
        ) / WINDOWS_TICKS
        return datetime.fromtimestamp(seconds_since_posix_epoch, tz=UTC)

    def _encode(self, obj: datetime, context: Container, path: str) -> int:  # noqa: ARG002
        """Convert datetime object (obj) to Windows FILETIME integer.

        :return: the integer expected by the underlying construct (Int64ul).
        """
        if not isinstance(obj, datetime):
            msg = f"Expected datetime object, got {type(obj)}"
            raise ValidationError(msg, path=path)

        if obj.tzinfo is None:
            dt_utc = obj.replace(tzinfo=UTC)
        elif obj.tzinfo != UTC:
            dt_utc = obj.astimezone(UTC)
        else:
            dt_utc = obj

        # datetime.timestamp() gives seconds since POSIX epoch (UTC)
        seconds_since_posix_epoch = dt_utc.timestamp()

        # Calculate total seconds since 1601-01-01 UTC
        seconds_since_win_epoch = seconds_since_posix_epoch + EPOCH_DIFF_SECS

        # Convert seconds to 100ns intervals and round to nearest integer
        return round(seconds_since_win_epoch * WINDOWS_TICKS)


FileTime = FileTimeAdapter(Int64ul)
