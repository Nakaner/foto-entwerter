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

import io
import os
import gi
import cairo
from enum import Enum

from .image import Image
from .blur import Blur

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf

# inspired by http://zetcode.com/gfx/pycairo/images/

class MainWindow(Gtk.Window):
    class Mode(Enum):
        ADD = 1
        DELETE = 2

    def __init__(self, args):
        self.images = []
        self.mode = MainWindow.Mode.ADD
        Gtk.Window.__init__(self, title="Foto-Entwerter")
        self.maximize()
        self.add_draw_area()
        self.connect("destroy", Gtk.main_quit)
        self.show_all()
        self.current_image_index = 0
        self.x_offset = 0
        self.y_offset = 0
        self.scale_factor = 1.0
        self.mouse_down_x = 0
        self.mouse_down_y = 0
        self.mouse_current_x = 0
        self.mouse_current_y = 0
        self.mouse_down = False
        self.output_directory = args.output_directory
        files = os.listdir(args.input_directory)
        files = [ f for f in files if f.lower().endswith(".jpg") ]
        files.sort()
        self.images = [ Image(os.path.join(args.input_directory, f)) for f in files if f.lower().endswith(".jpg") ]
        self.load_image()
        self.connect("key-press-event", self.on_key_press)

    def on_key_press(self, widget, event):
        mask = Gtk.accelerator_get_default_mod_mask()
        state = event.state & mask
        want_next = state == 0 and event.keyval == Gdk.KEY_space and self.current_image_index < len(self.images) - 1
        want_prev = state == 0 and event.keyval == Gdk.KEY_BackSpace and self.current_image_index > 0
        want_delete = state == 0 and event.keyval == Gdk.KEY_d
        want_add = state == 0 and event.keyval == Gdk.KEY_a
        want_save = state == 0 and event.keyval == Gdk.KEY_s
        if want_next:
            # next image
            self.current_image_index += 1
            self.load_image()
            self.event_box.queue_draw()
        elif want_prev:
            # previous image
            self.current_image_index -= 1
            self.load_image()
            self.event_box.queue_draw()
        elif want_delete and self.mode != MainWindow.Mode.DELETE:
            self.mode = MainWindow.Mode.DELETE
        elif want_add and self.mode != MainWindow.Mode.ADD:
            self.mode = MainWindow.Mode.ADD
        elif want_save:
            self.images[self.current_image_index].save(self.output_directory)

    def add_draw_area(self):
        self.event_box = Gtk.EventBox()
        self.event_box.connect("button-press-event", self.on_mouse_down)
        self.event_box.connect("button-release-event", self.on_mouse_up)
        self.event_box.connect("motion-notify-event", self.on_motion_notify)
        self.darea = Gtk.DrawingArea()
        self.darea.connect("draw", self.render)
        self.event_box.add(self.darea)
        self.add(self.event_box)

    def load_image(self):
        self.pb = GdkPixbuf.Pixbuf.new_from_file(self.images[self.current_image_index].path)
        self.pb = self.pb.apply_embedded_orientation()

    def click_to_image_coords(self, event_x, event_y):
        return (1 / self.scale_factor) * (event_x - self.x_offset), (1 / self.scale_factor) * (event_y - self.y_offset)

    def on_mouse_down(self, box, event):
        image_x, image_y = self.click_to_image_coords(event.x, event.y)
        self.mouse_down_x = image_x
        self.mouse_down_y = image_y
        self.mouse_down = True

    def on_mouse_up(self, box, event):
        self.mouse_down = False
        image_x, image_y = self.click_to_image_coords(event.x, event.y)
        blur_start_x = self.mouse_down_x
        blur_start_y = self.mouse_down_y
        if self.mode == MainWindow.Mode.ADD:
            new_blur = Blur.from_bbox(image_x, image_y, blur_start_x, blur_start_y)
            self.images[self.current_image_index].add_blur(new_blur)
        else:
            self.images[self.current_image_index].remove_intersecting_blurs(image_x, image_y, blur_start_x, blur_start_y)
        self.mouse_down_x = -1
        self.mouse_down_y = -1
        self.mouse_current_x = -1
        self.mouse_current_y = -1
        box.queue_draw()

    def on_motion_notify(self, widget, event):
        if not self.mouse_down:
            return
        self.mouse_current_x, self.mouse_current_y = self.click_to_image_coords(event.x, event.y)
        widget.queue_draw()

    def draw_rectangle(self, cairo_context, red, green, blue, alpha, blur):
        cairo_context.set_source_rgba(red, green, blue, alpha)
        cairo_context.move_to(self.scale_factor * blur.minx + self.x_offset, self.scale_factor * blur.miny + self.y_offset)
        cairo_context.line_to(self.scale_factor * blur.minx + self.x_offset, self.scale_factor * blur.maxy + self.y_offset)
        cairo_context.line_to(self.scale_factor * blur.maxx + self.x_offset, self.scale_factor * blur.maxy + self.y_offset)
        cairo_context.line_to(self.scale_factor * blur.maxx + self.x_offset, self.scale_factor * blur.miny + self.y_offset)
        cairo_context.close_path()
        cairo_context.fill()

    def render(self, widget, cr):
        widget_rect = widget.get_allocation()
        padding = 10
        self.scale_keep_aspect_ratio(widget_rect.width - 2 * padding , widget_rect.height - 2 * padding)
        self.x_offset = (widget_rect.width - self.rendered_pixbuf.get_width()) / 2
        self.y_offset = (widget_rect.height - self.rendered_pixbuf.get_height()) / 2
        Gdk.cairo_set_source_pixbuf(cr, self.rendered_pixbuf, self.x_offset, self.y_offset)
        factor = 1 / self.scale_factor
        cr.paint()
        for blur in self.images[self.current_image_index].blurs:
            self.draw_rectangle(cr, 0, 0, 0, 1, blur)
        if self.mouse_down_x != -1 and self.mouse_current_x != self.mouse_down_x and self.mouse_down_y != -1 and self.mouse_current_y != self.mouse_down_y:
            self.draw_rectangle(cr, 1, 0, 0, 0.5, Blur.from_bbox(self.mouse_down_x, self.mouse_down_y, self.mouse_current_x, self.mouse_current_y))

    def scale_keep_aspect_ratio(self, dest_width, dest_height):
        """Scale a pixbuf while preserving aspect ratio."""
        height = float(self.pb.get_height())
        width = float(self.pb.get_width())
        if dest_width / width < dest_height / height:
            self.scale_factor = dest_width / width
            self.rendered_pixbuf = self.pb.scale_simple(dest_width, int((dest_width / width) * height), GdkPixbuf.InterpType.BILINEAR)
        else:
            self.scale_factor = dest_height / height
            self.rendered_pixbuf =  self.pb.scale_simple(int((dest_height / height) * width), dest_height, GdkPixbuf.InterpType.BILINEAR)

