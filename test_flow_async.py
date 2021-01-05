import datetime
import time
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GdkPixbuf, GObject
import os
from os.path import join
from glob import glob
import subprocess
from utils import *
from mplayer import *


class MyWindow(Gtk.Window):

    def __init__(self):

        alsa_device = 2
        self.mplayer = MPlayer(alsa_device)

        Gtk.Window.__init__(self, title="Window 1")
        self.set_border_width(10)
        self.set_default_size(1900, 1000)
        self.set_icon_from_file("icon.png")

        header = Gtk.HeaderBar(title="FlowdIo")
        header.props.show_close_button = True

        self.set_titlebar(header)
        self.playlist_filename = '/tmp/playlist_%s.m3u' % os.getpid();

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

        button_select = Gtk.Button.new_from_stock(Gtk.STOCK_OPEN)

        button_scan = Gtk.Button.new_from_stock(Gtk.STOCK_HARDDISK)
        button_scan.connect("clicked", self.scan_folder)

        button_stop = Gtk.Button.new_from_stock(Gtk.STOCK_MEDIA_STOP)
        button_stop.connect("clicked", self.playback_stop)

        button_prev = Gtk.Button.new_from_stock(Gtk.STOCK_MEDIA_PREVIOUS)
        button_prev.connect("clicked", self.playback_prev)

        button_next = Gtk.Button.new_from_stock(Gtk.STOCK_MEDIA_NEXT)
        button_next.connect("clicked", self.playback_next)

        button_pause = Gtk.Button.new_from_stock(Gtk.STOCK_MEDIA_PAUSE)
        button_pause.connect("clicked", self.playback_pause)


        self.position_label = Gtk.Label("0") 

        command_box.pack_start(button_select, False, False, 0)
        command_box.pack_start(button_scan, False, False, 0)
        command_box.pack_start(self.path_to_scan, True, True, 0)
        command_box.pack_start(button_stop, False, False, 0)
        command_box.pack_start(button_prev, False, False, 0)
        command_box.pack_start(button_next, False, False, 0)
        command_box.pack_start(button_pause, False, False, 0)
        command_box.pack_start(self.position_label, False, False, 0)

        self.info_label = Gtk.Label("Welcome")
        self.info_label.set_line_wrap(True)   

        self.progressbar = Gtk.ProgressBar()

        info_box.pack_start(self.info_label, False, True, 0)
        info_box.pack_start(self.progressbar, False, True, 0)

        main_box.pack_start(command_box, False, False, 0)
        main_box.pack_start(albums_scrolled, True, True, 0)
        main_box.pack_start(info_box, False, False, 0)

        button_select.connect("clicked", self.on_folder_clicked)

        self.add(main_box)


            
    def playback_play(self, widget, *data):

        files_to_play = data[0]
        print(files_to_play)

        build_playlist(self.playlist_filename, files_to_play)

        try:
          self.mplayer.command('loadlist', self.playlist_filename)   
        except : 
          self.mplayer = MPlayer(2)
          self.mplayer.command('loadlist', self.playlist_filename)   

        """ 
        i = 5000000000
        while i > 0 :
          time.sleep(1) 
          GObject.timeout_add_seconds(1, self.update_playback_position, []) """


    def update_playback_position(self, widget):

        pos = self.mplayer.get_time_pos()
        if pos == None:
          pos = 0
        pos = datetime.timedelta(seconds=pos)

        tot = self.mplayer.get_time_length()
        if tot == None:
          tot = 0        
        tot = datetime.timedelta(seconds=tot)

        self.position_label.set_text(str(pos) + "/" + str(tot))   

        self.position_label.show_all()
        
        return True   


    def playback_pause(self, widget):
        self.mplayer.pause()


    def playback_stop(self, widget):
        self.mplayer.quit()
        del self.mplayer


    def playback_next(self, widget):

        self.mplayer.pt_step([1])


    def playback_prev(self, widget):
        self.mplayer.pt_step([-1])



    def scan_folder(self, widget):

        self.path_to_scan.get_text()

        self.load_cover_view()

        #GObject.timeout_add_seconds(1, self.load_cover_view)


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

          dialog.hide()
          self.load_cover_view(None)

        dialog.destroy()
   

    def load_cover_view(self, widget):

        valid_audio_extensions = ["flac", "mpc", "mp3", "wav", "wv", "ape", "ogg"]

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
        dirs_parsed_count = 0
        files_found_count = 0

        # build album covers
        for dir in dirs:
          
          dirs_parsed_count += 1

          cover_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

          audio_files = get_files_with_extension(dir, valid_audio_extensions)
          
          audio_files_count = len(audio_files)

          files_found_count += audio_files_count

          dirs_found_count += 1
          
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

          button.connect('clicked', self.playback_play, audio_files)

          label = Gtk.Label(dir.split("/")[-1])
          label.set_line_wrap(True)
          label.set_max_width_chars(20)

          cover_box.add(button)
          cover_box.add(label)
          
          self.flowbox.add(cover_box)

          text = "Albums found = " + str(dirs_found_count) + ", audio files = " + str(files_found_count)
          self.progressbar.set_fraction(dirs_parsed_count/dirs_count)
          self.info_label.set_text(text)

          while Gtk.events_pending():
              Gtk.main_iteration()

          self.flowbox.show_all()


win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()

Gtk.main()