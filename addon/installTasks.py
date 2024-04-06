# -*- coding: utf-8 -*-
# TimeCalculator es un complemento para calcular el tiempo.
# Este archivo está cubierto por la Licencia Pública General de GNU.
# Consulta el archivo COPYING para más detalles.
# Última actualización 2024
# Derechos de autor (C) 2024 Ángel Alcántar <rayoalcantar@gmail.com>

import addonHandler
addonHandler.initTranslation()

class donate:
    def open():
        import webbrowser
        # Directamente abrir la página de PayPal sin especificar el idioma.
        webbrowser.open("https://www.paypal.com/paypalme/rayoalcantar")

    def request():
        import wx
        import gui
        
        # Translators: The title of the dialog requesting donations from users.
        title = _("Por favor, dona")
        
        # Translators: The text of the donate dialog
        message = _("""Internet Usage Monitor - complemento gratuito para NVDA.
Puedes hacer una donación a Ángel Alcántar para ayudar en el desarrollo futuro de este complemento.
¿Quieres hacer una donación ahora? Para la transacción, serás redirigido al sitio web de PayPal.""")
        
        name = addonHandler.getCodeAddon().manifest['summary']
        if gui.messageBox(message.format(name=name), title, style=wx.YES_NO|wx.ICON_QUESTION) == wx.YES:
            donate.open()
            return True
        return False

def onInstall():
    import globalVars
    if not globalVars.appArgs.secure:
        donate.request()