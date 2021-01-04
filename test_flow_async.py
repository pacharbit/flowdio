import time as t
import random as rd
import math 
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GdkPixbuf
import os
from os.path import join
from glob import glob
import subprocess
from utils import *
from playback import *


class MyWindow(Gtk.Window):

    def __init__(self):

        Gtk.Window.__init__(self, title="Window 1")
        self.set_border_width(10)
        self.set_default_size(1900, 1000)

        header = Gtk.HeaderBar(title="Flow Box")
        header.set_subtitle("Sample FlowBox app")
        header.props.show_close_button = True

        self.set_titlebar(header)


        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_homogeneous(False)

        command_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        command_box.set_homogeneous(False)

        albums_scrolled = Gtk.ScrolledWindow()
        albums_scrolled.set_hexpand(True)
        albums_scrolled.set_vexpand(True)
        albums_scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        info_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        info_box.set_homogeneous(False)

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)

        albums_scrolled.add(self.flowbox)

        self.path_to_scan = Gtk.Entry()
        self.path_to_scan.set_text("/home/pa.charbit/nicotine-downloads/")

        button_scan = Gtk.Button(label="Scan")

        button_stop = Gtk.Button(label="Stop")
        button_stop.connect("clicked", stop)

        button_prev = Gtk.Button(label="Prev")
        button_prev.connect("clicked", prev)

        button_next = Gtk.Button(label="Next")
        button_next.connect("clicked", next)

        button_pause = Gtk.Button(label="Pause")
        button_pause.connect("clicked", pause)

        command_box.pack_start(button_scan, False, False, 0)
        command_box.pack_start(self.path_to_scan, True, True, 0)
        command_box.pack_start(button_stop, False, False, 0)
        command_box.pack_start(button_prev, False, False, 0)
        command_box.pack_start(button_next, False, False, 0)
        command_box.pack_start(button_pause, False, False, 0)


        self.info_label = Gtk.Label("Welcome")
        self.info_label.set_line_wrap(True)   

        self.progressbar = Gtk.ProgressBar()

        info_box.pack_start(self.info_label, False, True, 0)
        info_box.pack_start(self.progressbar, False, True, 0)

        main_box.pack_start(command_box, False, False, 0)
        main_box.pack_start(albums_scrolled, True, True, 0)
        main_box.pack_start(info_box, False, False, 0)

        button_scan.connect("clicked", self.on_folder_clicked)

        self.add(main_box)

    def on_folder_clicked(self, widget):

        dialog = Gtk.FileChooserDialog(
            title="Please choose a folder",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK
        )
        dialog.set_default_size(800, 400)

        response = dialog.run()

        if response == Gtk.ResponseType.OK:

          self.path_to_scan.set_text(dialog.get_filename())

          self.load_cover_view(None)

        dialog.destroy()
   

    def load_cover_view(self, widget):

        valid_audio_extensions = ["*.flac", "*.mpc", "*.mp3", "*.wav", "*.wv", "*.ape"]

        # flush album covers
        for widget in self.flowbox:
          self.flowbox.remove(widget)

        path_to_scan = self.path_to_scan.get_text()

        if len(path_to_scan) == 0 : 
          return False

        dirs = get_dirs(path_to_scan)

        # init counters for progress bar
        dirs_count = len(dirs)
        dirs_found_count = 0
        files_found_count = 0

        # build album covers
        for dir in dirs:

          cover_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

          audio_files = get_files_with_extension(dir, valid_audio_extensions)
          
          audio_files_count = len(audio_files)

          files_found_count += audio_files_count

          # do not display folder with no audio file
          if audio_files_count == 0 :
            continue

          dirs_found_count += 1

          # get folder image
          pixbuf = Gtk.Image()
          image_file_path = get_folder_image(dir)

          try :
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(image_file_path, 350, 350)
          except :
            image_file_path = "nocover.png"
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(image_file_path, 350, 350)
            pass

          image = Gtk.Image.new_from_pixbuf(pixbuf)
          button = Gtk.Button()
          button.add(image)

          button.connect('clicked', play, dir)

          label = Gtk.Label(dir.split("/")[-1])
          label.set_line_wrap(True)
          label.set_max_width_chars(20)

          cover_box.add(button)
          cover_box.add(label)
          
          self.flowbox.add(cover_box)

          text = "Albums found = " + str(dirs_found_count) + ", audio files = " + str(files_found_count)
          self.progressbar.set_fraction(dirs_found_count/dirs_count)
          self.info_label.set_text(text)

          while Gtk.events_pending():
              Gtk.main_iteration()
          
          self.flowbox.show_all()

win = MyWindow()
win.connect("destroy", Gtk.main_quit)

win.show_all()

Gtk.main()