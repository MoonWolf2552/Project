from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel


class AboutWindow(QWidget):  # Окно 'О программе'
    def __init__(self):
        super(AboutWindow, self).__init__()
        self.setWindowTitle('О программе')
        self.setLayout(QVBoxLayout(self))
        self.info = QLabel('Автор - Терентьев Илья')
        self.info2 = QLabel('Информация взята с сайта finance.yahoo.com')
        self.layout().addWidget(self.info2)
        self.layout().addWidget(self.info)
