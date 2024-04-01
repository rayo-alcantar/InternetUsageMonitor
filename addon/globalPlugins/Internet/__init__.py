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
    # translators: Description for the script that toggles monitoring of internet usage. The script starts monitoring if it's not already happening, and stops it if it's in progress. A double press will stop the monitoring and report the usage.
    scriptCategory = _("Internet usage monitor")

    def __init__(self):
        super(GlobalPlugin, self).__init__()
        self.monitoring = False
        self.lastPressTime = 0
        self.start_time = None
        self.start_bytes = None
        self.timer = None

    @scriptHandler.script(
        description=_("Comienza a monitorear el uso de Internet o reporta el uso desde el inicio. Doble pulsación para detener."),
        gesture="kb:alt+NVDA+w"
    )
    def script_toggleInternetUsageMonitor(self, gesture):
        currentTime = time.time()
        if currentTime - self.lastPressTime < 0.5:  # Doble pulsación
            if self.monitoring:
                self.reportUsage(stopMonitoring=True)
        else:  # Pulsación simple
            if not self.monitoring:
                self.startMonitoring()
            else:
                self.reportUsage(stopMonitoring=False)
        self.lastPressTime = currentTime

    def startMonitoring(self):
        self.monitoring = True
        self.start_time = time.time()
        self.start_bytes = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        # translators: Message announced when internet usage monitoring starts.
        ui.message(_("Monitoreo de uso de Internet iniciado."))


    def reportUsage(self, stopMonitoring=False):
        current_time = time.time()
        current_bytes = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        total_seconds = int(current_time - self.start_time)
        total_minutes = total_seconds // 60  # Calcula los minutos totales desde los segundos
        remaining_seconds = total_seconds % 60  # Calcula los segundos restantes después de convertir a minutos
        total_mb = (current_bytes - self.start_bytes) / (1024 * 1024)
        #Translators: Explain that Internet usage will be reported in MB and time in minutes and seconds.
        ui.message(_("Uso de Internet: {:.2f} MB, Tiempo: {} minutos y {} segundos").format(total_mb, total_minutes, remaining_seconds))
        if stopMonitoring:
            self.monitoring = False
            #Translators: Notifies the user that Internet usage monitoring has been stopped.
            ui.message(_("Monitoreo detenido."))
    def terminate(self):
        if self.monitoring:
            self.reportUsage(stopMonitoring=True)