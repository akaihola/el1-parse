"""Parse ``.el1`` files."""

import argparse
import logging
from pathlib import Path

from el1_parse.structures.el1 import el1, el1_dat_extract

logger = logging.getLogger(__name__)


def main() -> None:
    """Parse ``.el1`` files."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description="Parse .el1 files")
    parser.add_argument("input_file", type=Path, help="Path to the .el1 file to parse")
    parser.add_argument(
        "-x", "--extract", action="store_true", help="Only extract raw .dat files"
    )
    opts = parser.parse_args()
    if opts.extract:
        extract_raw_dat_files(opts.input_file)
    else:
        _ = el1.parse(opts.input_file.read_bytes())
        logger.info("Parsed %s successfully", opts.input_file)


def extract_raw_dat_files(input_file: Path) -> None:
    """Extract raw ``.dat`` files into a directory."""
    data = el1_dat_extract.parse(input_file.read_bytes())
    directory = input_file.parent / input_file.stem
    directory.mkdir(parents=True, exist_ok=True)
    for entry_index, entry_data in enumerate(data.entries):
        entry_name = data.entry_table[entry_index].name
        output_path = directory / entry_name
        output_path.write_bytes(entry_data)
        logger.info("Extracted %s to %s", entry_name, output_path)
