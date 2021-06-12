##
# File:    ProcessStatusUtil.py
# Author:  J. Westbrook
# Date:    23-Aug-2020
# Version: 0.001
#
# Updates:
#
##
"""
Convenience utilities to report process status.

"""

__docformat__ = "google en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import datetime
import logging
import platform
import socket
import time
import uuid

# import requests

import psutil

logger = logging.getLogger(__name__)


class ProcessStatusUtil(object):
    def __init__(self, **kwargs):
        pass

    def getInfo(self):
        """Return a dictionary of system and process status details.

        Returns:
            dict: dictionary of system and process status
        """
        infoD = {}
        infoD.update(self.__getSystemInfo())
        infoD["traffic"] = self.__getNetworkTraffic()
        infoD.update(self.__getCpuInfo())
        infoD["memory"] = self.__getMemoryInfo()
        infoD.update(self.__getStorageInfo())
        #
        return infoD

    def __getSystemInfo(self):
        rD = {}
        try:
            hostName = socket.gethostname()
            systemName = platform.system()
            systemVersion = platform.release()
            timeStamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
            uptimeSeconds = int(time.time() - psutil.boot_time())
            systemId = uuid.getnode()
            rD = {"hostName": hostName, "systemName": systemName, "systemVersion": systemVersion, "update": timeStamp, "uptimeSeconds": uptimeSeconds, "uuid": systemId}
        except Exception as e:
            logger.exception("Failing with %r", str(e))
        return rD

    def __getCpuInfo(self):
        rD = {}
        try:
            cpuCount = psutil.cpu_count()
            cpuUsage = psutil.cpu_percent(interval=1)
            rD = {"cpuCount": cpuCount, "cpuUsagePercent": cpuUsage}
        except Exception as e:
            logger.exception("Failing with %r", str(e))
        return rD

    def __getMemoryInfo(self):
        rD = {}
        try:
            vm = psutil.virtual_memory()
            memoryTotalGi = round(vm.total / 1e9, 2)
            memoryUsedGi = round(vm.used / 1e9, 2)
            memoryUsedPercent = vm.percent
            rD = {"memoryTotalGi": memoryTotalGi, "memoryUsedGi": memoryUsedGi, "memoryUsedPercent": memoryUsedPercent}
        except Exception as e:
            logger.exception("Failing with %r", str(e))
        return rD

    def __getStorageInfo(self):
        rD = {}
        try:
            diskPartL = psutil.disk_partitions()
            diskL = []
            for dp in diskPartL:
                try:
                    disk = {
                        "name": dp.device,
                        "mount_point": dp.mountpoint,
                        "type": dp.fstype,
                        "totalSizeGi": round(psutil.disk_usage(dp.mountpoint).total / 1e9, 1),
                        "usedSizeGi": round(psutil.disk_usage(dp.mountpoint).used / 1e9, 1),
                        "percentUsed": psutil.disk_usage(dp.mountpoint).percent,
                    }
                    diskL.append(disk)
                except Exception:
                    pass
            rD = {"diskInfo": diskL}
        except Exception as e:
            logger.exception("Failing with %r", str(e))
        return rD

    def __getNetworkInfo(self):
        rD = {"networkInterfaces": []}
        try:
            # Network Info
            nicL = []
            for name, snicL in psutil.net_if_addrs().items():
                # Create NIC object
                nic = {"name": name, "mac": "", "address": "", "address6": "", "netmask": ""}
                # Get NiC values
                for snic in snicL:
                    if snic.family == -1:
                        nic["mac"] = snic.address
                    elif snic.family == 2:
                        nic["address"] = snic.address
                        nic["netmask"] = snic.netmask
                    elif snic.family == 23:
                        nic["address6"] = snic.address
                nicL.append(nic)

            rD = {"networkInterfaces": nicL}
        except Exception as e:
            logger.exception("Failing with %r", str(e))
        return rD

    def __getNetworkTraffic(self):
        rD = {"trafficIn": 0, "trafficOut": 0}
        try:
            #
            net1Out = psutil.net_io_counters().bytes_sent
            net1In = psutil.net_io_counters().bytes_recv
            time.sleep(1)
            net2Out = psutil.net_io_counters().bytes_sent
            net2In = psutil.net_io_counters().bytes_recv

            # Compare and get current speed
            if net1In > net2In:
                currentIn = 0
            else:
                currentIn = net2In - net1In

            if net1Out > net2Out:
                currentOut = 0
            else:
                currentOut = net2Out - net1Out
            rD = {"trafficIn": currentIn, "trafficOut": currentOut}
        except Exception as e:
            logger.exception("Failing with %r", str(e))
        return rD
