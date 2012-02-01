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

import time # sleep
import random # randint
import tg.tagim # shuffle_background_photo
from argparse import ArgumentParser
import signal # signal, SIGTERM
import multiprocessing # Event

p = ArgumentParser(description=__doc__.strip())
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
#print o
# print vars(o)
# better to use min/max for these so the order doesn't matter

# TODO: shorter sleep durations (~2 sec) to more frequently check for stop signal
#       but don't cycle background unless shuffle duration time has passed
#       so sleep durations can be some count of the shorter period clock cycle
def shuffle_background_then_sleep(min_period=3600,max_period=None):
	"""Change the desktop background image then sleep for specified number of seconds.
	
	If only one argument is given (min_period) then it is interpretted as a maximum time period (not min).
	"""
	MIN_DELAY = 5; # don't let the delay go below 5 seconds
	MAX_DELAY = 7*24*3600; # don't let the delay go beyond 1 week
	print "Shuffling the background photo..."
	tg.tagim.shuffle_background_photo()
	# None is smaller than any integer: `min(-5,None)` gives None, but `max(5,None)` gives 5

	print min_period,max_period;
	if ( max_period and type(max_period)==int and max_period>=1.1*MIN_DELAY and max_period>min_period
	      and type(min_period)==int and min_period and min_period>0 ):
		dt = random.randint(min(min_period,MAX_DELAY), min(max_period,MAX_DELAY))
	else: # reverse the assumed order of the arguments if only one given (one argument means it's max, not min)
		dt  = min(max(min_period,MIN_DELAY),MAX_DELAY)
	a = (dt,'s') if dt<0.5*3600 else (dt/3600,'hr');
	print "Done shuffling now sleeping for {0} {1}...".format(a[0],a[1])
	time.sleep(dt)  # Delay for N seconds

#while True:
#	shuffle_background()
# Question at http://stackoverflow.com/questions/4705564/python-script-as-linux-service-daemon uses the following:
stop_event = multiprocessing.Event()
def stop(signum, frame):
    stop_event.set()
signal.signal(signal.SIGTERM, stop)

# probably unnecessary to define __main__, since this can ONLY be run as a script
#if __name__ == '__main__':
while not stop_event.is_set():
	shuffle_background_then_sleep(o.N1,o.N2)

