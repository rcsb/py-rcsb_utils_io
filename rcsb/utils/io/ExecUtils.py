##
# File: ExeceUtils.py
# Date: 24-Jan-2020 jdw
#
##

import logging
import os
import subprocess

logger = logging.getLogger(__name__)


class ExecUtils:
    """Wrapper for subprocess execution.
    """

    def __init__(self):
        """Wrapper for subprocess execution
        """

    def run(self, execPath, execArgList=None, outPath=None, outAppend=False, timeOut=None):
        """Execute the input program as a blocking subprocess with optional timeout.

        Args:
            execPath ([type]): path to executable program or script
            execArgList ([type], optional): argument list. Defaults to None.
            outPath ([type], optional): redirect stdout and stderr to this file handle. Defaults to None.
            outAppend (bool, optional): append output. Defaults to False.
            timeOut ([type], optional): timeout (seconds). Defaults to None.

        Returns:
            bool: true for sucess or False otherwise
        """
        retCode = False
        try:
            if not os.path.isfile(execPath) and os.access(execPath, os.X_OK):
                return retCode
            cmdL = [execPath]
            if execArgList:
                cmdL.extend(execArgList)
            if outPath:
                myMode = "a" if outAppend else "w"
                with open(outPath, myMode) as ofh:
                    subProcResult = subprocess.call(cmdL, stdout=ofh, stderr=subprocess.STDOUT, timeout=timeOut)
            else:
                subProcResult = subprocess.call(cmdL, timeout=timeOut)
            retCode = not subProcResult
        except Exception as e:
            logger.exception("Failing execution of %s (%s) with %s", execPath, execArgList, str(e))
        #
        logger.info("return code is %r", subProcResult)
        return retCode
