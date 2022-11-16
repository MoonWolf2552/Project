import sqlite3
import sys
from datetime import datetime as dt, timedelta

import matplotlib.pyplot as plt
import yfinance as yf
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QLabel, QVBoxLayout, QWidget, QPushButton, \
    QCheckBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from project import Ui_MainWindow
from date_dialog import Date_Dialog
from about_window import AboutWindow
from compare_window import Compare_Window
from diff_window import Diff_Window


class AboutWindow(QWidget):  # Окно 'О программе'
    def __init__(self):
        super(AboutWindow, self).__init__()
        self.setWindowTitle('О программе')
        self.setLayout(QVBoxLayout(self))
        self.info = QLabel('Автор - Терентьев Илья')
        self.info2 = QLabel('Информация взята с сайта finance.yahoo.com')
        self.layout().addWidget(self.info2)
        self.layout().addWidget(self.info)


class Ui_CompareWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(370, 220)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setGeometry(QtCore.QRect(10, 50, 351, 121))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 349, 119))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_2.addLayout(self.verticalLayout_3)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(10, 10, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(110, 10, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(250, 10, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setObjectName("pushButton_3")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 370, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Сравнение"))
        self.pushButton.setText(_translate("MainWindow", "Cравнить"))
        self.pushButton_2.setText(_translate("MainWindow", "Выбрать всё"))
        self.pushButton_3.setText(_translate("MainWindow", "Убрать всё"))


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


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))


class Date_Dialog(QtWidgets.QDialog, Ui_Dialog):  # Выбор начала отсчёта
    submitClicked = QtCore.pyqtSignal(str)  # Сигнал даты

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.dateEdit = QtWidgets.QDateEdit(self)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.dateEdit.setFont(font)
        self.dateEdit.setCalendarPopup(True)  # +++
        self.dateEdit.setTimeSpec(QtCore.Qt.LocalTime)
        self.dateEdit.setGeometry(QtCore.QRect(220, 31, 133, 30))
        self.ok_button = QPushButton('OK', self)
        self.ok_button.resize(50, 32)
        self.ok_button.move(380, 30)
        self.ok_button.clicked.connect(self.run)

    def run(self):
        self.submitClicked.emit('-'.join(self.dateEdit.text().split('.')[::-1]))  # передаёт дату главному окну
        self.close()


class Ui_Diff(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Diff"))


class Diff_Window(QWidget, Ui_Diff):  # Вывод разницы
    def __init__(self, company, date, pc):
        super(Diff_Window, self).__init__()
        self.setupUi(self)
        self.vlayout = QVBoxLayout(self)
        self.setLayout(self.vlayout)
        start = dt.now().date() - timedelta(days=7)  # Начало
        end = dt.now().date()  # Конец
        price = yf.download(company, start=start, end=end, interval="1m")['Adj Close'][-1]  # Актуальная цена
        df = price - pc
        self.label = QLabel(f'Вы просматривали эту страницу {date}', self)
        self.label2 = QLabel(f'Последняя цена {pc}', self)
        self.label3 = QLabel(f'Нынешняя цена {price}', self)
        self.label4 = QLabel(f'Разница {df}', self)
        if df < 0:
            self.label4.setStyleSheet('color: rgb(255, 0, 0);')
        elif df > 0:
            self.label4.setStyleSheet('color: rgb(0, 255, 0);')
        else:
            self.label4.setStyleSheet('color: rgb(255, 255, 255);')
        self.layout().addWidget(self.label)
        self.layout().addWidget(self.label2)
        self.layout().addWidget(self.label3)
        self.layout().addWidget(self.label4)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 720)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(369, 9, 891, 651))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setGeometry(QtCore.QRect(40, 350, 261, 291))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 259, 289))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(40, 330, 81, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.scrollArea_2 = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea_2.setGeometry(QtCore.QRect(40, 30, 261, 291))
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName("scrollArea_2")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 259, 289))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_5.addLayout(self.verticalLayout_4)
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(40, 10, 81, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.pushButton_21 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_21.setGeometry(QtCore.QRect(40, 650, 75, 23))
        self.pushButton_21.setObjectName("pushButton_21")
        self.pushButton_22 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_22.setGeometry(QtCore.QRect(140, 650, 75, 23))
        self.pushButton_22.setObjectName("pushButton_22")
        self.pushButton_23 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_23.setGeometry(QtCore.QRect(240, 650, 75, 23))
        self.pushButton_23.setObjectName("pushButton_23")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1280, 21))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.about_action = QtWidgets.QAction(MainWindow)
        self.about_action.setObjectName("about_action")
        self.menu.addAction(self.about_action)
        self.menubar.addAction(self.menu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Акции"))
        self.label.setText(_translate("MainWindow", "Компании"))
        self.label_2.setText(_translate("MainWindow", "Избраное"))
        self.pushButton_21.setText(_translate("MainWindow", "Добавить *"))
        self.pushButton_22.setText(_translate("MainWindow", "Удалить *"))
        self.pushButton_23.setText(_translate("MainWindow", "Сравнение"))
        self.menu.setTitle(_translate("MainWindow", "Помощь"))
        self.about_action.setText(_translate("MainWindow", "О программе"))


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


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())