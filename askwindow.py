from PyQt5.QtWidgets import QWidget, QGroupBox, QLineEdit, QLabel, QPushButton, QTableWidget, QListWidget, QTableWidgetItem, QHeaderView, QComboBox
from PyQt5.Qt import Qt, QGridLayout, QColor, QBrush, QListWidgetItem, QAbstractItemView, QSpacerItem, QFrame, pyqtSignal, QMessageBox
import os

from levels import levels

class AskWindow(QWidget):
    signalClose = pyqtSignal(str, int)

    def __init__(self):
        super(AskWindow, self).__init__()

        self.setWindowTitle('Добавление директории')
        self.setMinimumWidth(400)

        self.frmExists = QFrame()
        self.frmExists.setMinimumWidth(25)
        self.frmExists.setMinimumHeight(25)
        self.frmExists.setStyleSheet('background-color: #DD5555')

        self.lePath = QLineEdit()
        self.lePath.setMinimumHeight(25)
        self.cbLevel = QComboBox()

        self.cbLevel.setFocusPolicy(Qt.NoFocus)

        for c, info in levels.items():
            self.cbLevel.addItem(info['name'])
            self.cbLevel.setItemData(self.cbLevel.count() - 1, QBrush(QColor(info['color'])), Qt.BackgroundRole)

        self.cbLevel.setStyleSheet("QComboBox { background-color: " + levels[self.cbLevel.currentIndex()]['color'] + "; }")
        self.cbLevel.setMinimumHeight(25)
        self.cbLevel.currentIndexChanged.connect(self.accessLevelChanged)

        self.btnOk = QPushButton('Ок')
        self.btnCancel = QPushButton('Отмена')

        self.lePath.textChanged.connect(self.lePathTextChanged)
        self.btnOk.clicked.connect(self.btnClicked)
        self.btnCancel.clicked.connect(self.btnClicked)

        self.lytSub = QGridLayout()
        self.lytSub.addWidget(self.btnOk, 0, 0)
        self.lytSub.addWidget(self.btnCancel, 0, 1)

        self.lytMain = QGridLayout()

        self.lytMain.addWidget(self.frmExists, 0, 0)
        self.lytMain.addWidget(self.lePath, 0, 1)
        self.lytMain.addWidget(self.cbLevel, 0, 2)
        self.lytMain.addLayout(self.lytSub, 1, 0, 1, 3)

        self.setLayout(self.lytMain)

    def accessLevelChanged(self):
        self.cbLevel.setStyleSheet("QComboBox { background-color: " +
                                   levels[self.cbLevel.currentIndex()]['color'] + "; }")

    def btnClicked(self):
        if self.sender() == self.btnOk:
            if os.path.isdir(self.lePath.text()):
                self.signalClose.emit(self.lePath.text(), self.cbLevel.currentIndex())
                self.close()
            else:
                QMessageBox.warning(self, 'Ошибка пути', 'Указанный путь не является директорией', QMessageBox.Ok)
        elif self.sender() == self.btnCancel:
            self.signalClose.emit(None, 0)
            self.close()

    def lePathTextChanged(self):
        if os.path.isdir(self.lePath.text()):
            self.frmExists.setStyleSheet('background-color: #55DD77')
        else:
            self.frmExists.setStyleSheet('background-color: #DD5555')

    def closeEvent(self, event):
        self.lePath.setText('')
        self.cbLevel.setCurrentIndex(0)