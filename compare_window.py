import sys
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow, QInputDialog, QCheckBox
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime as dt
import sqlite3
from compare import Ui_CompareWindow
from date_dialog import Date_Dialog


class Compare_Window(QMainWindow, Ui_CompareWindow):  # Окно сравнения
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.table()

        self.btns = []  # Создаём список
        for i in self.a.keys():  # Кидаем в него чекбоксы
            a = QCheckBox(i, self)
            a.setFont(font)
            self.btns.append(a)
            self.verticalLayout_3.addWidget(a)

        self.setFixedSize(370, 220)
        self.pushButton.clicked.connect(self.date_inter)
        self.pushButton_2.clicked.connect(self.check_all)
        self.pushButton_3.clicked.connect(self.uncheck_all)
        self.inters = {'День': '1d', '5 дней': '5d', 'Неделя': '1wk', 'Месяц': '1mo',
                       '3 месяца': '3mo'}

    def check_all(self):
        for i in self.btns:
            i.setChecked(True)

    def uncheck_all(self):
        for i in self.btns:
            i.setChecked(False)

    def date_inter(self):  # Выбор интервала
        text, ok = QInputDialog.getItem(self, "Интервал",
                                        "Выберите желаемый интервал",
                                        ("День", "5 дней", "Неделя", "Месяц", "3 месяца"), 4, False)

        if ok and text:
            self.inter = self.inters.get(text)
        else:
            self.inter = '3mo'
        self.stop = dt.now().date()

        self.start_date()  # Вызываем календарь

    def start_date(self):  # Вызывам календарь
        self.dialog = Date_Dialog()
        self.dialog.submitClicked.connect(self.date)
        self.dialog.show()

    def date(self, st):  # Принимаем значение из дочернего окна
        self.start = st
        self.plot()

    def plot(self):  # Рисуем график
        start = self.start
        stop = self.stop

        for i in self.btns:
            if i.isChecked():
                data = yf.download(self.a.get(i.text()),
                                   start, stop, interval=self.inter)['Adj Close'].plot(label=i.text())

        plt.title('Compare')
        plt.ylabel('Price')
        plt.xlabel('Date')
        plt.legend()
        plt.show()

    def table(self):  # Подключаем бд
        a = []
        con = sqlite3.connect('companies.sqlite')
        cur = con.cursor()

        result = cur.execute(f"""SELECT name, site FROM companies""")

        for i in result:
            a.append(i)
        self.a = {k: v for k, v in a}  # Создаём словарь с именами и тикетами

        con.close()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)
