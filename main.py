import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLineEdit, QLabel, QTabBar, QFrame,
                             QStackedLayout, QShortcut, QKeySequenceEdit, QSplitter)
from PyQt5.QtGui import QIcon, QWindow, QImage, QKeySequence
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *


class AddressBar(QLineEdit):
    def __init__(self):
        super().__init__()

    def mousePressEvent(self, e):
        self.selectAll()


# main class
class App(QFrame):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Browser")
        # to connect to create function
        self.CreateApp()
        # to set the size of window
        self.setBaseSize(1366, 768)
        self.setWindowIcon(QIcon("logo_B.png"))

    # function to create the tabs
    def CreateApp(self):
        # crating a layout
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # creating a dynamic tab bar
        self.tabbar = QTabBar(movable=True, tabsClosable=True)

        # to connect to the close function on clicking cross
        self.tabbar.tabCloseRequested.connect(self.CloseTab)

        # to be able to switch tabs
        self.tabbar.tabBarClicked.connect(self.SwitchTab)

        # for default tab
        self.tabbar.setCurrentIndex(0)

        self.tabbar.setDrawBase(False)
        self.tabbar.setLayoutDirection(Qt.LeftToRight)
        self.tabbar.setElideMode(Qt.ElideLeft)

        # to create shortcuts in the browser new tab and reload
        self.shortcutNewtab = QShortcut(QKeySequence("Ctrl+T"), self)
        self.shortcutNewtab.activated.connect(self.AddTab)
        self.shortcutReload = QShortcut(QKeySequence("Ctrl+R"), self)
        self.shortcutReload.activated.connect(self.Reload)

        # keep track of tabs
        self.tabCount = 0
        self.tabs = []

        # creating address bar
        self.Toolbar = QWidget()
        # we are using this to link with stylesheet
        self.Toolbar.setObjectName("Toolbar")
        self.ToolbarLayout = QHBoxLayout()
        self.addressbar = AddressBar()

        # to connect browseTo function
        self.addressbar.returnPressed.connect(self.BrowseTo)

        self.Toolbar.setLayout(self.ToolbarLayout)

        # creating toolbar buttons, connecting them to toolbar
        self.BackButton = QPushButton("<-")
        self.BackButton.clicked.connect(self.GoBack)
        self.ForwardButton = QPushButton("->")
        self.ForwardButton.clicked.connect(self.GoForward)
        self.ReloadButton = QPushButton("R")
        self.ReloadButton.clicked.connect(self.Reload)

        # creating new tab button,connecting them to toolbar
        self.AddTabButton = QPushButton("+")
        self.AddTabButton.clicked.connect(self.AddTab)

        # adding the items
        self.ToolbarLayout.addWidget(self.BackButton)
        self.ToolbarLayout.addWidget(self.ForwardButton)
        self.ToolbarLayout.addWidget(self.ReloadButton)
        self.ToolbarLayout.addWidget(self.addressbar)
        self.ToolbarLayout.addWidget(self.AddTabButton)

        # set main view
        self.container = QWidget()
        self.container.layout = QStackedLayout()
        self.container.setLayout(self.container.layout)

        self.layout.addWidget(self.tabbar)
        self.layout.addWidget(self.Toolbar)
        self.layout.addWidget(self.container)

        self.setLayout(self.layout)
        self.AddTab()
        self.show()

    # function to delete the tab
    def CloseTab(self, i):
        self.tabbar.removeTab(i)

    # function ot add new Tab
    def AddTab(self):
        i = self.tabCount
        self.tabs.append(QWidget())
        self.tabs[i].layout = QVBoxLayout()
        self.tabs[i].layout.setContentsMargins(0, 0, 0, 0)

        # used for switching the tabs
        self.tabs[i].setObjectName("tab" + str(i))

        # open web view
        self.tabs[i].content = QWebEngineView()
        self.tabs[i].content.load(QUrl.fromUserInput("http://google.com"))
        self.tabs[i].content.titleChanged.connect(lambda: self.SetTabContent(i, "title"))
        self.tabs[i].content.iconChanged.connect(lambda: self.SetTabContent(i, "icon"))
        self.tabs[i].content.urlChanged.connect(lambda: self.SetTabContent(i, "url"))

        # add web view to tabs layout using splitter
        self.tabs[i].splitview = QSplitter()
        self.tabs[i].layout.addWidget(self.tabs[i].splitview)
        self.tabs[i].splitview.addWidget(self.tabs[i].content)

        # add tab to top level stacked widget
        self.container.layout.addWidget(self.tabs[i])
        self.container.layout.setCurrentWidget(self.tabs[i])

        # set the tab at the top of the screen
        self.tabbar.addTab("New Tab")
        self.tabbar.setTabData(i, {"object": "tab" + str(i), "initial": i})
        self.tabbar.setCurrentIndex(i)

        self.tabCount += 1

    # function to switch tabs by receiving tab data and content
    def SwitchTab(self, i):
        if self.tabbar.tabData(i):
            tab_data = self.tabbar.tabData(i)["object"]
            tab_content = self.findChild(QWidget, tab_data)
            self.container.layout.setCurrentWidget(tab_content)

            # to update the url whenever we switch tabs
            new_url = tab_content.content.url().toString()
            self.addressbar.setText(new_url)

    def BrowseTo(self):
        text = self.addressbar.text()
        i = self.tabbar.currentIndex()
        tab = self.tabbar.tabData(i)
        wv = self.findChild(QWidget, tab).content

        # to check for correct input from the user
        if "http" not in text:
            if "." not in text:
                url = "https://www.google.com/#q=" + text
            else:
                url = "http://" + text
        else:
            url = text

        wv.load(QUrl.fromUserInput(url))

    def SetTabContent(self, i, type):
        '''
            self.tabs[i].objectName = tab1
            self.tabbar.tabData(i)["object"] = tab1
        '''
        tab_name = self.tabs[i].objectName()

        count = 0
        running = True

        # to update the address bar each time
        current_tab = self.tabbar.tabData(self.tabbar.currentIndex())["object"]

        if current_tab == tab_name and type == "url":
            new_url = self.findChild(QWidget, tab_name).content.url().toString()
            self.addressbar.setText(new_url)
            return False

        while running:
            tab_data_name = self.tabbar.tabData(count)

            if count >= 99:
                running = False

            if tab_name == tab_data_name["object"]:
                if type == "title":
                    newTitle = self.findChild(QWidget, tab_name).content.title()
                    self.tabbar.setTabText(count, newTitle)
                elif type == "icon":
                    newIcon = self.findChild(QWidget, tab_name).content.icon()
                    self.tabbar.setTabIcon(count, newIcon)
                running = False
            else:
                count += 1

    # function to go back page
    def GoBack(self):
        active_index = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(active_index)["object"]
        tab_content = self.findChild(QWidget, tab_name).content
        tab_content.back()

    # function to go next page
    def GoForward(self):
        active_index = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(active_index)["object"]
        tab_content = self.findChild(QWidget, tab_name).content
        tab_content.forward()

    # function to reload page
    def Reload(self):
        active_index = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(active_index)["object"]
        tab_content = self.findChild(QWidget, tab_name).content
        tab_content.reload()


# to run and close the tab
if __name__ == "__main__":
    app = QApplication(sys.argv)
    os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = "667"
    window = App()

    with open("webstyle.css", "r") as style:
        app.setStyleSheet(style.read())
    sys.exit(app.exec_())
