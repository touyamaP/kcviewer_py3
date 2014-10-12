# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QScrollArea, QSpacerItem, QSizePolicy, QListWidget,
                             QStackedLayout, QLineEdit, QPushButton)
from PyQt5.QtWebKitWidgets import QWebView, QWebPage
from PyQt5.QtCore import QFile, QSize, QStandardPaths, QTemporaryFile, QFileDevice, QIODevice
from PyQt5.QtGui import QPixmap, QImage, QPainter
from PyQt5.QtMultimedia import QAudioOutput, QAudioDeviceInfo, QAudio

from ui.shipstatus import PortStatus
from ui.expedition import ExpeditionBox
import resource
import os

class StatusPage(QWidget):
    def __init__(self, parent):
        super(StatusPage, self).__init__(parent)

        hbox = QHBoxLayout()
        self.setLayout(hbox)

        self.portstatus = PortStatus(self)
        sc = QScrollArea()
        sc.setWidgetResizable(True)
        sc.setWidget(self.portstatus)

        hbox.addWidget(sc)

        expdbox = QVBoxLayout()
        hbox.addLayout(expdbox)
        self.expedition = ExpeditionBox(self)
        expdbox.addWidget(self.expedition)
        expdbox.addItem(QSpacerItem(40, 20,
                                    QSizePolicy.Minimum,
                                    QSizePolicy.Expanding))

class SettingPage(QWidget):
    def __init__(self, parent):
        super(SettingPage, self).__init__(parent)

        vbox = QVBoxLayout()
        self.setLayout(vbox)

        self.location_edit = QLineEdit(self)
        self.location_edit.setSizePolicy(QSizePolicy.Expanding,
                                         self.location_edit.sizePolicy().verticalPolicy())
        #self.locationEdit.returnPressed.connect(self.changeLocation)

        vbox.addWidget(self.location_edit)

        vbox.addItem(QSpacerItem(40, 20,
                                 QSizePolicy.Minimum,
                                 QSizePolicy.Expanding))

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setObjectName("MainWindow")
        self.resize(818, 618)
        font = QtGui.QFont()
        font.setFamily("Serif")
        font.setPointSize(10)
        self.setFont(font)
        self.centralWidget = QWidget(self)
        self.centralWidget.setObjectName("centralWidget")
        self.verticalLayout = QVBoxLayout(self.centralWidget)
        self.verticalLayout.setObjectName("verticalLayout")

        self.web_view = QWebView(self.centralWidget)
        self.web_view.setUrl(QtCore.QUrl("about:blank"))
        self.web_view.setObjectName("web_view")
        self.web_view.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,
                                                QSizePolicy.Fixed))
        self.web_view.setMinimumSize(QSize(960, 560))
        self.web_view.setMaximumSize(QSize(9999, 560))

        self.verticalLayout.addWidget(self.web_view)
        self.setCentralWidget(self.centralWidget)

        status_box = QHBoxLayout()
        status_box.setContentsMargins(0,0,0,0)
        self.verticalLayout.addLayout(status_box)

        status_box.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        volume = QPushButton(self)
        volume.setCheckable(True)
        volume.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,
                                          QSizePolicy.Fixed))
        volume.setMinimumSize(QSize(40, 40))
        volume.setMaximumSize(QSize(40, 40))

        volume.setObjectName('volume')
        status_box.addWidget(volume)
        volume.clicked.connect(self.toggle_mute)

        take_ss = QPushButton(self)
        take_ss.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,
                                          QSizePolicy.Fixed))
        take_ss.setMinimumSize(QSize(40, 40))
        take_ss.setMaximumSize(QSize(40, 40))

        take_ss.setObjectName('screenshot')
        status_box.addWidget(take_ss)
        take_ss.clicked.connect(self.take_screenshot)

        hbox = QHBoxLayout()
        self.verticalLayout.addLayout(hbox)

        self.list_widget = QListWidget(self)
        self.list_widget.addItem(u'状態')
        self.list_widget.addItem(u'設定')
        self.list_widget.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,
                                                   QSizePolicy.MinimumExpanding))
        self.list_widget.setMinimumSize(QSize(100, 100))
        self.list_widget.setMaximumSize(QSize(100, 9999))

        hbox.addWidget(self.list_widget)

        self.stacked_layout = QStackedLayout(self)
        hbox.addLayout(self.stacked_layout)

        self.status_page = StatusPage(self)
        self.stacked_layout.addWidget(self.status_page)

        self.setting_page = SettingPage(self)
        self.stacked_layout.addWidget(self.setting_page)

        self.list_widget.currentRowChanged.connect(self.stacked_layout.setCurrentIndex)
        self.list_widget.setCurrentRow(0)

        self.retranslateUi(MainWindow)
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

        file = QFile(':/ui/stylesheet.css')
        file.open(QFile.ReadOnly)
        stylesheet = unicode(file.readAll(), encoding='utf8')
        self.setStyleSheet(stylesheet)

        self.web_view.loadFinished.connect(self.adjust_location)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "KCViewer"))

    def take_screenshot(self, clicked):
        import datetime,tempfile
        now = datetime.datetime.now()
        pic_location = QStandardPaths.writableLocation(QStandardPaths.PicturesLocation)

        frames = self.web_view.page().mainFrame().childFrames()
        for frame in frames:
            if frame.frameName() != 'game_frame': continue
            swf = frame.findFirstElement('embed#externalswf')
            if not swf.isNull():
                image = QImage(swf.geometry().size(), QImage.Format_ARGB32)
                painter = QPainter(image)
                swf.render(painter)
                painter.end()
                (fileno, tmppath) = tempfile.mkstemp(prefix=now.strftime('%Y%m%d%H%M%S-'),
                                                     suffix='.png',
                                                     dir=pic_location)
                qfile = QFile()
                qfile.open(fileno, QIODevice.WriteOnly, QFileDevice.AutoCloseHandle)
                image.save(qfile, 'png')

    def toggle_mute(self, clicked):
        if os.name == 'posix':
            import alsaaudio
            print(alsaaudio.mixers())

    def adjust_location(self):
        self.setting_page.location_edit.setText(self.web_view.url().toString())
