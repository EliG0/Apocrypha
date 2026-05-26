import random
from PyQt5.QtWidgets import *
import sys
from bank_check_password import check_password as cp
import sqlite3
import threading
import tempik
from bank_login_ui import Ui_Form
import datetime

class bank_login(QDialog, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setFixedSize(1024, 666)

        self.REGISTR.hide()
        self.REGISTR.move(20, 120)
        self.checkremember()
        self.regbtn.clicked.connect(self.logtoreg)
        self.backbtn.clicked.connect(self.logtoreg)
        self.contbtn.clicked.connect(self.check)
        self.contbtn_r.clicked.connect(self.check_r)
        self.login_label.textEdited.connect(self.lv1)
        self.login_label_r.textEdited.connect(self.lv2)
        self.password_label.textEdited.connect(self.pv1)
        self.password_label_r.textEdited.connect(self.pv2)
        self.password_label_rr.textEdited.connect(self.pv2)
        self.bug.clicked.connect(self.bugreg)

    def return_current_date(self):
        s = {1: 'января', 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня", 7: "июля", 8: "августа",
             9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"}
        current_date = datetime.datetime.now().strftime(f'%d %m %Y, %H:%M').split()
        current_date[1] = s[int(current_date[1])]
        current_date = ' '.join(current_date)
        return current_date


    def checkremember(self):
        temp_login = tempik.check_text()
        if temp_login:
            self.login_label.setText(temp_login[0])
            self.password_label.setText(temp_login[1])
            self.rememba.setChecked(True)
            threading.Timer(0.3, self.check).start()

    def bugreg(self):
        if self.REGISTR.isHidden():
            self.login_label.setText('+7 (000) 000 - 00 - 00')
            self.password_label.setText('admin')
            self.rememba.setChecked(True)
            self.check()
        else:
            self.login_label_r.setText('+7 (000) 000 - 00 - 00')
            self.username.setText('testik')
            self.password_label_r.setText('Abracadabra1')
            self.password_label_rr.setText('Abracadabra1')

    def lv1(self):
        if not self.login_label.inputMask():
            self.login_label.setInputMask('+7 (999) 999 - 99 - 99')

    def lv2(self):
        if not self.login_label_r.inputMask():
            self.login_label_r.setInputMask('+7 (999) 999 - 99 - 99')
        self.pv2()

    def pv1(self):
        if self.error.text() != '':
            self.error.setText('')

    def pv2(self):
        if self.error_r.text() != '':
            self.error_r.setText('')

    def check(self):
        self.error.setText('')
        if self.REGISTR.isHidden():
            try:
                assert len(self.login_label.text())
                assert len(self.password_label.text())
                log = ''.join(self.login_label.text().split()).replace('-', '').replace('(', '').replace(')', '')
                result = (sqlite3.connect('test.db').cursor().execute(
                    f"""SELECT * FROM main WHERE telnum = '{log}'""").fetchone())

                # pas check
                pas = self.password_label.text()
                assert result
                assert pas == result[2]
                if self.rememba.isChecked() and not tempik.check_text():
                    tempik.create_temp(result[3], result[2], result[1])

                elif not self.rememba.isChecked():
                    tempik.create_temp(result[1])
                self.dbresult = result[0]
                super().accept()

            except AssertionError:
                self.error.setText('Неверный логин или пароль.')

    def check_r(self):
        log = ''.join(self.login_label_r.text().split()).replace('-', '').replace('(', '').replace(')', '')
        us = self.username.text()
        pas = self.password_label_r.text()
        pas2 = self.password_label_rr.text()
        if log and us and pas and pas2:
            try:
                if pas != pas2 or cp(pas2) != 'ok':
                    raise ValueError()
                result = len(sqlite3.connect('test.db').cursor().execute(f"""SELECT id FROM main""").fetchall())
                telik = [''.join(x) for x in
                         sqlite3.connect('test.db').cursor().execute(f"""SELECT telnum FROM main""").fetchall()]
                assert log not in telik
                insert_new_user = sqlite3.connect('test.db')
                new_card = self.card_gen()
                insert_new_user.cursor().execute(
                    f'''INSERT INTO main VALUES ({result}, '{us}', '{pas}', '{log}', {new_card}, 0, 'Visa Classic', "Не указывать", 0,0,0)''')
                insert_new_user.commit()
                tempik.create_temp(us)
                # создаем бд
                create_bd = sqlite3.connect('data.sqlite')
                create_bd.execute(
                    f"""CREATE TABLE id{result}_data (Дата, "Тип операции", Категория, Сумма, Валюта, "Сумма в рублях", Описание, "Номер счета/карты списания");""")
                create_bd.commit()
                insert_bd = sqlite3.connect('data.sqlite')
                insert_bd.cursor().execute(
                    f'''INSERT INTO id{result}_data VALUES ("{self.return_current_date()}", 'Пополнение', 'Банк', '0', 'RUB', 0, 'Присоединение к банку', "{new_card}")''')
                insert_bd.commit()


                self.dbresult = (sqlite3.connect('test.db').cursor().execute(
                    f"""SELECT id FROM main WHERE telnum = '{log}'""").fetchone())[0]
                super().accept()
            except AssertionError:
                self.error_r.setText('Такой пользователь уже существует.')
            except ValueError:
                self.error_r.setText('Введите корректный пароль.')
        else:
            self.error_r.setText('Введите данные.')

    def card_gen(self):
        def Luhn(card):
            try:
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
                    return card

            except AssertionError:
                return False

        while True:
            test = Luhn(str(random.randrange(1000000000000000, 9999999999999999)))
            if test:
                break
        return test

    def logtoreg(self):
        if self.LOGIN.isHidden():
            self.LOGIN.show()
            self.REGISTR.hide()
        else:
            self.LOGIN.hide()
            self.REGISTR.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = bank_login()
    ex.show()
    sys.exit(app.exec_())
