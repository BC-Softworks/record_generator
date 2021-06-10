import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

def on_activate(app):
    win = Gtk.ApplicationWindow(application=app)
    btn = Gtk.Button(label="B.C. Softworks")
    btn.connect('clicked', lambda x: win.close())
    win.add(btn)
    win.show_all()

app = Gtk.Application(application_id='org.gtk.record_generator')
app.connect('activate', on_activate)
app.run(None)
