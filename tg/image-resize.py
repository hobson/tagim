#!/usr/bin/python
import os, getopt, sys, Image

# Parse command line arguments
opts, args = getopt.getopt(sys.argv[1:], "d:w:h:s:")

# default parameters
directory = "."
width = 256
height = 193
suffix = '_sm'

# Set parameters based on command line arguments
for opt, arg in opts:
  if opt == '-d':
    directory = arg
  elif opt == '-w':
    width = int(arg)
  elif opt == '-h':
    height = int(arg)
  elif opt == '-s':
    suffix = arg

# Check to see if default parameters have been overridden
if directory == "." or width == 256 or height == 193:
  print "Using default arguments. Normal usage is: -d [directory] -w [width] -h [height] required"
  #exit()

# Cycle through images and resize them
ifp = open('index.html','w')
ifp.write('<HTML>')
colnum = -1
numcols=4
for file in os.listdir(directory):
  if numcols==(colnum-1):
    ifp.write('<br>')
  colnum = (colnum+1) % numcols
  fp = os.path.join(directory, file)
  #print("Processing " + fp)
  # Try to open the image
  fn1,ext1 = os.path.splitext(fp)
  if ext1.lower() not in ['.jpg','.jpeg','.png','.bmp','.avi','.mpg','.mpeg']:
    print("WARNING: Skipping! Unrecognized extension ("+ext1.lower()+")for " + fp )
    continue
  if ext1.lower() in ['.avi','.mpg','.mpeg']: #TODO: look for .THM and .MPG pairs (video and cover image)
    print("Processing " + fp)
    ifp.write('<A HREF="'+file+'"><IMG SRC="'+os.path.basename(fp)+'" ALT="Video" HEIGHT='+str(height)+' WIDTH='+str(width)+' BORDER=2></a>\n')
    continue
  try:
    img = Image.open(fp)
  except:
    print "WARNING: Unable to open as an image:" + fp
    continue 
  # Resize it
  (fp,ext)=os.path.splitext(fp)
  if fp.endswith(suffix):
    print("WARNING: Skipping "+fp+" It already ends with " + suffix)
    continue
  fp2 = fp + suffix + ext
  ifp.write('<A HREF="'+file+'"><IMG SRC="'+os.path.basename(fp2)+'" HEIGHT='+str(height)+' WIDTH='+str(width)+' BORDER=2></a>\n')
  if os.path.exists(fp2):
    print("WARNING: Skipping! A file named " + fp2 + suffix + " already exists." )
    continue
  else:
    print "Resizing."
    img = img.resize((width, height), Image.BILINEAR)
  # Save it back to disk
  print "  Saving " + fp2
  img.save(fp2)
ifp.write('</HTML>')
ifp.close()

