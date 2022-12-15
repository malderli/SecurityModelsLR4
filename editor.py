from PyQt5.QtWidgets import QWidget, QGroupBox, QLineEdit, QLabel, QPushButton, QTableWidget, QListWidget, QTableWidgetItem, QHeaderView, QComboBox
from PyQt5.Qt import Qt, QGridLayout, QColor, QBrush, QListWidgetItem, QAbstractItemView, QMessageBox
import os
import json
import re

from levels import levels, DEFAULT_LEVEL
from askwindow import AskWindow

class Editor(QWidget):
    def __init__(self):
        super(Editor, self).__init__()

        self.permissions = None # {}

        self.setWindowTitle('МБКС ЛР4 | Лазарев Михайлин')
        self.setMinimumWidth(800)

        self.asker = AskWindow()
        self.asker.signalClose.connect(self.addFolder)

        # +++++++++++++++++++++++++++ Folders +++++++++++++++++++++++++++

        self.gbPaths = QGroupBox('Пути')
        self.layoutPaths = QGridLayout()
        self.lePermissionsFilePath = QLineEdit('permissions.json')

        self.layoutPaths.addWidget(QLabel('Файл уровней доступа: '), 1, 0)
        self.layoutPaths.addWidget(self.lePermissionsFilePath, 1, 1)

        self.gbPaths.setLayout(self.layoutPaths)

        # ++++++++++++++=++++++++++++++++++++++++++++++++++++++++++++++++

        # ^^^^^^^^^^^^^^^^^^^^^^^^^^ Permissions ^^^^^^^^^^^^^^^^^^^^^^^^

        self.gbPermissionsView = QGroupBox('Уровни доступа')
        self.lytPermissions = QGridLayout()

        self.twPermissions = QTableWidget()
        self.twPermissions.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.btnAddFolder = QPushButton('+')
        self.btnRemFolder = QPushButton('-')

        self.lytPermissions.addWidget(self.twPermissions, 0, 0, 1, 2)
        self.lytPermissions.addWidget(self.btnAddFolder, 1, 0)
        self.lytPermissions.addWidget(self.btnRemFolder, 1, 1)

        self.gbPermissionsView.setLayout(self.lytPermissions)

        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        # **************************** Files ***************************

        self.gbFiles = QGroupBox('Файлы')
        self.lytFiles = QGridLayout()

        self.leFolder1Path = QLineEdit()
        self.lwFolder1 = QListWidget()
        self.lblFolder1AccessLvl = QLabel(' Unclassified ')
        self.lblFolder1AccessLvl.setStyleSheet("QLabel { background-color : #AAD7E9; }")

        self.leFolder2Path = QLineEdit()
        self.lwFolder2 = QListWidget()
        self.lblFolder2AccessLvl = QLabel(' Unclassified ')
        self.lblFolder2AccessLvl.setMinimumHeight(20)
        self.lblFolder2AccessLvl.setStyleSheet("QLabel { background-color : #AAD7E9; }")

        self.btnMoveLeft = QPushButton('<<')
        self.btnMoveRight = QPushButton('>>')

        self.lytFiles.addWidget(self.btnMoveRight, 1, 2)
        self.lytFiles.addWidget(self.btnMoveLeft, 2, 2)

        self.lytFiles.addWidget(self.leFolder1Path, 0, 0)
        self.lytFiles.addWidget(self.lblFolder1AccessLvl, 0, 1)
        self.lytFiles.addWidget(self.lwFolder1, 1, 0, 3, 2)

        self.lytFiles.addWidget(self.leFolder2Path, 0, 3)
        self.lytFiles.addWidget(self.lblFolder2AccessLvl, 0, 4)
        self.lytFiles.addWidget(self.lwFolder2, 1, 3, 3, 3)


        self.gbFiles.setLayout(self.lytFiles)

        # **************************************************************

        self.lePermissionsFilePath.textChanged.connect(self.leFilePathTextChanged)
        self.leFolder1Path.textChanged.connect(self.leFolderPathTextChanged)
        self.leFolder2Path.textChanged.connect(self.leFolderPathTextChanged)
        self.lwFolder1.doubleClicked.connect(self.lwFolderDoubleClicked)
        self.lwFolder2.doubleClicked.connect(self.lwFolderDoubleClicked)
        self.btnAddFolder.clicked.connect(self.btnAddFolderClicked)
        self.btnRemFolder.clicked.connect(self.btnRemFolderClicked)
        self.btnMoveRight.clicked.connect(self.btnMoveClicked)
        self.btnMoveLeft.clicked.connect(self.btnMoveClicked)

        self.loadPermissions()

        self.layoutMain = QGridLayout()
        self.layoutMain.addWidget(self.gbPaths, 0, 0)
        self.layoutMain.addWidget(self.gbPermissionsView, 1, 0)
        self.layoutMain.addWidget(self.gbFiles, 2, 0)

        self.setLayout(self.layoutMain)

    def loadPermissions(self, from_file = True):
        self.twPermissions.clear()
        self.twPermissions.setRowCount(0)
        self.twPermissions.setColumnCount(2)

        self.twPermissions.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.twPermissions.setHorizontalHeaderLabels(['Путь', 'Уровень'])

        if from_file:
            self.permissions = {}

            try:
                if os.path.isfile(self.lePermissionsFilePath.text()):
                    with open(self.lePermissionsFilePath.text(), "r") as fs:
                        permissions = json.loads(fs.read())

                        self.permissions = permissions
            except:
                return

        for path, level in self.permissions.items():
            self.twPermissions.setRowCount(self.twPermissions.rowCount() + 1)
            self.twPermissions.setItem(self.twPermissions.rowCount() - 1, 0, QTableWidgetItem(path))
            self.twPermissions.setItem(self.twPermissions.rowCount() - 1, 1, QTableWidgetItem(str(level)))

            cbLevel = QComboBox()
            cbLevel.setFocusPolicy(Qt.NoFocus)

            for c, info in levels.items():
                cbLevel.addItem(info['name'])
                cbLevel.setItemData(cbLevel.count() - 1, QBrush(QColor(info['color'])), Qt.BackgroundRole)

            cbLevel.setStyleSheet("QComboBox { background-color: " + levels[level]['color'] + "; }")
            cbLevel.setCurrentText(levels[level]['name'])
            cbLevel.currentIndexChanged.connect(self.accessLevelChanged)

            self.twPermissions.setCellWidget(self.twPermissions.rowCount() - 1, 1, cbLevel)

        self.twPermissions.resizeColumnsToContents()

        self.updateLevelLabels()

        # Force resize
        self.twPermissions.setMinimumWidth(self.twPermissions.width() + 1)
        self.twPermissions.setMinimumWidth(0)

    def savePermissions(self):
        with open(self.lePermissionsFilePath.text(), "w") as fs:
            json.dump(self.permissions, fs)

    def btnAddFolderClicked(self):
        self.asker.show()

    def addFolder(self, path, level):
        if path in self.permissions:
            QMessageBox.warning(self, 'Ошибка пути', 'Указанный путь уже добавлен к рассмотрению', QMessageBox.Ok)
        else:
            self.permissions[path] = level
            self.loadPermissions(False)
            self.savePermissions()
            self.leFolder1Path.setText(self.leFolder1Path.text())
            self.leFolderPathTextChanged('Left')
            self.leFolderPathTextChanged('Right')

    def btnRemFolderClicked(self):
        index = self.twPermissions.currentRow()

        if (index >= 0) and (self.twPermissions.item(index, 0).isSelected()):
            self.permissions.pop(self.twPermissions.item(index, 0).text())
            self.twPermissions.removeRow(index)
            self.savePermissions()
            self.leFolderPathTextChanged('Left')
            self.leFolderPathTextChanged('Right')
        else:
            QMessageBox.warning(self, 'Ошибка удаления', 'Не выбрана директория для удаления из рассмотрения',
                                QMessageBox.Ok)

    def btnMoveClicked(self):
        if self.sender() == self.btnMoveRight:
            if not self.lwFolder1.currentRow() >= 0:
                QMessageBox.warning(self, 'Ошибка файла', 'Не выбран файл для переноса', QMessageBox.Ok)
                return

            file = self.lwFolder1.currentItem().text()
            source = self.leFolder1Path.text()
            dest = self.leFolder2Path.text()
        elif self.sender() == self.btnMoveLeft:
            if not self.lwFolder2.currentRow() >= 0:
                QMessageBox.warning(self, 'Ошибка файла', 'Не выбран файл для переноса', QMessageBox.Ok)
                return

            file = self.lwFolder2.currentItem().text()
            source = self.leFolder2Path.text()
            dest = self.leFolder1Path.text()
        else:
            return

        if not os.path.isdir(dest):
            return

        start = os.path.join(source, file)
        finish = os.path.join(dest, file)

        if not os.path.exists(start):
            return

        if os.path.isdir(start):
            QMessageBox.warning(self, 'Ошибка файла', 'Для переноса доступны только файлы', QMessageBox.Ok)
            return

        if os.path.exists(finish):
            QMessageBox.warning(self, 'Ошибка файла', 'Файл со схожим названием уже существует в директории назначения',
                                QMessageBox.Ok)
            return

        if source in self.permissions:
            source_level = self.permissions[source]
        else:
            source_level = DEFAULT_LEVEL

        if dest in self.permissions:
            dest_level = self.permissions[dest]
        else:
            dest_level = DEFAULT_LEVEL

        if source_level < dest_level:
            QMessageBox.warning(self, 'Ошибка доступа', 'Перенос в директорию с меньшим классом секретности не '
                                                        'доступен', QMessageBox.Ok)
            return

        os.rename(start, finish)

        self.leFolderPathTextChanged('Left')
        self.leFolderPathTextChanged('Right')

    def accessLevelChanged(self, index):
        for row in range(self.twPermissions.rowCount()):
            if self.sender() == self.twPermissions.cellWidget(row, 1):
                self.twPermissions.cellWidget(row, 1).setStyleSheet("QComboBox { background-color: "
                                                                    + levels[index]['color'] + "; }")

                self.permissions[self.twPermissions.item(row, 0).text()] = index
                self.savePermissions()
                self.loadPermissions()
                self.updateLevelLabels()
                self.leFolderPathTextChanged('Left')
                self.leFolderPathTextChanged('Right')
                break

    def updateLevelLabels(self):
        if self.leFolder1Path.text() in self.permissions:
            self.lblFolder1AccessLvl.setText(levels[self.permissions[self.leFolder1Path.text()]]['name'])
            self.lblFolder1AccessLvl.setStyleSheet("QLabel { background-color : " +
                                                   levels[self.permissions[self.leFolder1Path.text()]]['color']
                                                   + "; }")
        else:
            self.lblFolder1AccessLvl.setText(' Unclassified ')
            self.lblFolder1AccessLvl.setStyleSheet("QLabel { background-color : #AAD7E9; }")

        if self.leFolder2Path.text() in self.permissions:
            self.lblFolder2AccessLvl.setText(levels[self.permissions[self.leFolder2Path.text()]]['name'])
            self.lblFolder2AccessLvl.setStyleSheet("QLabel { background-color : " +
                                                   levels[self.permissions[self.leFolder2Path.text()]]['color']
                                                   + "; }")
        else:
            self.lblFolder2AccessLvl.setText(' Unclassified ')
            self.lblFolder2AccessLvl.setStyleSheet("QLabel { background-color : #AAD7E9; }")

    def getFolderContent(self, path):
        content = []
        colors = []

        try:
            rawcontent = os.listdir(path)

            content.append('[ .. ]')
            colors.append('#DDDDDD')

            folderscount = 0

            for index, elm in enumerate(rawcontent):
                curr = os.path.join(path, elm)

                if os.path.isdir(curr):
                    folderscount += 1
                    content.insert(folderscount, elm)

                    if curr in self.permissions:
                        colors.insert(folderscount, levels[self.permissions[curr]]['color'])
                    else:
                        colors.insert(folderscount, '#EEEEEE')

                else:
                    content.append(elm)
                    colors.append('#FFFFFF')
        except:
            pass

        return content, colors

    def leFolderPathTextChanged(self, force = None):
        if (force == 'Left') or (self.sender() == self.leFolder1Path):
            currentLE = self.leFolder1Path
            currentLW = self.lwFolder1
        elif (force == 'Right') or (self.sender() == self.leFolder2Path):
            currentLE = self.leFolder2Path
            currentLW = self.lwFolder2
        else:
            return

        self.updateLevelLabels()

        content, colors = self.getFolderContent(currentLE.text())

        currentLW.clear()

        for i in range(len(content)):
            item = QListWidgetItem(content[i])
            item.setBackground(QColor(colors[i]))

            currentLW.addItem(item)

    def leFilePathTextChanged(self):
        self.loadPermissions()

    def lwFolderDoubleClicked(self, index):
        row = index.row()

        currentLW = self.lwFolder1 if self.sender() == self.lwFolder1 else self.lwFolder2
        currentLE = self.leFolder1Path if self.sender() == self.lwFolder1 else self.leFolder2Path

        currentLW.item(0).background().color().getRgb()

        if row == 0:
            currentLE.setText(os.path.dirname(currentLE.text()))
        elif not currentLW.item(row).background().color().getRgb() == (255, 255, 255, 255):
            currentLE.setText(os.path.join(currentLE.text(), currentLW.item(row).text()))
