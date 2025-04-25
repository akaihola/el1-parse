# Samples

## File name structure

Example file name:

```
p1-l001-f1empty-f2empty.el1  # the binary photo layout file
p1-l001-f1empty-f2empty.yaml  # structured data describing the layout
p1-l001-f1empty-f2empty.png  # screenshot from the photo layout app
```

- `p1`: page number one
- `l001`: layout `001`
- `f1empty`: first frame is empty, has no picture
- `f2empty`: second frame is empty, too

## Layout description `*.yaml` format

```yaml
---
pages:
  - layout: "001"  # first page, layout `001`
    frames:
      - center-x: 105.0  # first frame, coordinates in mm
        center-y: 81.7
      - center-x: 105.0  # second frame
        center-y: 215.2
```

## Screenshots

Screenshots should be auto-trimmed e.g. using e.g. ImageMagick
and optimized using e.g. `optipng`:

```shell
mogrify -trim p1-l001-f1empty-f2empty.png
optipng -o7 -strip all p1-l001-f1empty-f2empty.png
```
