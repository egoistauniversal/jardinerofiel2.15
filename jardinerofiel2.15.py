from PyQt4 import QtGui
import sys
import mainWindow


def jardinerofiel():
    app = QtGui.QApplication(sys.argv)
    _myMainWindow = mainWindow.MainWindow()
    _myMainWindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    jardinerofiel()