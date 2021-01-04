
import os
import subprocess


def play(widget , *data):
  
  dir = data[0]
  stop(None)
  subprocess.run('bash mplayer3.sh "' + str(dir) + '" &', shell=True)
            
def stop(widget):
   subprocess.run("echo 'quit' > /tmp/pipe &", shell=True)

def next(widget):
   subprocess.run("echo 'pt_step 1' > /tmp/pipe &", shell=True)

def prev(widget):
   subprocess.run("echo 'pt_step -1' > /tmp/pipe &", shell=True)

def pause(widget):
   subprocess.run("echo 'pause' > /tmp/pipe &", shell=True)
