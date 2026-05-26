from PyQt5.QtWidgets import *
import sys
from suc_perevod_ui import Ui_Dialog


class suc_perevod(QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.countbtn.clicked.connect(self.closing)
        self.suc.clicked.connect(self.closing)
    def closing(self):
        super().accept()
        # loadUi('bank_suclog.ui', self)

def sucess_perevod(komy,skolko,ostatok):
    test = suc_perevod()
    test.dkomy.setText(komy)
    test.dskolko.setText(skolko)
    test.dostalos.setText(ostatok)
    test.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.exit(app.exec_())