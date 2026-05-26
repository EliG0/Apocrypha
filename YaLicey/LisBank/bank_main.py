import datetime
import os
import sqlite3
import sys
import threading

import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from pyqtgraph import mkPen

import tempik
from addfunction import add_fucntio
from bank_check_password import check_password as cp
from bank_login import bank_login
from bank_suclog import bank_suclog
from daigengy import daidengy
from mainui import Ui_MainWindow
from suc_perevod import sucess_perevod
from tempik import create_temp


# pyinstaller.exe --onefile --noconsole --icon=logofox.ico bank_main.py

class MyBank(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # loadUi('mainui.ui', self)
        self.startlogin()
        self.fillmainmenu()
        self.homebut.clicked.connect(self.gotohome)
        self.perevodbut.clicked.connect(self.gotohome)
        self.userbut.clicked.connect(self.gotohome)
        self.analizbut.clicked.connect(self.gotohome)
        self.daideneg.clicked.connect(self.createmoney)
        self.create_history()
        self.create_profil()
        self.smenit.clicked.connect(self.smenit_func)
        self.perevodkomy.currentTextChanged.connect(self.sistemaplatejei)
        self.SBP.hide()
        self.vihod.clicked.connect(self.sysexit)
        self.add_hist.clicked.connect(self.addfunc)
        self.din_but.clicked.connect(self.dinamika)
        self.din_but.clicked.connect(self.dinamika_perevod)
        self.dinamika()
        self.pev_but.clicked.connect(self.dinamika)
        self.pev_but.clicked.connect(self.dinamika_perevod)
        self.create_perevod_history()
        self.sbp_contbtn.clicked.connect(self.sbp_perevod)
        self.per_numtel.textEdited.connect(self.pce)
        self.per_summa.textEdited.connect(self.pce)
        self.janvaradd()
        self.janvar.setCurrentText('ноября')
        self.janvar.currentTextChanged.connect(self.updatedb)
        # ДОБАВИТЬ В БД

    def janvaradd(self):
        res = sqlite3.connect("data.sqlite").cursor().execute(
            f'SELECT Дата FROM id{self.idishnik}_data {'''WHERE "Категория" = "Перевод"'''
            if self.sender() == self.pev_but else ''}').fetchall()
        res = list(set([(x[0].split())[1] for x in res]))
        self.janvar.addItems(res)

    def addfunc(self):
        adddialog = add_fucntio()
        adddialog.exec_()
        if adddialog.result():
            to_hist = sqlite3.connect('data.sqlite')
            cur = to_hist.cursor()
            que = f'''INSERT INTO id{self.idishnik}_data VALUES ({adddialog.queresult} "{self.cardnum}")'''
            cur.execute(que)
            to_hist.commit()
            self.updatedb()

    def pce(self):
        self.sbp_error.setText('')

    def sbp_perevod(self):
        komy = self.perevodkomy.currentText()
        if komy == 'СБП':
            try:
                temp_num = ''.join(self.per_numtel.text().split()).replace('-', '').replace('(', '').replace(')', '')
                if len(temp_num) != 12:
                    raise ValueError('Введите корректный номер')
                if temp_num == self.telefonnum:
                    raise ValueError('Нельзя перевести самому себе')
                res = sqlite3.connect("test.db").cursor().execute(
                    f'''SELECT name FROM main WHERE telnum = "{temp_num}"''').fetchone()
                if not res:
                    raise ValueError('Такого пользователя не существует')
                if not self.per_summa.text() or not int(self.per_summa.text()):
                    raise ValueError('Нельзя перевести 0')
                if int(self.per_summa.text()) > self.current_price:
                    raise ValueError("На карте нет столько денег")
                new = self.current_price - int(self.per_summa.text())
                # убрать у старого
                con = sqlite3.connect('test.db')
                que = f'''UPDATE main
                            SET price = {new}
                            WHERE id = {self.idishnik}'''
                con.cursor().execute(que)
                con.commit()
                # зафиксировать в истории
                to_hist = sqlite3.connect('data.sqlite')
                cur = to_hist.cursor()
                que = f'''INSERT INTO id{self.idishnik}_data VALUES ('{self.return_current_date()}', 'Расходы', 
                "Перевод", {self.per_summa.text()}, "RUB", {self.per_summa.text()}, 
                "Перевод пользователю {temp_num} через СБП", "{self.cardnum}")'''
                cur.execute(que)
                to_hist.commit()
                # добавить новому
                con = sqlite3.connect('test.db')
                price_new = (sqlite3.connect('test.db').cursor().execute(
                    f"""SELECT id, price, cardnum FROM main WHERE telnum = '{temp_num}'""").fetchone())
                que = f'''UPDATE main SET price = 
{price_new[1] + int(self.per_summa.text())} WHERE telnum = "{temp_num}"'''
                con.cursor().execute(que)
                con.commit()
                # зафиксировать у нового в истории
                to_hist = sqlite3.connect('data.sqlite')
                cur = to_hist.cursor()
                que = f'''INSERT INTO id{price_new[0]}_data VALUES ('{self.return_current_date()}', 'Пополнение', 
                "Перевод", {self.per_summa.text()}, "RUB", {self.per_summa.text()},
                 "Перевод от пользователя {self.telefonnum} через СБП", "{price_new[2]}")'''
                cur.execute(que)
                to_hist.commit()
                self.updatedb()
                sucess_perevod(f"{temp_num}", f'{self.per_summa.text()} ₽', f'{str(self.current_price)}')
            except ValueError as e:
                self.sbp_error.setText(str(e))
        elif komy == 'Мобильная связь':
            try:
                temp_num = ''.join(self.per_numtel.text().split()).replace('-', '').replace('(', '').replace(')', '')
                if len(temp_num) != 12:
                    raise ValueError('Введите корректный номер')
                if not self.per_summa.text() or not int(self.per_summa.text()):
                    raise ValueError('Нельзя перевести 0')
                if int(self.per_summa.text()) > self.current_price:
                    raise ValueError("На карте нет столько денег")
                new = self.current_price - int(self.per_summa.text())
                # убрать у старого
                con = sqlite3.connect('test.db')
                que = f'''UPDATE main
                                       SET price = {new}
                                       WHERE id = {self.idishnik}'''
                con.cursor().execute(que)
                con.commit()
                # зафиксировать в истории
                to_hist = sqlite3.connect('data.sqlite')
                cur = to_hist.cursor()
                que = f'''INSERT INTO id{self.idishnik}_data VALUES ('{self.return_current_date()}', 'Расходы',
                 "Пополнение телефона", {self.per_summa.text()}, "RUB", {self.per_summa.text()}, 
                 "Пополнение номера телефона {temp_num}", "{self.cardnum}")'''
                cur.execute(que)
                to_hist.commit()
                sucess_perevod(f"{temp_num}", f'{self.per_summa.text()} ₽', f'{str(self.current_price)}')
                self.updatedb()
            except ValueError as e:
                self.sbp_error.setText(str(e))
        elif komy == 'Транспортная карта':
            try:
                if len(self.per_numtel.text()) == 0:
                    raise ValueError('Введите корректный номер')
                if not self.per_summa.text() or not int(self.per_summa.text()):
                    raise ValueError('Нельзя перевести 0')
                if int(self.per_summa.text()) > self.current_price:
                    raise ValueError("На карте нет столько денег")
                new = self.current_price - int(self.per_summa.text())
                # убрать у старого
                con = sqlite3.connect('test.db')
                que = f'''UPDATE main
                                                       SET price = {new}
                                                       WHERE id = {self.idishnik}'''
                con.cursor().execute(que)
                con.commit()
                # зафиксировать в истории
                to_hist = sqlite3.connect('data.sqlite')
                cur = to_hist.cursor()
                que = f'''INSERT INTO id{self.idishnik}_data VALUES ('{self.return_current_date()}', 'Расходы',
                 "Пополнение транспортной карты", {self.per_summa.text()}, "RUB", {self.per_summa.text()},
                  "Пополнение транспортной карты {self.per_numtel.text()}", "{self.cardnum}")'''
                cur.execute(que)
                to_hist.commit()

                sucess_perevod(f"{self.per_numtel.text()}", f'{self.per_summa.text()} ₽', f'{str(self.current_price)}')
                self.updatedb()
            except ValueError as e:
                self.sbp_error.setText(str(e))
        elif komy == "Благотворительность":
            try:
                if not self.per_summa.text() or not int(self.per_summa.text()):
                    raise ValueError('Нельзя пожертвовать 0')
                if int(self.per_summa.text()) > self.current_price:
                    raise ValueError("На карте нет столько денег")
                new = self.current_price - int(self.per_summa.text())
                # убрать у старого
                con = sqlite3.connect('test.db')
                que = f'''UPDATE main
                                            SET price = {new}
                                            WHERE id = {self.idishnik}'''
                con.cursor().execute(que)
                con.commit()
                # зафиксировать в истории
                to_hist = sqlite3.connect('data.sqlite')
                cur = to_hist.cursor()
                que = f'''INSERT INTO id{self.idishnik}_data VALUES ('{self.return_current_date()}', 'Расходы',
                 "Благотворительность", {self.per_summa.text()}, "RUB", {self.per_summa.text()}, 
                 "Пожертвования на благотворительность", "{self.cardnum}")'''
                cur.execute(que)
                to_hist.commit()
                sucess_perevod(f"Благотворительный фонд {self.blago.currentText()}", f'{self.per_summa.text()} ₽',
                               f'{str(self.current_price)}')
                self.updatedb()
            except ValueError as e:
                self.sbp_error.setText(str(e))
        self.per_summa.setText('')
        self.per_numtel.setText('')

    def create_perevod_history(self):
        res = sqlite3.connect("data.sqlite").cursor().execute(
            f'SELECT Дата, "Тип операции", Категория, Сумма, Валюта, Описание FROM id{self.idishnik}_data').fetchall()
        res = list(filter(
            lambda x: x[2] == 'Перевод' or x[2].split()[0] == "Пополнение" or x[2].split()[0] == 'Благотворительность',
            res[::-1]))
        if len(res):
            self.perevod_wid.setRowCount(len(res))
            self.perevod_wid.setColumnCount(len(res[0]))
            for i, elem in enumerate(res):
                for j, val in enumerate(elem):
                    self.perevod_wid.setItem(i, j, QTableWidgetItem(str(val)))
            self.perevod_wid.setHorizontalHeaderLabels(
                ['Дата', 'Тип операции', 'Категория', 'Сумма', 'Валюта', "Описание"])
        else:
            self.perevod_wid.clear()
            self.perevod_wid.setRowCount(1)
            self.perevod_wid.setColumnCount(1)
            self.perevod_wid.setItem(1, 1, QTableWidgetItem(str("Нет данных")))

    def dinamika_perevod(self):
        res = sqlite3.connect("data.sqlite").cursor().execute(
            f'SELECT Дата, "Тип операции", Сумма, Описание FROM id{self.idishnik}_data {
            '''WHERE "Категория" = "Перевод"''' if self.sender() == self.pev_but else ''}').fetchall()
        try:
            res = list(filter(
                lambda x: (x[0].split())[1] == (self.janvar.currentText() if self.janvar.currentText() else 'ноября'),
                res))
            if not res:
                raise ValueError("Нет данных")
            res = sorted(res, key=lambda x: int(x[2]), reverse=True)
            self.max_view.setRowCount(len(res))
            self.max_view.setColumnCount(len(res[0]))
            for i, elem in enumerate(res):
                for j, val in enumerate(elem):
                    self.max_view.setItem(i, j, QTableWidgetItem(str(val)))
            self.max_view.setHorizontalHeaderLabels(
                ['Дата', 'Тип операции', 'Сумма', 'Описание'])
        except ValueError as e:
            self.max_view.clear()
            self.max_view.setRowCount(1)
            self.max_view.setColumnCount(1)
            self.max_view.setItem(1, 1, QTableWidgetItem(str(e)))

    def dinamika(self):
        def create_month(mode, result):
            month = {}
            for x in range(0, 31):
                month[x] = 0
            if mode == 'min':
                res = list(filter(lambda x: x[2] == 'Расходы', result))
            elif mode == 'plus':
                res = list(filter(lambda x: x[2] == 'Пополнение', result))
            else:
                res = result
            for data in res:
                d = ((data[0].split(',')[0]).split())[0]
                month[int(d)] += int(data[1])
            elem = month.items()
            return elem

        self.per_view.clear()
        try:
            res = sqlite3.connect("data.sqlite").cursor().execute(
                f'SELECT Дата, Сумма, "Тип операции" FROM id{self.idishnik}_data {'''WHERE "Категория" = "Перевод"'''
                if self.sender() == self.pev_but else ''}').fetchall()
            res = list(filter(
                lambda x: (x[0].split())[1] == (self.janvar.currentText() if self.janvar.currentText() else 'ноября'),
                res))
            if not res:
                raise ValueError('Нет данных')
            self.per_view.addLegend()
            elem = create_month('min', res)
            self.per_view.plot([i[0] for i in elem], [i[1] for i in elem],
                               pen=mkPen(color=(255, 0, 0), width=1, style=Qt.DashLine))
            min = [int(x[1]) for x in elem]
            elem = create_month('plus', res)
            self.per_view.plot([i[0] for i in elem], [i[1] for i in elem],
                               pen=mkPen(color=(0, 255, 0), width=1, style=Qt.DashLine))

            maxres = max(max(min), max([int(x[1]) for x in elem]))
            self.per_view.showGrid(x=True, y=True)

            self.per_view.setLimits(xMin=-1, xMax=31, yMin=(-10), yMax=(maxres + ((5 * maxres) // 100)))
            self.per_view.setLabel("left", '<span style="color: white; font-size: 14px">Рублей</span>')
            self.per_view.setLabel("bottom", '<span style="color: white; font-size: 14px">Ноябрь (день)</span>')
        except ValueError as e:
            pass

    def sysexit(self):
        tempik.clear_temp()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def sistemaplatejei(self):
        def noth():
            self.SBP.hide()

        def sbp():
            self.blago.hide()
            self.per_summalab.setText('Сумма перевода')
            self.per_numtelab.setText('Номер телефона')
            self.sbp_contbtn.setText('ПЕРЕВЕСТИ')
            self.per_numtel.show()
            self.per_numtel.setInputMask('+7 (999) 999 - 99 - 99')
            self.SBP.show()

        def nomer():
            self.blago.hide()
            self.per_summalab.setText('Сумма пополнения')
            self.sbp_contbtn.setText('ПОПОЛНИТЬ')
            self.per_numtel.setInputMask('+7 (999) 999 - 99 - 99')
            self.per_numtel.show()
            self.SBP.show()

        def transp():
            self.blago.hide()
            self.per_numtelab.setText('Номер карты')
            self.per_summalab.setText('Сумма пополнения')
            self.sbp_contbtn.setText('ПОПОЛНИТЬ')
            self.sbp_contbtn.setText('ПЕРЕВЕСТИ')
            self.per_numtel.setInputMask("")
            self.per_numtel.show()
            self.SBP.show()

        def blago():
            self.per_numtelab.setText('Благотворительная организация')
            self.per_summalab.setText('Сумма')
            self.per_numtel.hide()

            self.blago.move(5, 25)
            self.blago.show()
            self.SBP.show()

        self.per_summa.setText('')
        self.per_numtel.setText('')
        self.per_summa.setInputMask('9999999999')
        s = {"": noth, 'СБП': sbp, "Мобильная связь": nomer, 'Транспортная карта': transp,
             'Благотворительность': blago}
        s[self.perevodkomy.currentText()]()

    def updatedb(self):
        self.res = self.dbresult
        self.res = (sqlite3.connect('test.db').cursor().execute(
            f"""SELECT * FROM main WHERE id = '{self.res[0]}'""").fetchone())
        self.idishnik = self.res[0]
        self.logen = self.res[1]
        self.pasa = self.res[2]
        self.telefonnum = self.res[3]
        self.cardnum = self.res[4]
        self.current_price = self.res[5]
        self.visastat = self.res[6]
        self.sexic = self.res[7]
        self.dinamika()
        self.dinamika_perevod()
        self.create_perevod_history()
        self.fillmainmenu()
        self.create_history()

    def smenit_func(self):
        con = sqlite3.connect('test.db')
        spisok_horosh = []
        st = 'font-size: 17px; border-color: rgb(0, 255, 0);'
        # РЕАЛИЗОВАТЬ СИСТЕМУ >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        if self.name_label.text() != self.logen:
            spisok_horosh.append('Имя')
            self.name_label.setStyleSheet(st)
            que = f'''UPDATE main SET name = "{self.name_label.text()}" WHERE id = {self.idishnik}'''
            con.cursor().execute(que)

        if self.telefon_label.text() != self.telefonnum:
            spisok_horosh.append('Номер телефона')
            self.telefon_label.setStyleSheet(st)
            que = f'''UPDATE main SET telnum = "{self.telefon_label.text()}" WHERE id = {self.idishnik}'''
            con.cursor().execute(que)

        if self.cardnum_profil.text() != self.cardnum:
            Luhntest = self.Luhn(self.cardnum_profil.text())
            if Luhntest:
                spisok_horosh.append('Номер карты')
                que = f'''UPDATE main SET cardnum = "{self.cardnum_profil.text()}" WHERE id = {self.idishnik}'''
                con.cursor().execute(que)
                self.cardnum_profil.setStyleSheet(st)
            else:
                self.cardnum_profil.setStyleSheet('border-color: rgb(255, 0, 0);')
                self.horosh.setText('Введите корректный номер карты')
        if self.visa_box.currentText() != self.visastat:
            spisok_horosh.append('Платежная система')
            que = f'''UPDATE main SET visasystem = "{self.visa_box.currentText()}" WHERE id = {self.idishnik}'''
            con.cursor().execute(que)
            self.visa_box.setStyleSheet('border-color: rgb(0, 255, 0);')
            self.cardvisa.setText(f'{self.visastat} ••{self.cardnum[-4:]}')

        if self.sex_box.currentText() != self.sexic:
            spisok_horosh.append('Пол')
            que = f'''UPDATE main SET sex = "{self.sex_box.currentText()}" WHERE id = {self.idishnik}'''
            con.cursor().execute(que)
            self.sex_box.setStyleSheet('border-color: rgb(0, 255, 0);')
        try:
            if self.password_label.text() != '' and self.sec_password_label.text() != '':
                if self.password_label.text() != self.sec_password_label.text():
                    self.password_label.setStyleSheet('border-color: rgb(255, 0, 0);')
                    self.sec_password_label.setStyleSheet('border-color: rgb(255, 0, 0);')
                    raise Exception('Пароли не сходятся')
                if cp(self.password_label.text()) != 'ok':
                    self.password_label.setStyleSheet('border-color: rgb(255, 0, 0);')
                    self.sec_password_label.setStyleSheet('border-color: rgb(255, 0, 0);')
                    raise Exception('Введите корректный пароль')
                spisok_horosh.append('Пароль')
                que = f'''UPDATE main SET passw = "{self.password_label.text()}" WHERE id = {self.idishnik}'''
                con.cursor().execute(que)
                self.password_label.setStyleSheet(st)
                self.sec_password_label.setStyleSheet(st)
            if len(spisok_horosh) > 2:
                spisok_horosh = spisok_horosh[:2] + ['и т.д.']
            if spisok_horosh:
                self.horosh.setText('Изменено: ' + ', '.join(spisok_horosh))
                con.commit()
                self.updatedb()
                self.create_profil()
                create_temp(self.telefonnum, self.pasa, self.logen)
            threading.Timer(2.5, self.clear_smenit).start()
        except Exception as e:
            self.horosh.setText(str(e))

    def clear_smenit(self):
        self.horosh.setText('')
        st = 'font-size: 17px;'
        s = [self.name_label, self.telefon_label, self.password_label, self.sec_password_label, self.cardnum_profil]
        for i in s:
            i.setText('')
            i.setStyleSheet(st)
            i.update()
        self.visa_box.setStyleSheet('')
        self.sex_box.setStyleSheet('')
        self.create_profil()

    def Luhn(self, card):
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

    def create_profil(self):
        self.prof_name.setText(self.logen)
        self.name_label.setText(self.logen)
        self.telefon_label.setText(self.telefonnum)
        self.cardnum_profil.setText(self.cardnum)
        self.visa_box.setCurrentText(self.visastat)
        self.sex_box.setCurrentText(self.sexic)
        s = {"Мужской": ":/logo/boy-dynamic-color.png", 'Женский': ":/logo/girl-dynamic-color.png",
             'Не указывать': ':/logo/logofox.png'}
        self.sexicon.setPixmap(QPixmap(s[self.sex_box.currentText()]))

    def return_current_date(self):
        s = {1: 'января', 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня", 7: "июля", 8: "августа",
             9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"}
        current_date = datetime.datetime.now().strftime(f'%d %m %Y, %H:%M').split()
        current_date[1] = s[int(current_date[1])]
        current_date = ' '.join(current_date)
        return current_date

    def createmoney(self):
        daideng = daidengy()
        daideng.exec_()
        if daideng.result():
            append_summ = daideng.check()
            new = str(self.current_price + append_summ)
            self.chet.setText(new + ' ₽')
            # update database
            con = sqlite3.connect('test.db')
            que = f'''UPDATE main
            SET price = {new}
            WHERE id = {self.idishnik}'''
            con.cursor().execute(que)
            con.commit()
            current_date = self.return_current_date()
            # insert new hirtory
            to_hist = sqlite3.connect('data.sqlite')
            cur = to_hist.cursor()
            que = f'''INSERT INTO id{self.idishnik}_data VALUES ('{current_date}', 'Пополнение', "Комиссия",
            {append_summ}, "RUB", {append_summ}, "Пополнение с карты другого банка", "{self.cardnum}")'''
            cur.execute(que)
            to_hist.commit()
            sucess_perevod(f"Мне ({self.logen})", f'{append_summ} ₽', f'{self.chet.text()}')
            self.updatedb()

    def create_history(self):
        res = sqlite3.connect("data.sqlite").cursor().execute(f'SELECT * FROM id{self.idishnik}_data').fetchall()
        res = res[::-1]
        self.tableWidget.setRowCount(len(res))
        self.tableWidget.setColumnCount(len(res[0]))
        for i, elem in enumerate(res):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.tableWidget.setHorizontalHeaderLabels(
            ['Дата', 'Тип операции', 'Категория', 'Сумма', 'Валюта', 'Сумма в рублях', 'Описание',
             'Номер счета/карты списания'])

    def startlogin(self):
        login_dialog = bank_login()
        login_dialog.exec_()
        if not login_dialog.result():
            sys.exit()
        result = (sqlite3.connect('test.db').cursor().execute(
            f"""SELECT * FROM main WHERE id = '{login_dialog.dbresult}'""").fetchone())
        self.dbresult = result
        self.updatedb()

        bank_suclog().exec_()

    def fillmainmenu(self):
        # money
        self.chet.setText(str(self.res[5]) + ' ₽')
        self.prof_name.setText(self.logen)
        self.cardvisa.setText(f'{self.visastat} ••{self.cardnum[-4:]}')
        # chvaluta
        data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
        usa = data['Valute']['USD']
        eur = data['Valute']['EUR']
        cny = data['Valute']['CNY']
        self.usdbuy.setText(str(round(usa["Value"] + (usa["Value"] / 100 * 5), 2)), )
        self.usdsell.setText(str(round(usa['Previous'] - (usa['Previous'] / 100 * 5), 2)))
        self.eurbuy.setText(str(round(eur["Value"] + (eur["Value"] / 100 * 5), 2)))
        self.eursell.setText(str(round(eur['Previous'] - (eur['Previous'] / 100 * 5), 2)))
        self.cnybuy.setText(str(round(cny["Value"] + (cny["Value"] / 100 * 5), 2)))
        self.cnysell.setText(str(round(cny['Previous'] - (cny['Previous'] / 100 * 5), 2)))
        #

    def gotohome(self):
        def st(x=60):
            return f'''font-size: 23pt; font-family: Neo Sans Pro; background-color: rgba(255, 255, 255, 30); 
        border-radius: 7px; border: 1px solid rgba(0,0,0,{x});'''

        s = {self.homebut: 0, self.analizbut: 1, self.perevodbut: 2, self.userbut: 3}
        self.tabWidget.setCurrentIndex(s[self.sender()])
        for i in s.keys():
            if i != self.sender():
                i.setStyleSheet(st())
            else:
                i.setStyleSheet(st(150))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyBank()
    ex.show()
    sys.exit(app.exec_())
