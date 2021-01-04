import os
from glob import escape
from os.path import join


def get_dirs(dir_path):
  """
  parse dir recursively 
  return list of all directories and subdirs
  """
  subdirs = [x[0] for x in os.walk(dir_path, topdown=False)]
  return sorted(subdirs)     


def get_files_with_extension(dir_path, exts):
  """
  list files in directory with certain extension
  """

  files = []

  for ext in exts:
    files.append(escape(join(dir_path, ext)))

  return files


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
