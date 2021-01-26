##
# File: ExeceUtils.py
# Date: 24-Jan-2020 jdw
#
##
import logging
import os
import subprocess
import sys

logger = logging.getLogger(__name__)


class ExecUtils(object):
    """Wrapper for subprocess execution."""

    def __init__(self):
        """Wrapper for subprocess execution"""

    def run(self, execPath, execArgList=None, outPath=None, outAppend=False, timeOut=None, inpPath=None, suppressStderr=False):
        """Execute the input program as a blocking subprocess with optional timeout.

        Args:
            execPath (str): path to executable program or script
            execArgList (list, optional): argument list. Defaults to None.
            outPath (str, optional): redirect stdout and stderr to this file handle. Defaults to None.
            inpPath (str, optional): redirect stdin to this file handle. Defaults to None.
            outAppend (bool, optional): append output. Defaults to False.
            timeOut (float, optional): timeout (seconds). Defaults to None.
            suppressStderr (bool, optional): suppress stderr output (default: combined with stdout)


        Returns:
            bool: true for sucess or False otherwise
        """
        retCode = False
        subProcResult = None
        kwD = {}
        if suppressStderr:
            myStderr = subprocess.DEVNULL
        else:
            myStderr = subprocess.STDOUT
        try:
            if not os.path.isfile(execPath) and os.access(execPath, os.X_OK):
                return retCode
            if sys.version_info[0] > 2 and timeOut:
                kwD = {"timeout": timeOut}
            cmdL = [execPath]
            if execArgList:
                cmdL.extend(execArgList)
            if outPath and inpPath:
                myMode = "a" if outAppend else "w"
                with open(outPath, myMode) as ofh, open(inpPath, "r") as ifh:
                    subProcResult = subprocess.call(cmdL, stdout=ofh, stdin=ifh, stderr=myStderr, **kwD)
            elif outPath:
                myMode = "a" if outAppend else "w"
                with open(outPath, myMode) as ofh:
                    subProcResult = subprocess.call(cmdL, stdout=ofh, stderr=myStderr, **kwD)
            else:
                subProcResult = subprocess.call(cmdL, **kwD)
            retCode = not subProcResult
        except Exception as e:
            logger.exception("Failing execution of %s (%s) with %s", execPath, execArgList, str(e))
        #
        if subProcResult != 0:
            logger.error("return code is %r", subProcResult)
        return retCode

    def runShell(self, script, outPath=None, outAppend=False, timeOut=None, inpPath=None, suppressStderr=False):
        """Execute the input program as a blocking subprocess with optional timeout.

        Args:
            script (str): script
            outPath (str, optional): redirect stdout and stderr to this file handle. Defaults to None.
            inpPath (str, optional): redirect stdin to this file handle. Defaults to None.
            outAppend (bool, optional): append output. Defaults to False.
            timeOut (float, optional): timeout (seconds). Defaults to None.
            suppressStderr (bool, optional): suppress stderr output (default: combined with stdout)


        Returns:
            bool: true for sucess or False otherwise
        """
        retCode = 0
        kwD = {}
        subProcResult = None
        if suppressStderr:
            myStderr = subprocess.DEVNULL
        else:
            myStderr = subprocess.STDOUT
        try:
            if sys.version_info[0] > 2 and timeOut:
                kwD = {"timeout": timeOut}
            #
            if outPath and inpPath:
                myMode = "a" if outAppend else "w"
                with open(outPath, myMode) as ofh, open(inpPath, "r") as ifh:
                    subProcResult = subprocess.run(script, stdout=ofh, stdin=ifh, stderr=myStderr, shell=True, check=False, **kwD)
            elif outPath:
                myMode = "a" if outAppend else "w"
                with open(outPath, myMode) as ofh:
                    subProcResult = subprocess.run(script, stdout=ofh, stderr=myStderr, shell=True, check=False, **kwD)
            else:
                subProcResult = subprocess.run(script, shell=True, check=False, **kwD)
            retCode = not subProcResult.returncode
        except Exception as e:
            logger.exception("Failing execution of %r with %s", subProcResult, str(e))
        #
        if subProcResult and subProcResult.returncode != 0:
            logger.warning("return code is %r", subProcResult.returncode)
        return retCode
