#! /usr/bin/python
# based on http://askubuntu.com/a/85191/31658 answer by andrewsomething

from gi.repository import Gtk, Gio


class BackgroundChanger(Gtk.Window):

    SCHEMA = 'org.gnome.desktop.background'
    KEY = 'picture-uri'

    def __init__(self):
        Gtk.Window.__init__(self, title="Background Changer")

        box = Gtk.Box(spacing=6)
        self.add(box)

        button1 = Gtk.Button("Set Background Image")
        button1.connect("clicked", self.on_file_clicked)
        box.add(button1)

    def on_file_clicked(self, widget):
        gsettings = Gio.Settings.new(self.SCHEMA)

        dialog = Gtk.FileChooserDialog("Please choose a file", self, Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            background = dialog.get_filename()
            gsettings.set_string(self.KEY, "file://" + background)
        elif response == Gtk.ResponseType.CANCEL:
            pass

        dialog.destroy()

    def add_filters(self, dialog):
        filter_image = Gtk.FileFilter()
        filter_image.set_name("Image files")
        filter_image.add_mime_type("image/*")
        dialog.add_filter(filter_image)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

win = BackgroundChanger()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()