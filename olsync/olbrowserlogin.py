"""Ol Browser Login Utility"""
##################################################
# MIT License
##################################################
# File: olbrowserlogin.py
# Description: Overleaf Browser Login Utility
# Author: Moritz Glöckl
# License: MIT
# Version: 1.1.6
##################################################

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

# Where to get the CSRF Token and where to send the login request to
LOGIN_URL = "https://www.overleaf.com/login"
PROJECT_URL = "https://www.overleaf.com/project"  # The dashboard URL
# JS snippet to extract the csrfToken
JAVASCRIPT_CSRF_EXTRACTOR = "document.getElementsByName('ol-csrfToken')[0].content"
# Name of the cookies we want to extract
COOKIE_NAMES = ["overleaf_session2", "GCLB"]


class OlBrowserLoginWindow(QMainWindow):
    """
    Overleaf Browser Login Utility
    Opens a browser window to securely login the user and returns relevant login data.
    """

    def __init__(self, *args, **kwargs):
        super(OlBrowserLoginWindow, self).__init__(*args, **kwargs)

        self.webview = QWebEngineView()

        self._cookies = {}
        self._csrf = ""
        self._login_success = False

        self.profile = QWebEngineProfile(self.webview)
        self.cookie_store = self.profile.cookieStore()
        self.cookie_store.cookieAdded.connect(self.handle_cookie_added)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)

        self.profile.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)

        webpage = QWebEnginePage(self.profile, self)
        self.webview.setPage(webpage)
        self.webview.load(QUrl.fromUserInput(LOGIN_URL))
        self.webview.loadFinished.connect(self.handle_load_finished)

        self.setCentralWidget(self.webview)
        self.resize(600, 700)

    def handle_load_finished(self):
        def callback(result):
            self._csrf = result
            self._login_success = True
            QCoreApplication.quit()

        if self.webview.url().toString() == PROJECT_URL:
            self.webview.page().runJavaScript(
                JAVASCRIPT_CSRF_EXTRACTOR, callback
            )

    def handle_cookie_added(self, cookie):
        cookie_name = cookie.name().data().decode('utf-8')
        if cookie_name in COOKIE_NAMES:
            self._cookies[cookie_name] = cookie.value().data().decode('utf-8')

    @property
    def cookies(self):
        return self._cookies

    @property
    def csrf(self):
        return self._csrf

    @property
    def login_success(self):
        return self._login_success


def login():
    app = QApplication([])
    ol_browser_login_window = OlBrowserLoginWindow()
    ol_browser_login_window.show()
    app.exec()

    if not ol_browser_login_window.login_success:
        return None

    return {"cookie": ol_browser_login_window.cookies, "csrf": ol_browser_login_window.csrf}
