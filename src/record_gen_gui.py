# GTK
import os
import gi
gi.require_version("Gtk", "3.24")
from gi.repository import Gtk

# Record Generator
import lpcm_to_csv
import basic_shape_gen
import record_gen

class Handler:
    
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
  builder = Gtk.Builder()
  builder.add_from_file("Record_gen_GTK.glade")
  builder.connect_signals(Handler())

  window = builder.get_object("main_window")
  window.show_all()

  Gtk.main()
    
#Run program
if __name__ == '__main__':
    main()
#
#
# record_gen.main(filename, stlname)
