# -*- coding: utf-8 -*-

# Este archivo está cubierto por la Licencia Pública General de GNU.
# Última actualización 2024
# Derechos de autor (C) 2024 Ángel Alcántar <rayoalcantar@gmail.com>

import addonHandler

_N = _
addonHandler.initTranslation()

class donate:
    def open():
        import languageHandler
        import webbrowser
        lang = languageHandler.getLanguage()
        # This check ensures the donation page is presented in Spanish if applicable.
        if lang.startswith('es'):
            lang = 'es'
        else:
            lang = 'en'
        webbrowser.open(f"https://www.paypal.com/paypalme/rayoalcantar?lang={lang}")

    def request():
        import wx
        import gui
        
        # Translators: The title of the dialog requesting donations from users.
        title = _N("Por favor, dona")
        
        # Translators: The text of the donate dialog
        message = _("""Internet usage monitor  - complemento gratuito para NVDA.
Puedes hacer una donación a Ángel Alcántar para ayudar en el desarrollo futuro de este complemento.
¿Quieres hacer una donación ahora? Para la transacción, serás redirigido al sitio web de PayPal.""")
        
        name = addonHandler.getCodeAddon().manifest['summary']
        if gui.messageBox(message.format(name=name), title, style=wx.YES_NO|wx.ICON_QUESTION) == wx.YES:
            donate.open()
            return True
        return False

def onInstall():
    import globalVars
    # This checks if NVDA is running in a secure mode (e.g., on the Windows login screen),
    # which would prevent the addon from performing certain actions.
    if not globalVars.appArgs.secure:
        donate.request()