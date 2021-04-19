# Foto-Entwerter

Foto-Entwerter (German: invalidate photos or – more literally – remove the value from photos)
is a tool to black out faces and license plates from a large number of photos in a
manual but efficient way for a large number of photos. It preserves metadata and updates
EXIF thumbnails.

## Dependencies

* OpenCV Python bindings
* Numpy
* PyGObject
* Cairo Python bindings
* Py3Exiv2

On Debian/Ubuntu:

```sh
apt install python3-opencv python3-numpy python3-gi python3-cairo python3-py3exiv2
```

On Arch Linux:

```sh
pacman -S opencv python-numpy python-gobject python-cairo
yay -S python-exiv2
```

## Usage

Foto-Entwerter is called from the command line. It expects two arguments, the input and the output directory.

In the GUI, you can navigate with your keyboard only:

* A: Switch to *add* mode. You now add areas to be blacked out by drawing rectangles.
* D: Switch to *delete* mode. By drawing a rectangle, you delete all blacked areas intersecting with it.
* S: Apply the blurs and *save* the image to the output directory.
* Space: Switch to next image.
* Backspace: Switch to previous image.

## License

Foto-Entwerter is licensed under the terms of the GNU GENERAL PUBLIC LICENSE Version 3 or newer.
See [COPYING](COPYING) for details.
