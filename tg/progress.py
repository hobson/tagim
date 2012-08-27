import sys
import time


class ProgressBase(object):
    """
    An abstract class that helps to put text on the screen and erase it again.
    """
    
    def __init__(self):
        self._str = ''

    def _show(self, text):
        sys.stderr.write('\b' * len(self._str))
        self._str = text.ljust(len(self._str))
        sys.stderr.write(self._str)


class with_spinner(ProgressBase):
    """
    A spinner for long loops of unknown duration, written on stderr.

    Wrap this around any iterable, for example:
    for line in with_spinner(lines, action = 'Processing lines...')
    """

    chars = '|/-\\'

    def __init__(self, iterable = None, action = None, done = 'done'):
        super(with_spinner, self).__init__()
        self.iterable = iterable
        self.frame = 0
        self.last = time.time()
        self.done = done
        if action:
            sys.stderr.write(action + ' ')

    def update(self):
        now = time.time()
        if self.last + 0.5 < now:
            self.last = now
            self.frame = (self.frame + 1) % len(with_spinner.chars)
            self._show(with_spinner.chars[self.frame])
    
    def stop(self):
        self._show(self.done or '')
        sys.stderr.write('\n')

    def __iter__(self):
        for item in self.iterable:
            yield item
            self.update()
        self.stop()
    

class with_progress_meter(ProgressBase):
    """
    A progress meter for long loops of known length, written on stderr.

    Wrap this around a list-like object, for example:
    for line in with_progress_meter(lines, action = 'Processing lines...')
    """

    def __init__(self, iterable = None, total = None, action = None, done = 'done'):
        super(with_progress_meter, self).__init__()
        self.iterable = iterable
        if total is None:
            total = len(self.iterable)
        self.total = total
        self.start_time = time.time()
        self.last = self.start_time
        self.at = 0
        self.done = done
        if action:
            sys.stderr.write(action + ' ')
        self._str = ''

    def update(self, at):
        self.at = at
        now = time.time()
        if self.last + 0.5 < now:
            self.last = now
            self._show(self._progress())
    
    def stop(self):
        self._show(self.done or '')
        sys.stderr.write('\n')

    def __iter__(self):
        at = 0
        for item in self.iterable:
            yield item
            at += 1
            self.update(at)
        self.stop()
    
    def _progress(self):
        text = '%3d%%' % int(self.at * 100 / self.total if self.total else 100)
        if self.at > 0:
            spent = time.time() - self.start_time
            remaining = (self.total - self.at) * spent / self.at
            text += ' (ETC: %01d:%02d.%03d)' % (
                int(remaining) / 60,
                int(remaining) % 60,
                int(remaining * 1000) % 1000)
        return text
    

