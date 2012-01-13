#!/usr/bin/env python
# Filename: looping_shuffle_background_photo.py
"""Change the desktop background image every so often.

Examples:
	# this will rotate the image every hour
	looping_shuffle_background_photo.py
	# this will rotate the image every day (86400=60*60*24 seconds)
	looping_shuffle_background_photo.py 86400

Dependencies:
	time
	argparse
	tg.tagim 

TODO:
	Add command line options.
	Verify resources.
	Check for other instances/tasks/jobs and abort.
	Spawn low priority task for self (linux nice).
	
	((c) Hobson Lane dba TotalGood)
"""

#. /etc/profile
#. /home/hobs/.profile

import time 
import tg.tagim
from argparse import ArgumentParser

p = ArgumentParser(
	description=__doc__.strip())
p.add_argument(
	'N1', 
	metavar='N1',
	type=int,
	nargs = '?', # other options '*','+', 2
	default = 3600,
	help='Minimum number of seconds between desktop image updates.')
p.add_argument(
	'N2', 
	metavar='N2',
	type=int,
	nargs = '?', # other options '*','+', 2
	default = None,
	help='Maximum number of seconds between desktop image updates.')
o = p.parse_args()
# print vars(o)
# better to use min/max for these so the order doesn't matter

# TODO: shorter sleep durations (~2 sec) to more frequently check for stop signal
#       but don't cycle background unless shuffle duration time has passed
#       so sleep durations can be some count of the shorter period clock cycle
import random
def shuffle_background_then_sleep(max_period,min_period=None):
	MIN_DELAY = 5; # don't let the delay go below 5 seconds
	MAX_DELAY = 7*24*3600; # don't let the delay go beyond 1 week
	print "Shuffling the background photo..."
	tg.tagim.shuffle_background_photo()
	# None is smaller than any integer: `min(-5,None)` gives None, but `max(5,None)` gives 5
	min_period = min(min_period,max_period)
	if max_period and type(max_period)==int and max_period>=2*minDelay and max_period>min_period and type(min_period)==int and min_period and min_period>0:
		random_delay_period = random.randint(min_period,max_period)
	else:
		random_delay_period  = min(max(min_period,MIN_DELAY),MAX_DELAY)
	print "Done shuffling now sleeping for {0} seconds...".format(N)
	time.sleep(N)  # Delay for N seconds

while True:
	shuffle_background()
# Question at http://stackoverflow.com/questions/4705564/python-script-as-linux-service-daemon uses the following:
import signal
import time
import multiprocessing

stop_event = multiprocessing.Event()

def stop(signum, frame):
    stop_event.set()

signal.signal(signal.SIGTERM, stop)

if __name__ == '__main__':
	minDelay = 5
	while not stop_event.is_set():
		shuffle_background_then_sleep(o.N1,o.N2)
		time.sleep()

