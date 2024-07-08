#! /usr/bin/env python3

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

import argparse
import os.path
import sys
from foto_entwerter.main_window import MainWindow

def main():
    parser = argparse.ArgumentParser(description="Blur photos")
    parser.add_argument("-c", "--max-jpeg-compression", type=int, default=80, help="Default JPEG compression")
    parser.add_argument("-l", "--limit", type=float, help="Size limit in MB", default=4)
    parser.add_argument("input_directory", type=str, help="Input directory")
    parser.add_argument("output_directory", type=str, help="Output directory")
    args = parser.parse_args()
    if not os.path.isdir(args.output_directory):
        sys.stderr.write("ERROR: {} does not exist.\n".format(args.output_directory))
        sys.exit(1)
    app = MainWindow(args)
    from gi.repository import Gtk
    Gtk.main()

if __name__ == "__main__":
    main()
