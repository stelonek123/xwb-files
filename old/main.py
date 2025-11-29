import sys
import os
import qdarkstyle
import json
from PySide6.QtWidgets import QApplication, QMainWindow, QToolBar, QLineEdit
from PySide6.QtWebEngineWidgets import *
from PySide6.QtCore import *
from PySide6 import QtGui
from PySide6.QtGui import QAction

htmlf = os.path.abspath('about.html')
Home = QUrl.fromLocalFile(htmlf)

class MainWindow(QMainWindow):
    def __init__(self):
        #Base Settings
        super(MainWindow, self).__init__()
        self.browser = QWebEngineView()
        self.browser.setUrl(Home)
        #Browser central widget
        self.setCentralWidget(self.browser)
        self.showMaximized()
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
        #MenuBar
        self.menuBar().addAction(QAction('Settings', self))
        #NavBar
        navbar = QToolBar()
        self.addToolBar(navbar)
        #Buttons
        back_btn = QAction('<<', self)
        back_btn.triggered.connect(self.browser.back)
        navbar.addAction(back_btn)
        

        forward_btn = QAction('>>', self)
        forward_btn.triggered.connect(self.browser.forward)
        navbar.addAction(forward_btn)

        reload_btn = QAction('reload', self)
        reload_btn.triggered.connect(self.browser.reload)
        navbar.addAction(reload_btn)

        home_btn = QAction('Home', self)
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)
        
        #Url Line
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.nav_to_url)
        navbar.addWidget(self.url_bar)

        self.browser.urlChanged.connect(self.update_url)

    def navigate_home(self):
        self.browser.setUrl(Home)
    def nav_to_url(self):
        url = self.url_bar.text()
        self.browser.setUrl(QUrl(url))
    def update_url(self, q):
        self.url_bar.setText(q.toString())
#   def udata_saving(self, site, uname, password):
#       USER_DATA_W.write()
app = QApplication(sys.argv)
QApplication.setApplicationName('Xilan Web Browser')
app.setWindowIcon(QtGui.QIcon('icon.png'))
window = MainWindow()
app.exec_()