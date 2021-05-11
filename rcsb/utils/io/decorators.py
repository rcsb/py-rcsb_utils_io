##
# File: decorators.py
# Date:  9-Aug-2019 Jdw
#

import multiprocessing
import signal
import sys
import time
from functools import wraps


def quietHook(kind, message, traceback):
    if QuietException in kind.__bases__:
        print("{0}: {1}".format(kind.__name__, message))  # Only print Error Type and Message
    else:
        sys.__excepthook__(kind, message, traceback)  # Print Error Type, Message and Traceback


sys.excepthook = quietHook


class QuietException(Exception):
    pass


class TimeoutException(Exception):
    def __init__(self, value):
        super(TimeoutException, self).__init__(value)
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return repr(self.value)


class MyProcess(multiprocessing.Process):
    def __init__(self, func, *args, **kwargs):
        self.queue = multiprocessing.Queue(maxsize=1)
        args = (func,) + args
        multiprocessing.Process.__init__(self, target=self.runner, args=args, kwargs=kwargs)

    def runner(self, func, *args, **kwargs):
        try:
            result = func(*args, **kwargs)
            self.queue.put((True, result))
        except Exception as e:
            self.queue.put((False, e))

    def done(self):
        return self.queue.full()

    def result(self):
        return self.queue.get()


def timeout(seconds, message="Function call timed out"):
    def wrapper(function):
        def _handleTimeout(signum, frame):
            raise TimeoutException(message)

        @wraps(function)
        def wrapped(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handleTimeout)
            signal.alarm(seconds)
            try:
                result = function(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wrapped

    return wrapper


def timeoutMp(seconds, forceKill=True):
    def wrapper(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            now = time.time()
            proc = MyProcess(function, *args, **kwargs)
            proc.start()
            proc.join(seconds)
            if proc.is_alive():
                if forceKill:
                    proc.terminate()
                runtime = int(time.time() - now)
                raise TimeoutException("timed out after {0} seconds".format(runtime))
            assert proc.done()
            success, result = proc.result()
            if success:
                return result
            else:
                raise result

        return wrapped

    return wrapper


def retry(targetException, maxAttempts=3, delaySeconds=2, multiplier=3, defaultValue=None, logger=None):
    """Retry the method or function on exception after a delay interval which grows by a
    multiplicative factor between attempts.  On failure after maxAttempts are exceeded then default value
    is returned.

    Args:
        targetException (Exception or tuple of exceptions): target exception
        maxAttempts (int, optional): number of attempts. Defaults to 3.
        delaySeconds (int, optional): interval to wait between attempts. Defaults to 2.
        multiplier (int, optional): multiplicative factor to apply to delay interval. Defaults to 3.

    Adapted from example at: http://code.activestate.com/recipes/580745-retry-decorator-in-python/
                         and https://wiki.python.org/moin/PythonDecoratorLibrary#Retry
    """

    def wrapper(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            attemptsLeft = maxAttempts
            currentDelaySecs = delaySeconds
            while attemptsLeft > 1:
                try:
                    if logger:
                        logger.debug("Attempts left %d", attemptsLeft)
                    return function(*args, **kwargs)
                except targetException as e:
                    if logger:
                        logger.info("waiting for %d seconds after %s", currentDelaySecs, str(e))
                    time.sleep(currentDelaySecs)
                    attemptsLeft -= 1
                    currentDelaySecs *= multiplier
            try:
                return function(*args, **kwargs)
            except targetException:
                if logger:
                    logger.info("Failing after %d attempts returning default %r", maxAttempts, defaultValue)
                return defaultValue
            return

        return wrapped

    return wrapper
