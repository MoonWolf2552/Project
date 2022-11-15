from datetime import datetime as dt, timedelta
from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QWidget
import yfinance as yf


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
