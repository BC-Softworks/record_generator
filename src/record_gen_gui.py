# GTK
import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

# Record Generator
import lpcm_to_csv
import basic_shape_gen
import record_gen



def on_activate(app):
    win = Gtk.ApplicationWindow(application=app)
    btn = Gtk.Button(label="B.C. Softworks")
    btn.connect('clicked', lambda x: win.close())
    win.add(btn)
    win.show_all()
    
def processlpcm(path):
    filename = os.path.basename(path)
    extension = filename.split(".")[1]
    if extension in ['wav', 'wave']:
        lpcm_to_csv.wavetocsv(filename)
    elif extension in ['aifc', 'aiff']:
        lpcm_to_csv.aifctocsv(filename)
    else:
      # Not a supported file format.
      # TODO: Add pop up error message

def generate_disc():
    basic_shape_gen.main()
    
def generate_record(path, stlname):
    filename = os.path.basename(path)
    record_gen.main(filename, stlname)
    
def main():
    app = Gtk.Application(application_id='org.gtk.record_generator')
    app.connect('activate', on_activate)
    app.run(None)
    
#Run program
if __name__ == '__main__':
    main()
#
#
# record_gen.main(filename, stlname)
