import random
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
from PyQt5.QtCore import *
import datetime
import threading
from tempik import forsuclog
from bank_suclog_ui import Ui_Dialog


class bank_suclog(QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.background.setPixmap(QPixmap(f':/wallpaper/{random.randrange(1, 21)}.png'))
        self.check_dt()

        self.running()

    def check_dt(self):
        tim = int(str(datetime.datetime.now().time())[:2])
        day = ''
        if 3 <= tim < 9:
            day = 'Доброго утра,'
        elif 9 <= tim < 15:
            day = 'Доброго дня,'
        elif 15 <= tim < 21:
            day = 'Доброго вечера,'
        elif 21 <= tim or tim < 3:
            day = 'Доброй ночи,'
        self.timelab.setText(day)

        self.name.setText(forsuclog() + '!')

    def running(self):
        threading.Timer(3.0, self.closing).start()
        self.anim = QPropertyAnimation(self.timelab, b"pos")
        self.anim.setEndValue(QPoint(30, 160))
        self.anim.setDuration(1000)
        self.anim.start()
        self.anim1 = QPropertyAnimation(self.name, b"pos")
        self.anim1.setEndValue(QPoint(30, 220))
        self.anim1.setDuration(1000)
        self.anim1.start()

    def closing(self):
        super().accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = bank_suclog()
    ex.show()
    sys.exit(app.exec_())
