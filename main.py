from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWebEngineWidgets import *
from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEnginePage, QWebEngineDownloadRequest
from PySide6.QtPrintSupport import *
import qdarkstyle
import os
import sys
import json
font = QFont("Lato", 10)

class XWBMainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(XWBMainWindow, self).__init__(*args, **kwargs)
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.setCentralWidget(self.tabs)
        self.fsmkey = QShortcut(QKeySequence("F11"), self)
        self.fsmkey.activated.connect(self.toggle_fullscreen)
        navtb = QToolBar("Navigation")
        self.addToolBar(navtb)
        
        browser_icon = QAction(QIcon('icon.png'), 'icon', self)
        navtb.addAction(browser_icon)
        
        back_btn = QAction(QIcon('back.png'), 'back', self)
        back_btn.triggered.connect(lambda:self.tabs.currentWidget().back())
        navtb.addAction(back_btn)

        forward_btn = QAction(QIcon('forward.png'), 'forward', self)
        forward_btn.triggered.connect(lambda:self.tabs.currentWidget().forward())
        navtb.addAction(forward_btn)

        reload_btn = QAction(QIcon('reload.png'), 'reload', self)
        reload_btn.triggered.connect(lambda:self.tabs.currentWidget().reload())
        navtb.addAction(reload_btn)
        
        home_btn = QAction(QIcon('home.png'), 'home', self)
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)

        navtb.addSeparator()

        self.urlBar = QLineEdit()
        self.urlBar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlBar)
        
        stop_btn = QAction(QIcon('cross.png'), 'stop', self)
        stop_btn.triggered.connect(lambda:self.tabs.currentWidget().stop())
        navtb.addAction(stop_btn)

        menu_btn = QAction(QIcon('menu.png'), 'Settings', self)
        menu_btn.triggered.connect(self.open_settings)
        navtb.addAction(menu_btn)
        # Load Settings
        self.load_settings()
        newtab_btn = QAction(QIcon('plus.png'), 'NewTab', self)
        newtab_btn.triggered.connect(lambda: self.add_new_tab())
        navtb.addAction(newtab_btn)
        
        self.homepage = "http://stelonek123.github.io/xilan-web-browser/"

        self.add_new_tab(QUrl(self.homepage), 'homepage')        
        self.showMaximized()
        self.setWindowTitle('Xilan Web Browser')

        self.download_dir = ''
    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                data = json.load(f)
                self.homepage = data.get("homepage", "http://stelonek123.github.io/xilan-web-browser/")
                self.download_dir = data.get("download_dir", "")
            if data.get("app_dark_mode"):
                self.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
            else:
                self.setStyleSheet("")
        except FileNotFoundError:
            pass
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showMaximized()
        else:
            self.showFullScreen()
    def add_new_tab(self, qurl=None, label="New Tab"):
        self.load_settings()
        if qurl == None:
            qurl = QUrl(self.homepage)
        browser = QWebEngineView()
        profile = browser.page().profile()
        profile.downloadRequested.connect(self.on_downloadRequested)
        bsettings = browser.settings()
        bsettings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        #browser.setAttribute(QWebEngineSettings.ForceDarkMode, True)
        browser.setUrl(qurl)

        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

        browser.urlChanged.connect(lambda qurl, browser = browser : self.update_url_bar(qurl, browser))

        browser.loadFinished.connect(lambda _, i= i, browser = browser : self.tabs.setTabText(i, browser.page().title()))

    def on_downloadRequested(self, download:QWebEngineDownloadRequest):
        msg = QDialog(self)
        label = QLabel("Downloading...")
        layout = QVBoxLayout()
        layout.addWidget(label)
        ok = QPushButton('Ok')
        ok.clicked.connect(msg.close)
        msg.setLayout(layout)
        msg.show()
        download.setDownloadDirectory(self.download_dir)
        download.accept()
        def on_state_changed(state):
            if state == QWebEngineDownloadRequest.DownloadState.DownloadInProgress:
                label.setText('Downloading...')
            elif state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
                label.setText('File downloaded succesfully!')
                layout.addWidget(ok)
        download.stateChanged.connect(on_state_changed)
        
        
    def tab_open(self, i):
        
        if i == -1:
            self.add_new_tab()

    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        self.update_url_bar(qurl, self.tabs.currentWidget())

        self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i):
        if self.tabs.count() <2:
            return
        
        self.tabs.removeTab(i)

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            return
        
        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle("% s - Xilan Web Browser " % title)
    
    def navigate_home(self, i):
        self.tabs.currentWidget().setUrl(QUrl(self.homepage))

    def navigate_to_url(self):
        q = QUrl(self.urlBar.text())
        if q.scheme() == "":
            q.setScheme("http")

        self.tabs.currentWidget().setUrl(q)


    def update_url_bar(self, q, browser = None):
        if browser != self.tabs.currentWidget():
            return

        self.urlBar.setText(q.toString())
        self.urlBar.setCursorPosition(0)

    def open_settings(self):
        self.settings_window = Settings(self)
        self.settings_window.exec()
        self.load_settings()

class Settings(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(300, 220)

        layout = QVBoxLayout()
        self.app_dark_mode = QCheckBox("Enable app darkmode")
        self.site_dark_mode = QCheckBox("Enable site darkmode")
        self.dwnld_dir = QLineEdit()
        self.homepage_setup = QComboBox()
        self.homepage_setup.addItem("Classic", "https://www.stelonek123.github.io/xilan-web-engine/")
        self.homepage_setup.addItem("Google", "https://google.com/")
        self.homepage_setup.addItem("DuckDuckGo!", "https://duckduckgo.com/")
        self.homepage_setup.addItem("Yahoo!", "https://yahoo.com/")
        self.homepage_setup.addItem("Bing", "https://bing.com/")

        save_btn = QPushButton('Save')
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.app_dark_mode)
        layout.addWidget(QLabel("HomePage"))
        layout.addWidget(self.homepage_setup)
        layout.addWidget(QLabel("Set download directory"))
        layout.addWidget(self.dwnld_dir)

        layout.addWidget(save_btn)

        self.setLayout(layout)
        self.load_settings()

    def save_settings(self):
        data = {
            "app_dark_mode": self.app_dark_mode.isChecked(),
            "homepage": self.homepage_setup.currentData(),
            "homepage_index": self.homepage_setup.currentIndex(),
            "download_dir" : self.dwnld_dir.text()
        }
        with open('settings.json', 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            self.close()

    def load_settings(self):
        try:
            with open("settings.json", 'r') as f:
                data = json.load(f)
            self.app_dark_mode.setChecked(data.get("app_dark_mode", False))
            self.site_dark_mode.setChecked(data.get("site_dark_mode", False))
            self.homepage_setup.setCurrentIndex(data.get("homepage_index", 0))
            self.dwnld_dir.setText(data.get("download_dir", None))
        except FileNotFoundError:
            pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(font)
    app.setWindowIcon(QIcon('icon.png'))
    app.setApplicationName("Xilan Web Browser")
    window = XWBMainWindow()
    app.exec()        
