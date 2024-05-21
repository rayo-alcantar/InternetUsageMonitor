# -*- coding: utf-8 -*-
# Addon para NVDA que monitorea el uso de internet
# Copyright (C) 2024 Ángel Alcantar <rayoalcantar@gmail.com>
# This file is covered by the GNU General Public License.
# Agradecimientos a Cary-rowen <manchen_0528@outlook.com>
# Agradecimientos a hwf1324 <1398969445@qq.com>
# creadores de objWatcher, de donde se tomó la idea para manejar las pulsaciones del atajo de teclado.

import globalPluginHandler
import globalVars
import scriptHandler
import ui
import tones
import time
import threading
from .timer import Timer
import wx
import gui
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
        self.stop_thread = False
        self.verify_thread = None
        self.mb_limit = None

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

    @scriptHandler.script(
        description=_("Lanza un diálogo para establecer un límite en mb en el que el usuario será avisado para que tome las acciones pertinentes."),
        gesture="kb:shift+NVDA+w"
    )
    def script_setMbLimit(self, gesture):
        if not self.monitoring:
            # Translators: Error message to warn the user to start monitoring first before setting an mb limit.
            ui.message(_("Es necesario iniciar el monitoreo primero."))
            return

        dialog = wx.TextEntryDialog(
            gui.mainFrame,
            # Translators: Text box title where the user is asked to enter the consumption limit in mb.
            _("Ingrese el límite (en mb) de consumo de red para ser advertido:"),
            # Translators: Dialog title where the text box will be contained.
            _("Límite de consumo"),
            ""
        )
        def callback(result):
            if result == wx.ID_OK:
                limit = int(dialog.GetValue())
                if limit <= 0:
                    ui.message(_("Ingrese un límite válido (mayor a 0)."))
                    return

                self.mb_limit = limit
                self.verify_thread = threading.Thread(target=self.checkLimit)
                self.verify_thread.start()
                # Translators: Message that indicates to the user that the network consumption limit has been set correctly.
                ui.message(_("Límite establecido correctamente."))

        gui.runScriptModalDialog(dialog, callback)

    def checkLimit(self):
        verify = Timer()
        beep = Timer()
        needs_beep = False
        while self.monitoring and not self.stop_thread:
            if verify.elapsed(1, False):
                verify.restart()
                current_bytes = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
                total_mb = (current_bytes - self.start_bytes) / (1024 * 1024)
                needs_beep = total_mb >= self.mb_limit

            if needs_beep and beep.elapsed(30, False):
                beep.restart()
                tones.beep(100, 150)
                # Translators: Warning message to the user that has reached the previously established limit, this will be repeated every 30 seconds until monitoring is deactivated.
                ui.message(_("¡Has alcanzado el límite de consumo establecido!"))

            time.sleep(0.05)
            
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
    
        # Convert total time to hours, minutes, and seconds
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        total_mb = (current_bytes - self.start_bytes) / (1024 * 1024)
    
        if total_mb >= 1000:
            total_gb = total_mb / 1024
            usage = "{:.2f} GB".format(total_gb)
        else:
            usage = "{:.2f} MB".format(total_mb)
        
        # Check if the total time is more than an hour for reporting
        if hours > 0:
            # Translators: Message announced when internet usage is reported. Displays usage in appropriate units, and time in hours, minutes, and seconds.
            message = _("Uso de Internet: {}, Tiempo: {} horas, {} minutos y {} segundos").format(usage, hours, minutes, seconds)
        else:
            # Translators: Message announced when internet usage is reported. Displays usage in appropriate units, and time in minutes and seconds.
            message = _("Uso de Internet: {}, Tiempo: {} minutos y {} segundos").format(usage, minutes, seconds)
        
        ui.message(message)
        if stopMonitoring:
            self.monitoring = False
            # Translators: Notifies the user that Internet usage monitoring has been stopped.
            ui.message(_("Monitoreo detenido."))
            if self.verify_thread is not None:
                self.stop_thread = True
                self.verify_thread = None
                self.stop_thread = False
                self.mb_limit = None
    
    def terminate(self):
        if self.monitoring:
            self.reportUsage(stopMonitoring=True)

        if self.verify_thread is not None:
            self.stop_thread = True
            self.verify_thread = None
            self.stop_thread = False
            self.mb_limit = None
