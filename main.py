import sqlite3
import sys
from datetime import datetime as dt, timedelta

import matplotlib.pyplot as plt
import yfinance as yf
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from project import Ui_MainWindow
from date_dialog import Date_Dialog
from about_window import AboutWindow
from compare_window import Compare_Window
from diff_window import Diff_Window


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.figure = plt.figure()
        self.setLayout(self.verticalLayout)
        self.create_buttons()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.verticalLayout.addWidget(self.toolbar)
        self.verticalLayout.addWidget(self.canvas)
        self.setFixedSize(1280, 720)  # Фиксируем размер окна
        self.old_company = ''
        self.send = ''
        self.data = '0'
        self.stop = 0
        self.inter = ''
        self.pushButton_21.clicked.connect(self.add_fav)
        self.pushButton_22.clicked.connect(self.del_fav)
        self.pushButton_23.clicked.connect(self.compare_show)
        self.aboutwindow = AboutWindow()
        self.about_action.triggered.connect(self.about)
        self.inters = {'День': '1d', '5 дней': '5d', 'Неделя': '1wk', 'Месяц': '1mo',
                       '3 месяца': '3mo'}

    def create_buttons(self):  # Создаём кнопки
        btns = self.btn()
        for i in btns.keys():  # Берём названия из словаря
            if i == 'Amazon':
                continue
            a = QPushButton(i, self)
            a.clicked.connect(self.plot_demo)
            if btns[i] == 1:  # Проверяем есть ли кнопка в избранном
                self.verticalLayout_4.addWidget(a)  # Если да, то переносим в layout избранное
            else:
                self.verticalLayout_2.addWidget(a)  # Если нет, то переносим в layout компании

    def btn(self):  # Подключаем бд
        a = []
        con = sqlite3.connect('companies.sqlite')
        cur = con.cursor()

        result = cur.execute(f"""SELECT name, favorite FROM companies""")

        for i in result:
            a.append(i)
        return {k: v for k, v in a}  # Создаём словарь с именами и значением избранного

        con.close()

    def about(self):  # Вызываем окно 'О программе'
        self.aboutwindow.show()

    def compare_show(self):  # Вызываем окно сравнения
        self.compare = Compare_Window()
        self.compare.show()

    def add_fav(self):  # Добавляем в избранное
        con = sqlite3.connect('companies.sqlite')
        cur = con.cursor()

        cur.execute(f"""UPDATE companies
                    SET favorite = {1}
                    WHERE name = '{self.send}'""")

        con.commit()
        con.close()
        self.verticalLayout_4.addWidget(self.but)

    def del_fav(self):  # Удаляем из избранного
        con = sqlite3.connect('companies.sqlite')
        cur = con.cursor()

        cur.execute(f"""UPDATE companies
                    SET favorite = {2}
                    WHERE name = '{self.send}'""")

        con.commit()
        con.close()
        self.verticalLayout_2.addWidget(self.but)

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
        self.diff(self.send, *self.date_df(self.send), *self.price_df(self.send))  # Окно с разицей
        self.plot()  # Рисуем график

    def plot_demo(self):  # Подготовка к постройке графика
        self.send = self.sender().text()  # Текст отправителя сигнала
        self.but = self.sender()  # Отправитель сигнала
        self.date_inter()  # Вызываем диалог выбора интервала

    def diff(self, sd, date, pc):  # Вызов окна с разницей
        if date and pc:
            self.dw = Diff_Window(self.comp(sd), date, pc)
            self.dw.show()

    def date_df(self, name):  # Проверяем есть ли компания в избранном
        con = sqlite3.connect('companies.sqlite')
        cur = con.cursor()

        result = cur.execute(f"""SELECT date FROM companies
                            WHERE name = '{name}'""")

        for elem in result:
            return elem
        con.close()

    def price_df(self, name):  # Проверяем есть ли компания в избранном
        con = sqlite3.connect('companies.sqlite')
        cur = con.cursor()

        result = cur.execute(f"""SELECT price FROM companies
                            WHERE name = '{name}'""")

        for elem in result:
            return elem
        con.close()

    def plot(self):  # Рисуем график
        self.figure.clear()
        self.table(self.send)  # Обновляем БД
        company = self.comp(self.send)
        start = self.start
        stop = self.stop
        self.data = yf.download(*company, start, stop, interval=self.inter)['Adj Close']
        ax = self.figure.add_subplot(111)
        ax.plot(self.data)
        self.canvas.draw()

    def table(self, company):  # Обновляем дату и цену
        con = sqlite3.connect('companies.sqlite')
        cur = con.cursor()

        start = dt.now().date() - timedelta(days=7)  # Начало
        end = dt.now().date()  # Конец
        price = yf.download(*self.comp(company), start=start, end=end, interval="1m")['Adj Close'][
            -1]  # Актуальная цена

        cur.execute(f"""UPDATE companies
                    SET date = '{dt.now()}'
                    WHERE name = '{company}'""")
        cur.execute(f"""UPDATE companies
                    SET price = '{price}'
                    WHERE name = '{company}'""")

        con.commit()
        con.close()

    def comp(self, name):  # Достаём тикет из БД
        con = sqlite3.connect('companies.sqlite')
        cur = con.cursor()

        result = cur.execute(f"""SELECT site FROM companies
                            WHERE name = '{name}'""")

        for elem in result:
            return elem
        con.close()

    def like(self, name):  # Проверяем есть ли компания в избранном
        con = sqlite3.connect('companies.sqlite')
        cur = con.cursor()

        result = cur.execute(f"""SELECT favorite FROM companies
                                    WHERE name = '{name}'""")

        for elem in result:
            return elem
        con.close()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
