from PyQt4 import QtGui, QtCore
from misc import database
from misc import files


class ComponentFirstLevelItemDialog(QtGui.QDialog):
    def __init__(self, title, name='', parent=None):
        super(ComponentFirstLevelItemDialog, self).__init__(parent)
        self.setWindowTitle(title)
        self._myDataBase = database.DataBase()
        # Nice widget for editing
        self._nameLabel = QtGui.QLabel('Nombre:', self)
        self._nameLineEdit = QtGui.QLineEdit(self)
        self._previousName = name

        # OK and Cancel buttons
        self._dialogButtons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                                     QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        self._setup()

    def _setup(self):
        self._nameLineEdit.setText(self._previousName)
        self._layouts()
        self._connections()

    def _layouts(self):
        _nameLayout = QtGui.QHBoxLayout()
        _nameLayout.addWidget(self._nameLabel)
        _nameLayout.addWidget(self._nameLineEdit)

        _mainLayout = QtGui.QVBoxLayout(self)
        _mainLayout.addLayout(_nameLayout)
        _mainLayout.addWidget(self._dialogButtons)
        self.setLayout(_mainLayout)

    def _connections(self):
        self._dialogButtons.accepted.connect(self._validations)
        self._dialogButtons.rejected.connect(self.reject)

    def _validations(self):
        if self._nameLineEdit.text().isEmpty():
            QtGui.QMessageBox().warning(self, 'Falta Nombre', 'No has escrito un nombre', QtGui.QMessageBox.Ok)
            self._nameLineEdit.setFocus()
        else:
            self._nameLineEdit.setText(self._nameLineEdit.text().replace(' ', '_'))
            if self._nameLineEdit.text() == self._previousName:
                self.accept()
            else:
                if not self._myDataBase.component_group_table_name_exist(str(self._nameLineEdit.text())):
                    self.accept()
                else:
                    QtGui.QMessageBox().warning(self, 'Nombre ya existe', 'Nombre de grupo ' +
                                                self._nameLineEdit.text() + ' ya existe', QtGui.QMessageBox.Ok)

        # Get data from dialog
    def _get_name(self):
        return self._nameLineEdit.text()

    # static method to create the dialog and return (name, time, etc, accepted)
    @staticmethod
    def get_data(title, name='', parent=None):
        dialog = ComponentFirstLevelItemDialog(title, name, parent)
        result = dialog.exec_()
        _nameStr = dialog._get_name()
        return _nameStr, result == QtGui.QDialog.Accepted

    # -----------------------------------------SECOND LEVEL CLOCK-----------------------------------------------


class SecondLevelItemsClockDialog(QtGui.QDialog):
    def __init__(self, title, name='', time_on='', time_off='', pin='', parent=None):
        super(SecondLevelItemsClockDialog, self).__init__(parent)
        self.setWindowTitle(title)
        self._myDataBase = database.DataBase()

        # Nice widget for editing
        self._nameLabel = QtGui.QLabel('Nombre:', self)
        self._timeEditOnLabel = QtGui.QLabel('Encendido:', self)
        self._timeEditOffLabel = QtGui.QLabel('Apagado:', self)
        self._pinLabel = QtGui.QLabel('Pin:', self)

        self._nameLineEdit = QtGui.QLineEdit(self)
        self._timeEditOn = QtGui.QTimeEdit(self)
        self._timeEditOff = QtGui.QTimeEdit(self)
        self._pinComboBox = QtGui.QComboBox(self)

        self._previousName = name

        # OK and Cancel buttons
        self._dialogButtons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                                     QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        self._setup(name, time_on, time_off, pin)

    def _setup(self, name, time_on, time_off, pin):
        self._timeEditOn.setDisplayFormat('HH:mm:ss')
        self._timeEditOff.setDisplayFormat('HH:mm:ss')

        self._setup_pin_combo_box(pin)

        if not QtCore.QString(name).isEmpty():
            self._nameLineEdit.setText(name)
            time = QtCore.QTime(int(time_on.mid(0, 2)), int(time_on.mid(3, 2)), int(time_on.mid(6, 2)))
            self._timeEditOn.setTime(time)
            time = QtCore.QTime(int(time_off.mid(0, 2)), int(time_off.mid(3, 2)), int(time_off.mid(6, 2)))
            self._timeEditOff.setTime(time)
            self._pinComboBox.setCurrentIndex(self._pinComboBox.findText(pin))

        self._layouts()
        self._connections()

    def _setup_pin_combo_box(self, pin):
        _file = files.Pins()
        _list = _file.read()
        # _analogPinsRange = int(_list[0])
        _digitalPinsRange = int(_list[1])

        for x in xrange(_digitalPinsRange):
            self._pinComboBox.addItem(str(x))

        _db = database.DataBase()
        _pinList = _db.get_pin_list()

        for item in _pinList:
            if item != pin:
                # Get the index of the value to disable
                index = self._pinComboBox.model().index(self._pinComboBox.findText(item), 0)
                # This is the effective 'disable' flag
                v = QtCore.QVariant(0)
                # The Magic
                self._pinComboBox.model().setData(index, v, QtCore.Qt.UserRole - 1)

        for x in xrange(_digitalPinsRange):
            try:
                _pinList.index(str(x))
            except ValueError:
                self._pinComboBox.setCurrentIndex(x)
                break

    def _layouts(self):
        _nameLayout = QtGui.QHBoxLayout()
        _nameLayout.addWidget(self._nameLabel)
        _nameLayout.addWidget(self._nameLineEdit)

        _timeEditOnLayout = QtGui.QHBoxLayout()
        _timeEditOnLayout.addWidget(self._timeEditOnLabel)
        _timeEditOnLayout.addWidget(self._timeEditOn)

        _timeEditOffLayout = QtGui.QHBoxLayout()
        _timeEditOffLayout.addWidget(self._timeEditOffLabel)
        _timeEditOffLayout.addWidget(self._timeEditOff)

        _pinLayout = QtGui.QHBoxLayout()
        _pinLayout.addWidget(self._pinLabel)
        _pinLayout.addWidget(self._pinComboBox)

        _mainLayout = QtGui.QVBoxLayout(self)
        _mainLayout.addLayout(_nameLayout)
        _mainLayout.addLayout(_timeEditOnLayout)
        _mainLayout.addLayout(_timeEditOffLayout)
        _mainLayout.addLayout(_pinLayout)
        _mainLayout.addWidget(self._dialogButtons)
        self.setLayout(_mainLayout)

    def _connections(self):
        self._dialogButtons.accepted.connect(self._validations)
        self._dialogButtons.rejected.connect(self.reject)

    def _validations(self):
        _validationIsOk = False
        if not self._nameLineEdit.text().isEmpty():
            self._nameLineEdit.setText(self._nameLineEdit.text().replace(' ', '_'))
            if self._timeEditOn.time() != self._timeEditOff.time():
                if self._nameLineEdit.text() == self._previousName:
                    _validationIsOk = True
                else:
                    if not self._myDataBase.component_table_name_exist(str(self._nameLineEdit.text())):
                        _validationIsOk = True
                    else:
                        QtGui.QMessageBox().warning(self, 'Nombre ya existe', 'Nombre de componente ' +
                                                    self._nameLineEdit.text() + ' ya existe', QtGui.QMessageBox.Ok)
            else:
                QtGui.QMessageBox().warning(self, 'Tiempo Erroneo', 'La hora de encendido y apagado es el mismo',
                                            QtGui.QMessageBox.Ok)
                self._timeEditOn.setFocus()
        else:
            QtGui.QMessageBox().warning(self, 'Falta Nombre', 'No has escrito un nombre', QtGui.QMessageBox.Ok)
            self._nameLineEdit.setFocus()
        if _validationIsOk:
            self.accept()

    # Get data from dialog
    def _get_name(self):
        return self._nameLineEdit.text()

    @staticmethod
    def _get_time_type():
        return '1'

    def _get_time_on(self):
        _myTime = self._timeEditOn.time()
        return _myTime.toString("HH:mm:ss")

    def _get_time_off(self):
        _myTime = self._timeEditOff.time()
        return _myTime.toString("HH:mm:ss")

    def _get_pin(self):
        return self._pinComboBox.itemText(self._pinComboBox.currentIndex())

    # static method to create the dialog and return (name, time, etc, accepted)
    @staticmethod
    def get_data(title, name='', time_on='', time_off='', pin='', parent=None):
        dialog = SecondLevelItemsClockDialog(title, name, time_on, time_off, pin, parent)
        result = dialog.exec_()
        _nameStr = dialog._get_name()
        _timeTypeStr = dialog._get_time_type()
        _dateTimeOnStr = dialog._get_time_on()
        _dateTimeOffStr = dialog._get_time_off()
        _pinStr = dialog._get_pin()
        return _nameStr, _timeTypeStr, _dateTimeOnStr, _dateTimeOffStr, _pinStr, result == QtGui.QDialog.Accepted

    # -----------------------------------------SECOND LEVEL TIMER-----------------------------------------------


class SecondLevelItemsTimerDialog(QtGui.QDialog):
    def __init__(self, title, name='', time_on='', time_off='', pin='', parent=None):
        super(SecondLevelItemsTimerDialog, self).__init__(parent)
        self.setWindowTitle(title)
        self._myDataBase = database.DataBase()

        # Nice widget for editing
        self._nameLabel = QtGui.QLabel('Nombre:', self)
        self._timeEditOnLabel = QtGui.QLabel('Encendido:', self)
        self._timeEditOffLabel = QtGui.QLabel('Apagado:', self)
        self._pinLabel = QtGui.QLabel('Pin:', self)

        self._nameLineEdit = QtGui.QLineEdit(self)
        self._timeEditOn = QtGui.QTimeEdit(self)
        self._timeEditOff = QtGui.QTimeEdit(self)
        self._pinComboBox = QtGui.QComboBox(self)

        self._previousName = name

        # OK and Cancel buttons
        self._dialogButtons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                                     QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        self._setup(name, time_on, time_off, pin)

    def _setup(self, name, time_on, time_off, pin):
        self._timeEditOn.setDisplayFormat('HH:mm:ss')
        self._timeEditOff.setDisplayFormat('HH:mm:ss')
        self._setup_pin_combo_box(pin)

        if not QtCore.QString(name).isEmpty():
            self._nameLineEdit.setText(name)
            time = QtCore.QTime(int(time_on.mid(0, 2)), int(time_on.mid(3, 2)), int(time_on.mid(6, 2)))
            self._timeEditOn.setTime(time)
            time = QtCore.QTime(int(time_off.mid(0, 2)), int(time_off.mid(3, 2)), int(time_off.mid(6, 2)))
            self._timeEditOff.setTime(time)
            self._pinComboBox.setCurrentIndex(self._pinComboBox.findText(pin))

        self._layouts()
        self._connections()

    def _setup_pin_combo_box(self, pin):
        _file = files.Pins()
        _list = _file.read()
        # _analogPinsRange = int(_list[0])
        _digitalPinsRange = int(_list[1])

        for x in xrange(_digitalPinsRange):
            self._pinComboBox.addItem(str(x))

        _db = database.DataBase()
        _pinList = _db.get_pin_list()

        for item in _pinList:
            if item != pin:
                # Get the index of the value to disable
                index = self._pinComboBox.model().index(self._pinComboBox.findText(item), 0)
                # This is the effective 'disable' flag
                v = QtCore.QVariant(0)
                # The Magic
                self._pinComboBox.model().setData(index, v, QtCore.Qt.UserRole - 1)

        for x in xrange(_digitalPinsRange):
            try:
                _pinList.index(str(x))
            except ValueError:
                self._pinComboBox.setCurrentIndex(x)
                break

    def _layouts(self):
        _nameLayout = QtGui.QHBoxLayout()
        _nameLayout.addWidget(self._nameLabel)
        _nameLayout.addWidget(self._nameLineEdit)

        _timeEditOnLayout = QtGui.QHBoxLayout()
        _timeEditOnLayout.addWidget(self._timeEditOnLabel)
        _timeEditOnLayout.addWidget(self._timeEditOn)

        _timeEditOffLayout = QtGui.QHBoxLayout()
        _timeEditOffLayout.addWidget(self._timeEditOffLabel)
        _timeEditOffLayout.addWidget(self._timeEditOff)

        _pinLayout = QtGui.QHBoxLayout()
        _pinLayout.addWidget(self._pinLabel)
        _pinLayout.addWidget(self._pinComboBox)

        _mainLayout = QtGui.QVBoxLayout(self)
        _mainLayout.addLayout(_nameLayout)
        _mainLayout.addLayout(_timeEditOnLayout)
        _mainLayout.addLayout(_timeEditOffLayout)
        _mainLayout.addLayout(_pinLayout)
        _mainLayout.addWidget(self._dialogButtons)
        self.setLayout(_mainLayout)

    def _connections(self):
        self._dialogButtons.accepted.connect(self._validations)
        self._dialogButtons.rejected.connect(self.reject)

    def _validations(self):
        _validationIsOk = False
        if not self._nameLineEdit.text().isEmpty():
            self._nameLineEdit.setText(self._nameLineEdit.text().replace(' ', '_'))
            _zeroTime = QtCore.QTime()
            _zeroTime.setHMS(0, 0, 0)
            _zeroTimeStr = _zeroTime.toString()
            _timeEditOnStr = self._timeEditOn.time().toString("HH:mm:ss")
            _timeEditOffStr = self._timeEditOff.time().toString("HH:mm:ss")
            if _timeEditOnStr != _zeroTimeStr and _timeEditOffStr != _zeroTimeStr:
                if self._nameLineEdit.text() == self._previousName:
                    _validationIsOk = True
                else:
                    if not self._myDataBase.component_table_name_exist(str(self._nameLineEdit.text())):
                        _validationIsOk = True
                    else:
                        QtGui.QMessageBox().warning(self, 'Nombre ya existe', 'Nombre de componente ' +
                                                    self._nameLineEdit.text() + ' ya existe', QtGui.QMessageBox.Ok)
            else:
                QtGui.QMessageBox().warning(self, 'Tiempo Erroneo', 'No puede haber un tiempo de encendido o '
                                                                    'apagado de 00:00:00', QtGui.QMessageBox.Ok)
                self._timeEditOn.setFocus()
        else:
            QtGui.QMessageBox().warning(self, 'Falta Nombre', 'No has escrito un nombre', QtGui.QMessageBox.Ok)
            self._nameLineEdit.setFocus()
        if _validationIsOk:
            self.accept()

    # Get data from dialog
    def _get_name(self):
        return self._nameLineEdit.text()

    @staticmethod
    def _get_time_type():
        return '2'

    def _get_time_on(self):
        return self._timeEditOn.time()

    def _get_time_off(self):
        return self._timeEditOff.time()

    def _get_pin(self):
        return self._pinComboBox.itemText(self._pinComboBox.currentIndex())

    # static method to create the dialog and return (name, time, etc, accepted)
    @staticmethod
    def get_data(title, name='', time_on='', time_off='', pin='', parent=None):
        dialog = SecondLevelItemsTimerDialog(title, name, time_on, time_off, pin, parent)
        result = dialog.exec_()
        _nameStr = dialog._get_name()
        _timeTypeStr = dialog._get_time_type()
        _timeOn = dialog._get_time_on()
        _timeOff = dialog._get_time_off()

        _timeOnStr = _timeOn.toString("HH:mm:ss")
        _timeOffStr = _timeOff.toString("HH:mm:ss")

        _pinStr = dialog._get_pin()

        return _nameStr, _timeTypeStr, _timeOnStr, _timeOffStr, _pinStr, result == QtGui.QDialog.Accepted