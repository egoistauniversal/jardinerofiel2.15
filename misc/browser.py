from PyQt4 import QtGui, QtCore
from misc.files import Log


class Browser(QtGui.QWidget):
    def __init__(self):
        super(Browser, self).__init__()
        self._browser = QtGui.QTextBrowser()
        self._palette = QtGui.QPalette()
        self._backgroundColor = QtGui.QColor(43, 43, 43)
        self._myLogFile = Log()
        self._linesCounter = 0
        self._linesNumberMax = 500
        self._setup()

    def _setup(self):
        self._setup_browser()
        self._setup_layout()
        self._connections()

    def _setup_browser(self):
        self._palette.setColor(QtGui.QPalette.Base, self._backgroundColor)
        self._browser.setPalette(self._palette)

    def _setup_layout(self):
        _mainLayout = QtGui.QVBoxLayout()
        _mainLayout.addWidget(self._browser)
        self.setLayout(_mainLayout)
        self.show()

    def _connections(self):
        pass

    def print_normal_message(self, text):
        _myDateTime = QtCore.QDateTime().currentDateTime()
        if self._linesCounter == self._linesNumberMax:
            self.clear()
            self._linesCounter = 0

        output = '[' + _myDateTime.toString("dd-MM-yyyy HH:mm:ss") + '] ' + text
        self._browser.append('<font color="#A9B7C6">' + output + '</font>')
        self._linesCounter += 1
        self._myLogFile.write(output)

    def print_alert_message(self, text):
        _myDateTime = QtCore.QDateTime().currentDateTime()

        output = '[' + _myDateTime.toString("dd-MM-yyyy HH:mm:ss") + '] ' + text
        self._browser.append('<font color="#C55450">' + output + '</font>')
        self._linesCounter += 1
        self._myLogFile.write(output)

    def clear(self):
        self._browser.clear()