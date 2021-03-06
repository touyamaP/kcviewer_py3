# -*- coding: utf-8 -*-

from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QFrame,
                             QSizePolicy, QLabel, QPushButton, QSpacerItem,
                             QStyleOption, QStyle)
from PyQt5.QtGui import QPainter

import model
import utils
import time

MAX_FLEET_NUM = 4

class ExpeditionLabel(QLabel):
    def __init__(self, parent, deck_no):
        super(ExpeditionLabel, self).__init__(parent)
        self.parent = parent
        self.deck_no = deck_no
        self.parent.timer.timeout.connect(self.update)
        self.reload()

    def reload(self):
        con = self.parent.con
        port = model.Port(con)
        self.deck = port.deck(self.deck_no)
        self.update()

    @staticmethod
    def formattime(sec):
        h = int(sec/(60**2))
        m = int((sec % (60**2)) / 60)
        s = int(sec % 60)

        return '{:02d}:{:02d}:{:02d}'.format(h,m,s)

    @pyqtSlot()
    def update(self):
        prefix = '/' + str(self.deck_no)
        if self.deck.is_null():
            self.setText(prefix + '- 未開放')
        elif self.deck.api_mission[2] == 0:
            self.setText(prefix + '- ')
        else:
            sec = int(self.deck.api_mission[2]/1000 - int(time.time()))
            if sec < 0:
                sec = 0
            self.setText(prefix + '- ' + self.formattime(sec))

class ExpeditionBox(QWidget):
    def __init__(self, parent):
        super(ExpeditionBox, self).__init__(parent)

        self.con = utils.connect_db()
        self.timer = QTimer()

        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)
        self.label = QLabel()
        self.label.setText('遠征')
        self.vbox.addWidget(self.label)

        # horizontal line
        self.line = QFrame(self)
        self.line.setFrameShape(QFrame.HLine)
        #self.line.setFrameShadow(QFrame.Sunken)
        self.line.setObjectName('hline')
        self.vbox.addWidget(self.line)
        self.fleets = []

        for i in range(1, MAX_FLEET_NUM):
            label = ExpeditionLabel(self, i+1)
            self.vbox.addWidget(label)
            self.fleets.append(label)
        self.timer.start(1000)

    @pyqtSlot()
    def on_status_change(self):
        for fleet in self.fleets:
            fleet.reload()

    # for apply stylesheet
    def paintEvent(self, pe):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        s = self.style()
        s.drawPrimitive(QStyle.PE_Widget, opt, p, self)

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    box = ExpeditionBox()
    box.show()

    ret = app.exec_()
    app = None
    sys.exit(ret)
