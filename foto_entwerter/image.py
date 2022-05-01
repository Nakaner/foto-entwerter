# Foto-Entwerter, a tool for blacking out parts of lots of images
# Copyright (C) 2021 Michael Reichert
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import cv2
import io
import numpy
import os.path
import pyexiv2
import sys

class Image:
    """Represents a single image with its blurred areas."""

    def __init__(self, path):
        self.path = path
        self.blurs = []

    def add_blur(self, blur):
        self.blurs.append(blur)

    def remove_intersecting_blurs(self, x1, y1, x2, y2):
        minx = min(x1, x2)
        maxx = max(x1, x2)
        miny = min(y1, y2)
        maxy = max(y1, y2)
        for i in range(len(self.blurs) - 1, -1, -1):
            if self.blurs[i].intersects(minx, miny, maxx, maxy):
                self.blurs.pop(i)

    def save(self, out_dir, size_limit, max_compression):
        # Try to save JPEG with declining compression until it is below the size limit
        if size_limit is None:
            self.save_with_compr(out_dir, max_compression)
            return
        for compression in range(max_compression, 70, -3):
            if self.save_with_compr(out_dir, compression) <= size_limit:
                break

    def save_with_compr(self, out_dir, compression):
        img = cv2.imread(self.path)
        shape = img.shape
        for blur in self.blurs:
            blur.apply(img, shape)
        outpath = os.path.join(out_dir, os.path.basename(self.path))
        metadata = pyexiv2.ImageMetadata(self.path)
        metadata.read()
        cv2.imwrite(outpath, img, [cv2.IMWRITE_JPEG_QUALITY, compression])
        metadata_new = pyexiv2.ImageMetadata(outpath)
        metadata_new.read()
        metadata.copy(metadata_new)
        for key in metadata.exif_keys:
            try:
                tag = metadata[key]
            except UnicodeDecodeError as err:
                sys.stderr.write("Skipping EXIF key {} due to {}\n".format(key, err))
                metadata_new.__delitem__(key)
        if "Exif.Image.Orientation" in metadata:
            metadata_new.__delitem__("Exif.Image.Orientation")
        # Update thumbnail
        thumb = pyexiv2.exif.ExifThumbnail(metadata_new)
        np_arr = numpy.frombuffer(bytes(thumb.data), numpy.uint8)
        if np_arr.size > 0:
            thumb_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            thumb_shape = thumb_img.shape
            for blur in self.blurs:
                blur_for_thumb = blur.transform_to(shape, thumb_shape)
                blur_for_thumb.apply(thumb_img, thumb_shape)
            retval, buf = cv2.imencode(".jpg", thumb_img)
            thumb.data = buf.tobytes()
        metadata_new.write()
        return os.path.getsize(outpath)
