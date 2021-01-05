import os
from glob import escape
from os.path import join
import datetime


def get_dirs(dir_path):
  """
  parse dir recursively 
  return list of all directories and subdirs
  """
  subdirs = [x[0] for x in os.walk(dir_path, topdown=False)]
  return sorted(subdirs)     

def format_result(result):
    seconds = int(result)
    output = datetime.timedelta(0, seconds)
    return output

def get_files_with_extension(dir_path, exts):
  """
  list files in directory with certain extension
  """

  files = []

  dir_files = os.listdir(dir_path)

  for ext in exts:
    for file in dir_files :
      if file.lower().endswith('.' + ext.lower()):
        files.append(join(dir_path, file))

  return sorted(files)


def get_folder_image(dir_path):
    
  valid_cover_image_files = ["folder.jpg", "cover.jpg", "cover.png", "front.jpg"]
  image_file = None

  for _ in valid_cover_image_files :
    image_path = os.path.join(dir_path, _)
    if os.path.isfile(image_path):
      image_file = image_path
      break

  if image_file is None:
    image_file = "nocover.png"

  return image_file




def build_playlist(filename, itemlist):

    with open(filename, "w") as outfile:
        outfile.write("\n".join(itemlist))