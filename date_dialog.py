from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QPushButton


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
