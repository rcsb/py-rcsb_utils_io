##
# File: decorators.py
# Date:  9-Aug-2019 Jdw
#

# import logging
import time
from functools import wraps

# logger = logging.getLogger(__name__)


def retry(targetException, maxAttempts=3, delaySeconds=2, multiplier=3, defaultValue=None, logger=None):
    """ Retry the method or function on exception after a delay interval which grows by a
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
