# -*- coding: utf-8 -*-
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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
import psutil


# Decorador para deshabilitar en modo seguro
def disableInSecureMode(decoratedCls):
    if globalVars.appArgs.secure:
        return lambda *args, **kwargs: None
    return decoratedCls

@disableInSecureMode
class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = _("Medir Wi-Fi")
    
    def __init__(self):
        # Verifica si NVDA se ejecuta en un entorno seguro
        if globalVars.appArgs.secure:
            return
        super(GlobalPlugin, self).__init__()
        self.monitoring = False
        self.start_time = None
        self.start_bytes = None

    @scriptHandler.script(
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
        ui.message(_("Monitoreo de uso de internet iniciado."))

    def stopMonitoring(self):
        if not self.monitoring:
            return
        end_time = time.time()
        end_bytes = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        total_bytes = end_bytes - self.start_bytes
        total_mb = total_bytes / (1024 * 1024)
        total_time = (end_time - self.start_time) / 60
        ui.message(_("Total de uso de internet: {:.2f} MB en {:.2f} minutos.").format(total_mb, total_time))
        self.monitoring = False

    def terminate(self):
        if self.monitoring:
            self.stopMonitoring()
