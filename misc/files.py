from PyQt4 import QtGui, QtCore


class Log(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        # find user home directory
        self._directory = QtCore.QDir(QtCore.QDir().home().path() + '/jf/log')
        # Create directory if it doesn't exist
        if not self._directory.exists():
            QtCore.QDir().mkpath(self._directory.path())
        self._previousDate = QtCore.QDate().currentDate()
        self._file = QtCore.QFile(self._directory.path() + '/' +
                                  self._previousDate.toString('yyyy-MM-dd') + '_log.txt')

    def write(self, output):
        _currentDate = QtCore.QDate().currentDate()
        if _currentDate.getDate() != self._previousDate.getDate():
            self._file.close()
            self._previousDate.setDate(_currentDate.year(), _currentDate.month(), _currentDate.day())
            # self._file = QtCore.QFile(self._directory.path() + '/' +
            #                           self._previousDate.toString('yyyy-MM-dd') + '_log.txt')

        if not self._file.open(QtCore.QIODevice.Append | QtCore.QFile.Text):
            QtGui.QMessageBox().warning(self, 'Fichero', 'No se puede crear el fichero %s:\n%s' %
                                        (self._file.fileName(), self._file.errorString()))
        else:
            _stream = QtCore.QTextStream(self._file)
            _stream << output + '\n'
            self._file.close()


class Standard(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        # find user home directory
        self._directory = QtCore.QDir(QtCore.QDir().home().path() + '/jf/config')
        # Create directory if it doesn't exist
        if not self._directory.exists():
            QtCore.QDir().mkpath(self._directory.path())
        self._file = QtCore.QFile(self._directory.path() + '/' + 'standard.txt')
        if not self._file.exists():
            _list = ['16', '10']
            self.write(_list)

    def read(self):
        _list = []
        if not self._file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtGui.QMessageBox().warning(self, 'Fichero', 'No se puede Abrir el fichero %s:\n%s' %
                                        (self._file.fileName(), self._file.errorString()))
        else:
            _stream = QtCore.QTextStream(self._file)
            while not _stream.atEnd():
                _line = _stream.readLine()
                _fields = _line.split('=')
                _list.append(_fields[1])
            self._file.close()
        return _list

    def write(self, l):
        if not self._file.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            QtGui.QMessageBox().warning(self, 'Fichero', 'No se puede crear el fichero %s:\n%s' %
                                        (self._file.fileName(), self._file.errorString()))
        else:
            _stream = QtCore.QTextStream(self._file)
            _stream << 'TreeViewFontSize=' + l[0] + '\n'
            _stream << 'SensorThreshold=' + l[1] + '\n'
            self._file.close()

    # -----------------------------------------------PINS---------------------------------------------


class Pins(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        # find user home directory
        self._directory = QtCore.QDir(QtCore.QDir().home().path() + '/jf/config')
        # Create directory if it doesn't exist
        if not self._directory.exists():
            QtCore.QDir().mkpath(self._directory.path())
        self._file = QtCore.QFile(self._directory.path() + '/' + 'pins.txt')
        if not self._file.exists():
            _list = ['15', '53']
            self.write(_list)

    def read(self):
        _list = []
        if not self._file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtGui.QMessageBox().warning(self, 'Fichero', 'No se puede Abrir el fichero %s:\n%s' %
                                        (self._file.fileName(), self._file.errorString()))
        else:
            _stream = QtCore.QTextStream(self._file)
            while not _stream.atEnd():
                _line = _stream.readLine()
                _fields = _line.split('=')
                _list.append(_fields[1])
            self._file.close()
        return _list

    def write(self, l):
        if not self._file.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            QtGui.QMessageBox().warning(self, 'Fichero', 'No se puede crear el fichero %s:\n%s' %
                                        (self._file.fileName(), self._file.errorString()))
        else:
            _stream = QtCore.QTextStream(self._file)
            _stream << 'AnalogPins=' + l[0] + '\n'
            _stream << 'DigitalPins=' + l[1] + '\n'
            self._file.close()

# -----------------------------------------------INTERVALS---------------------------------------------


class Intervals(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        # find user home directory
        self._directory = QtCore.QDir(QtCore.QDir().home().path() + '/jf/config')
        # Create directory if it doesn't exist
        if not self._directory.exists():
            QtCore.QDir().mkpath(self._directory.path())
        self._file = QtCore.QFile(self._directory.path() + '/' + 'intervals.txt')
        if not self._file.exists():
            _list = ['1000', '60000', '500', '200']
            self.write(_list)

    def read(self):
        _list = []
        if not self._file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtGui.QMessageBox().warning(self, 'Fichero', 'No se puede Abrir el fichero %s:\n%s' %
                                        (self._file.fileName(), self._file.errorString()))
        else:
            _stream = QtCore.QTextStream(self._file)
            while not _stream.atEnd():
                _line = _stream.readLine()
                _fields = _line.split('=')
                _list.append(_fields[1])
            self._file.close()
        return _list

    def write(self, l):
        if not self._file.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            QtGui.QMessageBox().warning(self, 'Fichero', 'No se puede crear el fichero %s:\n%s' %
                                        (self._file.fileName(), self._file.errorString()))
        else:
            _stream = QtCore.QTextStream(self._file)
            _stream << 'ComponentInterval=' + l[0] + '\n'
            _stream << 'SensorInterval=' + l[1] + '\n'
            _stream << 'SensorRequestInterval=' + l[2] + '\n'
            _stream << 'SensorGetInterval=' + l[3] + '\n'
            self._file.close()
