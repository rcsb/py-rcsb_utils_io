##
# File:    TimeUtil.py
# Author:  J. Westbrook
# Date:    23-Jun-2018
# Version: 0.001
#
# Updates:
#  10-Feb-2020 jdw Add before and after deltas to the timestamp method
##
"""
Convenience utilities to manipulate timestamps.

"""

__docformat__ = "google en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import datetime
import logging

import dateutil.parser
import pytz
from dateutil.tz import tzlocal  # pylint: disable=ungrouped-imports

logger = logging.getLogger(__name__)


class TimeUtil(object):
    def __init__(self, **kwargs):
        pass

    def getTimestamp(self, useUtc=True, before=None, after=None):
        """Return an a pseudo ISO 8601 format timestamp string (2018-07-11 12:33:22.874957+00:00) including timezone details.

        Args:
            useUtc (bool, optional): Use UTC time reference
            before (dict, optional): {"days": , "weeks":, "hours": , ... } (default=None)
            after (dict, optional): {"days": , "weeks":, "hours": , ... } (default=None)

        Returns:
            str: ISO 8601 format timestamp string
        """
        if before and isinstance(before, dict):
            if useUtc:
                td = datetime.datetime.utcnow() - datetime.timedelta(**before)
                dt = td.replace(tzinfo=pytz.utc)
            else:
                td = datetime.datetime.utcnow() - datetime.timedelta(**before)
                dt = td.replace(tzinfo=tzlocal())
        elif after and isinstance(after, dict):
            if useUtc:
                td = datetime.datetime.utcnow() + datetime.timedelta(**after)
                dt = td.replace(tzinfo=pytz.utc)
            else:
                td = datetime.datetime.utcnow() + datetime.timedelta(**after)
                dt = td.replace(tzinfo=tzlocal())
        else:
            dt = datetime.datetime.utcnow().replace(tzinfo=pytz.utc) if useUtc else datetime.datetime.now().replace(tzinfo=tzlocal())
        return dt.isoformat(" ")

    def getWeekSignature(self, yyyy, mm, dd):
        """Return week in year signature (e.g. 2018_21) for the input date (year, month and day).

        Args:
            yyyy (int): year
            mm (int): month in year (1-12)
            dd (int): day in month (1-##)

        Returns:
            str: week in year signature (<yyyy>_<week_number>)
        """
        return datetime.date(yyyy, mm, dd).strftime("%Y_%V")

    def getCurrentWeekSignature(self):
        """Return the curren tweek in year signature (e.g. 2018_21).

        Returns:
            str: week in year signature (<yyyy>_<week_number>)
        """
        dt = datetime.date.today()
        return dt.strftime("%Y_%V")

    def getDateTimeObj(self, tS):
        """Return a datetime object corresponding to the input timestamp string.

        Args:
            tS (str): timestamp string (e.g. 2018-07-11 12:33:22.874957+00:00)

        Returns:
            object: datetime object
        """
        try:
            return dateutil.parser.parse(tS)
        except Exception as e:
            logger.exception("Failing with %r", str(e))
        return None
