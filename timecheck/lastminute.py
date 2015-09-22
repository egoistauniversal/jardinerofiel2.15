from PyQt4 import QtGui
from PyQt4 import QtCore

class LastTime(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        # find user home directory
        self._directory = QtCore.QDir(QtCore.QDir().home().path() + '/jf/lastminute')
        # Create directory if it doesn't exist
        if not self._directory.exists():
            QtCore.QDir().mkpath(self._directory.path())
        self._previousDate = QtCore.QDate().currentDate()
        self._file = QtCore.QFile(self._directory.path() + '/' +
                                  self._previousDate.toString('yyyy-MM-dd') + '_lastminute.txt')
        # self._file = QtCore.QFile(self._directory.path() + '/' + 'lastminute.txt')
        # self.write()

    def _update_file_name(self):
        self._file = QtCore.QFile(self._directory.path() + '/' +
                                  self._previousDate.toString('yyyy-MM-dd') + '_lastminute.txt')

    def write(self):
        _currentDate = QtCore.QDate().currentDate()
        if _currentDate.getDate() != self._previousDate.getDate():
            self._file.close()
            self._previousDate.setDate(_currentDate.year(), _currentDate.month(), _currentDate.day())
            self._update_file_name()

        if not self._file.open(QtCore.QIODevice.Append | QtCore.QFile.Text):
            QtGui.QMessageBox().warning(self, 'Fichero', 'No se puede crear el fichero %s:\n%s' %
                                        (self._file.fileName(), self._file.errorString()))
        else:
            _currentDateTime = QtCore.QDateTime().currentDateTime().toString("dd-MM-yyyy HH:mm:ss")
            _stream = QtCore.QTextStream(self._file)
            _stream << _currentDateTime + '\n'
            self._file.close()
