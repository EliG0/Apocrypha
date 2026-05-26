from PyQt5.QtWidgets import *
import sys
import datetime
from PyQt5.QtCore import QDateTime
from add_function_ui import Ui_Dialog


class add_fucntio(QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.curr_data.stateChanged.connect(self.usdata)
        self.add_hist.clicked.connect(self.add_to_hist)
        self.summa_l.setInputMask('999999')
        self.data_l.dateTimeChanged.connect(self.curr_data_clear)

    def curr_data_clear(self):
        self.curr_data.setCheckState(False)

    def add_to_hist(self):
        try:
            if not self.data_l.text():
                raise ValueError('Введите корректную дату')
            if not self.cat_l.text():
                raise ValueError('Введите корректную категорию')
            if not int(self.summa_l.text()):
                raise ValueError('Не может быть равно 0')
            self.usdata()
            super().accept()
            que = f''''{self.usdata('return')}', '{self.type_c.currentText()}', "{self.cat_l.text()}",
                        {self.summa_l.text()}, "RUB", {self.summa_l.text()}, "{self.opis_l.text() if self.opis_l.text() else "Добавление вручную"}",'''
            self.queresult = que
        except ValueError as e:
            self.error.setText(str(e))

    def usdata(self, mode='return'):
        s = {1: 'января', 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня", 7: "июля", 8: "августа",
             9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"}
        current_date = datetime.datetime.now().strftime(f'%d %m %Y, %H:%M').split()
        current_date[1] = s[int(current_date[1])]
        current_date = ' '.join(current_date)
        if mode == "return":
            return current_date
        elif self.sender() == self.curr_data:
            self.data_l.setDateTime(QDateTime.currentDateTime())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = add_fucntio()
    ex.show()
    sys.exit(app.exec_())
