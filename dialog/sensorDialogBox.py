from PyQt4 import QtGui, QtCore
from misc import database
from misc import files


class SensorFirstLevelItemDialog(QtGui.QDialog):
    def __init__(self, title, name='', parent=None):
        super(SensorFirstLevelItemDialog, self).__init__(parent)
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
                if not self._myDataBase.sensor_group_table_name_exist(str(self._nameLineEdit.text())):
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
        dialog = SensorFirstLevelItemDialog(title, name, parent)
        result = dialog.exec_()
        _nameStr = dialog._get_name()
        return _nameStr, result == QtGui.QDialog.Accepted

    # -------------------------------------SENSOR---------------------------------------------


class SecondLevelItemSensorDialog(QtGui.QDialog):
    def __init__(self, title, name='', pin='', parent=None):
        super(SecondLevelItemSensorDialog, self).__init__(parent)
        self.setWindowTitle(title)
        self._myDataBase = database.DataBase()
        self._nameLabel = QtGui.QLabel('Nombre:', self)
        self._pinLabel = QtGui.QLabel('Pin:', self)
        self._nameLineEdit = QtGui.QLineEdit(self)
        self._pinComboBox = QtGui.QComboBox(self)

        self._previousName = name

        # OK and Cancel buttons
        self._dialogButtons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                                     QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        self._setup(name, pin)

    def _setup(self, name, pin):
        self._setup_pin_combo_box(pin)
        if not QtCore.QString(name).isEmpty():
            self._nameLineEdit.setText(name)
            self._pinComboBox.setCurrentIndex(self._pinComboBox.findText(pin))
        self._layouts()
        self._connections()

    def _setup_pin_combo_box(self, pin):
        _file = files.Pins()
        _list = _file.read()
        _analogPinsRange = int(_list[0])
        _digitalPinsRange = int(_list[1])

        for x in xrange(_analogPinsRange):
            self._pinComboBox.addItem('A' + str(x))

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

        # Return the index in the list of the first item whose value is x. It is an error if there is no such item.
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

        _pinLayout = QtGui.QHBoxLayout()
        _pinLayout.addWidget(self._pinLabel)
        _pinLayout.addWidget(self._pinComboBox)

        _mainLayout = QtGui.QVBoxLayout(self)
        _mainLayout.addLayout(_nameLayout)
        _mainLayout.addLayout(_pinLayout)
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
                if not self._myDataBase.sensor_table_name_exist(str(self._nameLineEdit.text())):
                    self.accept()
                else:
                    QtGui.QMessageBox().warning(self, 'Nombre ya existe', 'Nombre de sensor ' +
                                                self._nameLineEdit.text() + ' ya existe', QtGui.QMessageBox.Ok)

    # Get data from dialog
    def _get_name(self):
        return self._nameLineEdit.text()

    def _get_pin(self):
        return self._pinComboBox.itemText(self._pinComboBox.currentIndex())

    # static method to create the dialog and return (name, time, etc, accepted)
    @staticmethod
    def get_data(title, name='', pin='', parent=None):
        _dialog = SecondLevelItemSensorDialog(title, name, pin, parent)
        _result = _dialog.exec_()
        _nameStr = _dialog._get_name()
        _pinStr = _dialog._get_pin()
        return _nameStr, _pinStr, _result == QtGui.QDialog.Accepted
