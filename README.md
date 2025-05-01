# el1-parse

This is an attempt to reverse engineer the `.el1` file format
used by photo layout software shipped with some Canon inkjet printers.

Sample `.el1` files are in `samples/`.
The photo layout software stores images files for `<filename>.el1`
in `<filename>.el1.Data/*.jpg`.
The Pytest test suite parses and verifies every `samples/*.el1` file
which has an accompanying `samples/*.yaml` file.
The `.yaml` files describe known characteristics of the samples.
Optional `samples/*.png` screenshots are provided for some `.el1` files.

The parsing rules are intentionally very strict.
Parsing probably fails for new more complicated sample files.
This will help identify the meaning of currently unknown fields.

## Usage

### Try it online
Use [this web form] to upload an `.el1` file
and view its parsed structure.

### Install and run on your own computer

First install [uv],
clone this repository,
and do one of the following in the root of the repository.

Use [uv run] to use a temporary virtualenv:

```shell
uv run pytest
uv run el1-parse samples/<filename>.el1
uv run el1-parse --extract el1-parse samples/<filename>.el1
```

Or, create and enter a permanent virtualenv:

```shell
uv sync
. .venv/bin/activate
pytest
el1-parse samples/<filename>.el1
el1-parse --extract el1-parse samples/<filename>.el1
```

[this web form]: https://akaihola.github.io/el1-parse/
[uv]: https://docs.astral.sh/uv/getting-started/installation/
[uv run]: https://docs.astral.sh/uv/guides/projects/#running-commands
