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

# stdlib
import time  # sleep
import random  # randint
import tg.tagim  # shuffle_background_photo
from argparse import ArgumentParser
import threading
#import signal  # signal, SIGTERM
#import multiprocessing  # Event
import logging


logging.basicConfig(filename='tagim.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

p = ArgumentParser(description=__doc__.strip())
p.add_argument(
    'N1',
    metavar='N1',
    type=int,
    nargs='?',  # other options '*','+', 2
    default=3600,
    help='Minimum number of seconds between desktop image updates.')
p.add_argument(
    'N2',
    metavar='N2',
    type=int,
    nargs='?',  # other options '*','+', 2
    default=None,
    help='Maximum number of seconds between desktop image updates.')
o = p.parse_args()
#print o
# print vars(o)
# better to use min/max for these so the order doesn't matter


class ShufflerThread(threading.Thread):
    _min_delay = 1      # one second
    _max_delay = 7 * 24 * 3600   # one week

    def __init__(self, N1=3600, N2=None):
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.N1 = N1
        self.N2 = N2

        if (self.N1 and self.N2
                and isinstance(self.N2, (float, int)) and self.N2 >= 1.1 * self._min_delay and self.N2 > self.N1
                and isinstance(self.N1, (float, int)) and self.N1 >= self._min_delay):
            self.dt = random.randint(min(self.N1, self._max_delay), min(self.N2, self._max_delay))
        else:  # reverse the assumed order of the arguments if only one given (one argument means it's max, not min)
            self.dt = min(max(self.N1, self._min_delay), self._max_delay)
        self.start_time = time.time()
        self.run()

    def stop(self):
        self.event.set()

    # TODO: shorter sleep durations (~2 sec) to more frequently check for stop signal
    #       but don't cycle background unless shuffle duration time has passed
    #       so sleep durations can be some count of the shorter period clock cycle
    def shuffle_background(self):
        """Change the desktop background image"""
        logger.info("Shuffling the background photo...")
        tg.tagim.shuffle_background_photo()
        # None is smaller than any integer: `min(-5, None)` gives None, but `max(5, None)` gives 5
        logger.info("Finished shuffling. Going to sleep for {0} {1}...".format(self.dt, 'seconds'))

    def run(self):
        """Change the desktop background image then sleep for specified number of seconds, repeat.

        If only one argument is given (min_period) then it is interpretted as a maximum time period (not min)."""
        while not self.event.is_set():
            logger.info("{0} s elapsed in this cycle".format(time.time() - self.start_time))
            if (time.time() - self.start_time) > self.dt:
                self.start_time = time.time()
                self.shuffle_background()  # ignores o.N2
                self.event.wait(300)
            time.sleep(1)


# probably unnecessary to define main(), since this can ONLY be run as a script
if __name__ == '__main__':
    shuffler = ShufflerThread(o.N1, o.N2 or None)
    shuffler.start()
    shuffler.stop() + shuffler.join()
