from PyQt4 import QtGui, QtCore
from misc import custom, database, files


class FirstLevelItemDialog(QtGui.QDialog):
    def __init__(self, title, name='', parent=None):
        super(FirstLevelItemDialog, self).__init__(parent)
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
                if not self._myDataBase.control_group_table_name_exist(str(self._nameLineEdit.text())):
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
        dialog = FirstLevelItemDialog(title, name, parent)
        result = dialog.exec_()
        _nameStr = dialog._get_name()
        return _nameStr, result == QtGui.QDialog.Accepted

    # -------------------------------------SECOND LEVEL SENSOR---------------------------------------------


class SecondLevelItemSensorDialog(QtGui.QDialog):
    def __init__(self, title, sensor_name='', sensor_type='', operator='', goal_value='', device_name='', pause='',
                 protocol='', pin='', parent=None):
        super(SecondLevelItemSensorDialog, self).__init__(parent)
        self.setWindowTitle(title)
        self._myDataBase = database.DataBase()

        # Nice widget for editing
        self._sensorNameLabel = QtGui.QLabel('Sensor:', self)
        self._operatorLabel = QtGui.QLabel('Operador:', self)
        self._goalValueLabel = QtGui.QLabel('Valor Limite:', self)
        self._deviceNameLabel = QtGui.QLabel('Dispositivo:', self)
        self._pauseLabel = QtGui.QLabel('Pausa:', self)
        self._protocolLabel = QtGui.QLabel('Protocolo:', self)
        self._pinLabel = QtGui.QLabel('Pin:', self)

        self._sensorNameComboBox = QtGui.QComboBox(self)
        self._operatorComboBox = QtGui.QComboBox(self)
        self._goalValueDoubleSpinBox = QtGui.QDoubleSpinBox(self)
        self._deviceNameLineEdit = QtGui.QLineEdit(self)
        self._pauseTimeEdit = QtGui.QTimeEdit(self)
        self._protocolComboBox = QtGui.QComboBox(self)
        self._pinComboBox = QtGui.QComboBox(self)

        # OK and Cancel buttons
        self._dialogButtons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                                     QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        self._setup(sensor_name, sensor_type, operator, goal_value, device_name, pause, protocol, pin)

    def _setup(self, sensor_name, sensor_type, operator, goal_value, device_name, pause, protocol, pin):
        self.setGeometry(500, 200, 300, 400)
        self._setup_layouts()
        self._setup_sensor_name_combobox(sensor_name, sensor_type)
        self._setup_operator_combobox(operator)
        self._setup_goal_value_spinbox(goal_value)
        self._deviceNameLineEdit.setText(device_name)
        self._setup_pause_time_edit(pause)
        self._setup_protocol_combobox(protocol)
        self._setup_pin_combobox(pin)
        self._setup_connections()

    def _setup_layouts(self):
        _nameLayout = QtGui.QHBoxLayout()
        _nameLayout.addWidget(self._sensorNameLabel)
        _nameLayout.addWidget(self._sensorNameComboBox)

        _operatorLayout = QtGui.QHBoxLayout()
        _operatorLayout.addWidget(self._operatorLabel)
        _operatorLayout.addWidget(self._operatorComboBox)

        _goalValueLayout = QtGui.QHBoxLayout()
        _goalValueLayout.addWidget(self._goalValueLabel)
        _goalValueLayout.addWidget(self._goalValueDoubleSpinBox)

        _deviceNameLayout = QtGui.QHBoxLayout()
        _deviceNameLayout.addWidget(self._deviceNameLabel)
        _deviceNameLayout.addWidget(self._deviceNameLineEdit)

        _pauseLayout = QtGui.QHBoxLayout()
        _pauseLayout.addWidget(self._pauseLabel)
        _pauseLayout.addWidget(self._pauseTimeEdit)

        _protocolLayout = QtGui.QHBoxLayout()
        _protocolLayout.addWidget(self._protocolLabel)
        _protocolLayout.addWidget(self._protocolComboBox)

        _pinLayout = QtGui.QHBoxLayout()
        _pinLayout.addWidget(self._pinLabel)
        _pinLayout.addWidget(self._pinComboBox)

        _mainLayout = QtGui.QVBoxLayout(self)
        _mainLayout.addLayout(_nameLayout)
        _mainLayout.addLayout(_operatorLayout)
        _mainLayout.addLayout(_goalValueLayout)
        _mainLayout.addLayout(_deviceNameLayout)
        _mainLayout.addLayout(_pauseLayout)
        _mainLayout.addLayout(_protocolLayout)
        _mainLayout.addLayout(_pinLayout)
        _mainLayout.addWidget(self._dialogButtons)

        self.setLayout(_mainLayout)

    def _setup_sensor_name_combobox(self, s_name, s_type):
        _custom = custom.Icons()
        _nameList = self._myDataBase.sensor_table_select_sensor_names()
        for _tuple in _nameList:
            self._sensorNameComboBox.addItem(_custom.get_sensor_icon(_tuple[1]), _tuple[0], _tuple[1])
        if s_name:
            _count = self._sensorNameComboBox.count()
            for i in xrange(_count):
                _text = self._sensorNameComboBox.itemText(i)
                _data = self._sensorNameComboBox.itemData(i).toString()
                if s_name == _text and s_type == _data:
                    self._sensorNameComboBox.setCurrentIndex(i)
                    break

    def _setup_operator_combobox(self, operator):
        self._operatorComboBox.addItems(['>', '>=', '<', '<='])
        if operator:
            self._operatorComboBox.setCurrentIndex(self._operatorComboBox.findText(operator))

    def _setup_goal_value_spinbox(self, value):
        _sensorType = self._sensorNameComboBox.itemData(self._sensorNameComboBox.currentIndex()).toString()
        self._set_goal_value_spinbox_suffix(_sensorType)
        self._set_goal_value_spinbox_range(_sensorType)
        if value:
            self._goalValueDoubleSpinBox.setValue(float(value))

    def _setup_pause_time_edit(self, pause):
        self._pauseTimeEdit.setDisplayFormat('HH:mm:ss')
        if pause:
            self._pauseTimeEdit.setTime(QtCore.QTime(int(pause.mid(0, 2)), int(pause.mid(3, 2)),
                                                     int(pause.mid(6, 2))))

    def _setup_protocol_combobox(self, protocol):
        self._protocolComboBox.addItems(['1', '2', '3'])
        if protocol:
            self._protocolComboBox.setCurrentIndex(self._protocolComboBox.findText(protocol))

    def _setup_pin_combobox(self, pin):
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
        if pin:
            self._pinComboBox.setCurrentIndex(self._pinComboBox.findText(pin))

    def _setup_connections(self):
        self._sensorNameComboBox.currentIndexChanged.connect(self._sensor_name_combobox_current_index_changed)
        self._dialogButtons.accepted.connect(self._validations)
        self._dialogButtons.rejected.connect(self.reject)

    def _sensor_name_combobox_current_index_changed(self, index):
        _sensorType = self._sensorNameComboBox.itemData(index).toString()
        self._set_goal_value_spinbox_suffix(_sensorType)
        self._set_goal_value_spinbox_range(_sensorType)

    def _set_goal_value_spinbox_suffix(self, sensor_type):
        _suffix = self._get_suffix(sensor_type)
        self._goalValueDoubleSpinBox.setSuffix(_suffix)

    def _set_goal_value_spinbox_range(self, sensor_type):
        _rangeList = [[0.00, 100.00], [0.00, 100.00], [0.00, 100.00], [0.00, 100.00], [0.00, 100.00], [0, 1],
                      [0.00, 14.00], [0.00, 100.00]]
        _tuple = _rangeList[int(sensor_type) - 1]
        self._goalValueDoubleSpinBox.setRange(_tuple[0], _tuple[1])

    @staticmethod
    def _get_suffix(sensor_type):
        # Degree symbol, Octal value
        _degreeChar = QtCore.QChar(0260)
        _degree = QtCore.QString(' C')
        _degree.append(_degreeChar)
        _suffixList = [_degree, _degree, ' %', _degree, ' %', ' *', ' PH', ' us']
        return _suffixList[int(sensor_type) - 1]

    def _validations(self):
        if self._deviceNameLineEdit.text().isEmpty():
            QtGui.QMessageBox().warning(self, 'Falta Nombre', 'No has escrito un nombre', QtGui.QMessageBox.Ok)
            self._nameLineEdit.setFocus()
        else:
            self._deviceNameLineEdit.setText(self._deviceNameLineEdit.text().replace(' ', '_'))
            self.accept()

    # Get data from dialog
    def _get_sensor_name(self):
        return self._sensorNameComboBox.itemText(self._sensorNameComboBox.currentIndex())

    def _get_sensor_type(self):
        return self._sensorNameComboBox.itemData(self._sensorNameComboBox.currentIndex()).toString()

    def _get_operator(self):
        return self._operatorComboBox.itemText(self._operatorComboBox.currentIndex())

    def _get_goal_value(self):
        return str(self._goalValueDoubleSpinBox.value())

    def _get_device_name(self):
        return self._deviceNameLineEdit.text()

    def _get_pause(self):
        return self._pauseTimeEdit.time().toString('HH:mm:ss')

    def _get_protocol(self):
        return self._protocolComboBox.itemText(self._protocolComboBox.currentIndex())

    def _get_pin(self):
        return self._pinComboBox.itemText(self._pinComboBox.currentIndex())

    # static method to create the dialog and return (name, time, etc, accepted)
    @staticmethod
    def get_data(title, sensor_name='', sensor_type='', operator='', goal_value='', device_name='', pause='',
                 protocol='', pin='', parent=None):
        dialog = SecondLevelItemSensorDialog(title, sensor_name, sensor_type, operator, goal_value, device_name, pause,
                                             protocol, pin, parent)
        _result = dialog.exec_()
        _sensorNameStr = dialog._get_sensor_name()
        _sensorTypeStr = dialog._get_sensor_type()
        _operatorStr = dialog._get_operator()
        _goalValueStr = dialog._get_goal_value()
        _deviceNameStr = dialog._get_device_name()
        _pauseStr = dialog._get_pause()
        _protocolStr = dialog._get_protocol()
        _pinStr = dialog._get_pin()
        return _sensorNameStr, _sensorTypeStr, _operatorStr, _goalValueStr, _deviceNameStr, _pauseStr, \
               _protocolStr, _pinStr, _result == QtGui.QDialog.Accepted

    # -------------------------------------SECOND LEVEL COMPONENT---------------------------------------------


class SecondLevelItemComponentDialog(QtGui.QDialog):
    def __init__(self, title, component_name='', component_type='', operator='', goal_value='', device_name='',
                 pause='', protocol='', pin='', parent=None):
        super(SecondLevelItemComponentDialog, self).__init__(parent)
        self.setWindowTitle(title)
        self._myDataBase = database.DataBase()

        # Nice widget for editing
        self._componentNameLabel = QtGui.QLabel('Sensor:', self)
        self._operatorLabel = QtGui.QLabel('Operador:', self)
        self._goalValueLabel = QtGui.QLabel('Valor Limite:', self)
        self._deviceNameLabel = QtGui.QLabel('Dispositivo:', self)
        self._pauseLabel = QtGui.QLabel('Pausa:', self)
        self._protocolLabel = QtGui.QLabel('Protocolo:', self)
        self._pinLabel = QtGui.QLabel('Pin:', self)

        self._componentNameComboBox = QtGui.QComboBox(self)
        self._operatorComboBox = QtGui.QComboBox(self)
        self._goalStateComboBox = QtGui.QComboBox(self)
        self._deviceNameLineEdit = QtGui.QLineEdit(self)
        self._pauseTimeEdit = QtGui.QTimeEdit(self)
        self._protocolComboBox = QtGui.QComboBox(self)
        self._pinComboBox = QtGui.QComboBox(self)

        # OK and Cancel buttons
        self._dialogButtons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                                     QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        self._setup(component_name, component_type, operator, goal_value, device_name, pause, protocol, pin)

    def _setup(self, component_name, component_type, operator, goal_value, device_name, pause, protocol, pin):
        self.setGeometry(500, 200, 300, 400)
        self._setup_layouts()
        self._setup_component_name_combobox(component_name, component_type)
        self._setup_operator_combobox(operator)
        self._setup_goal_state_combobox(goal_value)
        self._deviceNameLineEdit.setText(device_name)
        self._setup_pause_time_edit(pause)
        self._setup_protocol_combobox(protocol)
        self._setup_pin_combobox(pin)
        self._setup_connections()

    def _setup_layouts(self):
        _nameLayout = QtGui.QHBoxLayout()
        _nameLayout.addWidget(self._componentNameLabel)
        _nameLayout.addWidget(self._componentNameComboBox)

        _operatorLayout = QtGui.QHBoxLayout()
        _operatorLayout.addWidget(self._operatorLabel)
        _operatorLayout.addWidget(self._operatorComboBox)

        _goalValueLayout = QtGui.QHBoxLayout()
        _goalValueLayout.addWidget(self._goalValueLabel)
        _goalValueLayout.addWidget(self._goalStateComboBox)

        _deviceNameLayout = QtGui.QHBoxLayout()
        _deviceNameLayout.addWidget(self._deviceNameLabel)
        _deviceNameLayout.addWidget(self._deviceNameLineEdit)

        _pauseLayout = QtGui.QHBoxLayout()
        _pauseLayout.addWidget(self._pauseLabel)
        _pauseLayout.addWidget(self._pauseTimeEdit)

        _protocolLayout = QtGui.QHBoxLayout()
        _protocolLayout.addWidget(self._protocolLabel)
        _protocolLayout.addWidget(self._protocolComboBox)

        _pinLayout = QtGui.QHBoxLayout()
        _pinLayout.addWidget(self._pinLabel)
        _pinLayout.addWidget(self._pinComboBox)

        _mainLayout = QtGui.QVBoxLayout(self)
        _mainLayout.addLayout(_nameLayout)
        _mainLayout.addLayout(_operatorLayout)
        _mainLayout.addLayout(_goalValueLayout)
        _mainLayout.addLayout(_deviceNameLayout)
        _mainLayout.addLayout(_pauseLayout)
        _mainLayout.addLayout(_protocolLayout)
        _mainLayout.addLayout(_pinLayout)
        _mainLayout.addWidget(self._dialogButtons)

        self.setLayout(_mainLayout)

    def _setup_component_name_combobox(self, c_name, c_type):
        _customIcons = custom.Icons()
        _nameList = self._myDataBase.component_table_select_component_names()
        for _tuple in _nameList:
            self._componentNameComboBox.addItem(_customIcons.get_component_icon(_tuple[1]), _tuple[0], _tuple[1])
        if c_name:
            _count = self._componentNameComboBox.count()
            for i in xrange(_count):
                _text = self._componentNameComboBox.itemText(i)
                _data = self._componentNameComboBox.itemData(i).toString()
                if c_name == _text and c_type == _data:
                    self._componentNameComboBox.setCurrentIndex(i)
                    break

    def _setup_operator_combobox(self, operator):
        self._operatorComboBox.addItems(['==', '!='])
        if operator:
            a = self._operatorComboBox.findText(operator)
            self._operatorComboBox.setCurrentIndex(self._operatorComboBox.findText(operator))

    def _setup_goal_state_combobox(self, c_state):
        _customIcons = custom.Icons()
        self._goalStateComboBox.addItem(_customIcons.get_state_icon(0), 'Apagado', '0')
        self._goalStateComboBox.addItem(_customIcons.get_state_icon(1), 'Encendido', '1')
        if c_state:
            if c_state == '0':
                self._goalStateComboBox.setCurrentIndex(0)
            else:
                self._goalStateComboBox.setCurrentIndex(1)

    def _setup_pause_time_edit(self, pause):
        self._pauseTimeEdit.setDisplayFormat('HH:mm:ss')
        if pause:
            self._pauseTimeEdit.setTime(QtCore.QTime(int(pause.mid(0, 2)), int(pause.mid(3, 2)),
                                                     int(pause.mid(6, 2))))

    def _setup_protocol_combobox(self, protocol):
        self._protocolComboBox.addItems(['1', '2', '3'])
        if protocol:
            self._protocolComboBox.setCurrentIndex(self._protocolComboBox.findText(protocol))

    def _setup_pin_combobox(self, pin):
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
        if pin:
            self._pinComboBox.setCurrentIndex(self._pinComboBox.findText(pin))

    def _setup_connections(self):
        self._dialogButtons.accepted.connect(self._validations)
        self._dialogButtons.rejected.connect(self.reject)

    def _validations(self):
        if self._deviceNameLineEdit.text().isEmpty():
            QtGui.QMessageBox().warning(self, 'Falta Nombre', 'No has escrito un nombre', QtGui.QMessageBox.Ok)
            self._nameLineEdit.setFocus()
        else:
            self._deviceNameLineEdit.setText(self._deviceNameLineEdit.text().replace(' ', '_'))
            self.accept()

    # Get data from dialog
    def _get_sensor_name(self):
        return self._componentNameComboBox.itemText(self._componentNameComboBox.currentIndex())

    def _get_sensor_type(self):
        return self._componentNameComboBox.itemData(self._componentNameComboBox.currentIndex()).toString()

    def _get_operator(self):
        return self._operatorComboBox.itemText(self._operatorComboBox.currentIndex())

    def _get_goal_state(self):
        return self._goalStateComboBox.itemData(self._goalStateComboBox.currentIndex()).toString()

    def _get_device_name(self):
        return self._deviceNameLineEdit.text()

    def _get_pause(self):
        return self._pauseTimeEdit.time().toString('HH:mm:ss')

    def _get_protocol(self):
        return self._protocolComboBox.itemText(self._protocolComboBox.currentIndex())

    def _get_pin(self):
        return self._pinComboBox.itemText(self._pinComboBox.currentIndex())

    # static method to create the dialog and return (name, time, etc, accepted)
    @staticmethod
    def get_data(title, sensor_name='', sensor_type='', operator='', goal_value='', device_name='', pause='',
                 protocol='', pin='', parent=None):
        dialog = SecondLevelItemComponentDialog(title, sensor_name, sensor_type, operator, goal_value, device_name,
                                                pause, protocol, pin, parent)
        _result = dialog.exec_()
        _componentNameStr = dialog._get_sensor_name()
        _componentTypeStr = dialog._get_sensor_type()
        _operatorStr = dialog._get_operator()
        _goalStateStr = dialog._get_goal_state()
        _deviceNameStr = dialog._get_device_name()
        _pauseStr = dialog._get_pause()
        _protocolStr = dialog._get_protocol()
        _pinStr = dialog._get_pin()
        return _componentNameStr, _componentTypeStr, _operatorStr, _goalStateStr, _deviceNameStr, _pauseStr, \
               _protocolStr, _pinStr, _result == QtGui.QDialog.Accepted