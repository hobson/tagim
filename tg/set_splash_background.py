# filename: set_splash_background.py
# version: 0.1

# Set the ubuntu startup screen background to an image file
import sys

print 'file='+__file__

if len(sys.argv) != 2:
	sys.stderr.write("Usage: sudo python set_splash_background.py <full_path_to_image>\n")
	sys.exit(1)

import tg.tagim
tg.tagim.set_splash_background(image=sys.argv[1])

