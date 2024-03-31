﻿# -*- coding: utf-8 -*-
# Addon para NVDA que monitorea el uso de internet
# Copyright (C) 2024 Ángel Alcantar <rayoalcantar@gmail.com>
# This file is covered by the GNU General Public License.

import globalPluginHandler
import globalVars
import scriptHandler
import ui
import time
import addonHandler
addonHandler.initTranslation()
import sys
import os
import sys
dirAddon=os.path.dirname(__file__)
sys.path.append(dirAddon)
sys.path.append(os.path.join(dirAddon, "lib"))
import psutil
psutil.__path__.append(os.path.join(dirAddon, "lib", "psutil"))
del sys.path[-2:]


# Decorador para deshabilitar en modo seguro
def disableInSecureMode(decoratedCls):
    if globalVars.appArgs.secure:
        return globalPluginHandler.GlobalPlugin
    return decoratedCls

@disableInSecureMode
class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    # translators: Category name for all scripts provided by the Internet Usage Monitor add-on.
    scriptCategory = _("InternetUsageMonitor")
    
    def __init__(self):
        super(GlobalPlugin, self).__init__()
        self.monitoring = False
        self.start_time = None
        self.start_bytes = None

    @scriptHandler.script(
        # translators: Description for a script that toggles the monitoring of internet usage on or off.
        description=_("Comienza o detiene el monitoreo del uso de internet."),
        gesture="kb:alt+NVDA+w",
        category=scriptCategory
    )
    def script_toggleInternetUsageMonitor(self, gesture):
        if not self.monitoring:
            self.startMonitoring()
        else:
            self.stopMonitoring()

    def startMonitoring(self):
        if self.monitoring:
            return
        self.monitoring = True
        self.start_time = time.time()
        self.start_bytes = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        # translators: This message is announced when the internet usage monitoring starts.
        ui.message(_("Monitoreo de uso de internet iniciado."))

    def stopMonitoring(self):
        if not self.monitoring:
            return
        end_time = time.time()
        end_bytes = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        total_bytes = end_bytes - self.start_bytes
        total_mb = total_bytes / (1024 * 1024)
        total_seconds = end_time - self.start_time
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        # translators: Announced to the user when the monitoring of internet usage stops, showing the total internet usage in megabytes and the duration in minutes and seconds.
        ui.message(_("Total de uso de internet: {:.2f} MB en {} minutos y {} segundos.").format(total_mb, minutes, seconds))
        self.monitoring = False
        self.start_time = None
        self.start_bytes = None

    def terminate(self):
        if self.monitoring:
            self.stopMonitoring()