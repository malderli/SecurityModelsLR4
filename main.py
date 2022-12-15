import sys
from PyQt5.Qt import QApplication

from editor import Editor
from askwindow import AskWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    edt = Editor()

    edt.show()

    sys.exit(app.exec_())