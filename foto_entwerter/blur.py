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

class Blur:
    """Represents a blurred box in an image."""

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def from_bbox(x1, y1, x2, y2):
        """Factory method to create an instance of Blur from a bounding box."""
        x = min(x1, x2)
        y = min(y1, y2)
        width = max(x1, x2) - x
        height = max(y1, y2) - y
        return Blur(x, y, width, height)

    def apply(self, img_data, shape):
        """Apply this blur to an image (read using cv2.imread or cv2.imdecode)."""
        for x in range(int(self.minx), int(self.maxx) + 1):
            if x >= shape[1]:
                continue
            for y in range(int(self.miny), int(self.maxy) + 1):
                if y >= shape[0]:
                    continue
                for band in range(0, shape[2]):
                    img_data[y, x, band] = 0

    def transform_to(self, old_shape, new_shape):
        """Return a copy with x, y, width and height scaled onto the new image."""
        x_factor = new_shape[1] / old_shape[1]
        y_factor = new_shape[0] / old_shape[0]
        return Blur(self.x * x_factor, self.y * y_factor, self.width * x_factor, self.height * y_factor)

    @property
    def minx(self):
        return self.x

    @property
    def miny(self):
        return self.y

    @property
    def maxx(self):
        return self.x + self.width

    @property
    def maxy(self):
        return self.y + self.height

    def intersects(self, x1, y1, x2, y2):
        return x2 >= self.minx and x1 <= self.maxx and y2 >= self.miny and y1 <= self.maxy

    def __repr__(self):
        return "Blur({} {} {} {})".format(self.x, self.y, self.width, self.height)
