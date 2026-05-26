from PyQt5.QtWidgets import *
import sys
from didinga_ui import Ui_daidengy


class daidengy(QDialog, Ui_daidengy):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # loadUi('didinga.ui', self)
        self.cardnum_label.setInputMask('9999999999999999')
        self.summa_label.setInputMask('999999')
        self.contbtn.clicked.connect(self.check)
        self.cardnum_label.textEdited.connect(self.lv1)
        self.summa_label.textEdited.connect(self.lv1)

    def lv1(self):
        if self.error.text() != '':
            self.error.setText('')

    def check(self):
        cardres = self.Luhn(self.cardnum_label.text())

        if cardres:
            super().accept()
            return int(self.summa_label.text())

    def Luhn(self, card):
        try:
            assert len(card)
            checksum = 0
            for count, num in enumerate(list(map(int, card))):
                if count % 2 == 0:
                    buffer = num * 2
                    if buffer > 9:
                        buffer -= 9
                    checksum += buffer
                else:
                    checksum += num
            res = checksum % 10 == 0
            assert res
            if res:
                return res

        except AssertionError:
            self.error.setText('Неверно набран номер карты.')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = daidengy()
    ex.show()
    sys.exit(app.exec_())
