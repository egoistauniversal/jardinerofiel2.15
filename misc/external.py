from PyQt4 import QtCore
from PyQt4 import QtGui
from custom import StandardItemState, StandardItemComponentType, StandardItemSensorType
from custom import StandardItemControlType, StandardItemDownCounter


class Generals(QtCore.QObject):
    @staticmethod
    def get_date_time_state(date_time_on, date_time_off):
        state = '0'
        _currentDateTime = QtCore.QDateTime().currentDateTime()
        if date_time_on > date_time_off:
            if _currentDateTime < date_time_off:
                date_time_on = date_time_on.addDays(1)
                state = '1'
            else:
                if _currentDateTime >= date_time_on:
                    date_time_on = date_time_on.addDays(1)
                    date_time_off = date_time_off.addDays(1)
                    state = '1'
                else:
                    date_time_off = date_time_off.addDays(1)
        elif date_time_on <= _currentDateTime < date_time_off:
            date_time_on = date_time_on.addDays(1)
            state = '1'
        elif date_time_on <= _currentDateTime > date_time_off:
            date_time_on = date_time_on.addDays(1)
            date_time_off = date_time_off.addDays(1)

        return state, date_time_on, date_time_off

    @staticmethod
    def get_date_time_data_type(my_time):
        _myDateTime = QtCore.QDateTime(QtCore.QDate().currentDate(),
                                       QtCore.QTime(int(my_time.mid(0, 2)),
                                                    int(my_time.mid(3, 2)),
                                                    int(my_time.mid(6, 2))))
        return _myDateTime

    # ---------------------------------------COMPONENTS-------------------------------------------------

    @staticmethod
    def component_add_first_level_item(item, c_name):
        item.appendRow(QtGui.QStandardItem(c_name))

    def component_add_second_level_item_clock(self, item, c_name, c_type, c_time_on, c_time_off, c_pin, c_active):
        _nameItem = QtGui.QStandardItem(c_name)
        _timeTypeItem = StandardItemComponentType(c_type)
        _dateTimeOn = self.get_date_time_data_type(c_time_on)
        _dateTimeOff = self.get_date_time_data_type(c_time_off)
        _activeItem = QtGui.QStandardItem()
        _activeItem.setCheckable(True)
        if c_active == 1:
            _activeItem.setCheckState(QtCore.Qt.Checked)
        _activeItem.setEnabled(False)

        _state, _dateTimeOn, _dateTimeOff = self.get_date_time_state(_dateTimeOn, _dateTimeOff)
        _dateTimeOnItem = QtGui.QStandardItem(_dateTimeOn.toString("HH:mm:ss dd-MM-yyyy"))
        _dateTimeOffItem = QtGui.QStandardItem(_dateTimeOff.toString("HH:mm:ss dd-MM-yyyy"))
        _stateItem = StandardItemState(_state)
        if c_active == 0:
            _stateItem.set_tag('0')
        else:
            _stateItem.set_tag(_state)

        _timeLeftItem = QtGui.QStandardItem('')
        _pinItem = QtGui.QStandardItem(c_pin)
        item.appendRow([_nameItem, _timeTypeItem, _dateTimeOnItem, _dateTimeOffItem,
                        _timeLeftItem, _stateItem, _pinItem, _activeItem])
        return _state

    def component_modify_second_level_item_clock(self, index, c_name, c_on, c_off, c_pin):
        _dateTimeOn = self.get_date_time_data_type(c_on)
        _dateTimeOff = self.get_date_time_data_type(c_off)
        state, _dateTimeOn, _dateTimeOff = self.get_date_time_state(_dateTimeOn, _dateTimeOff)

        index.model().itemFromIndex(index.parent().child(index.row(), 0)).setData(c_name, QtCore.Qt.DisplayRole)
        index.model().itemFromIndex(index.parent().child(index.row(), 2)).setData(
            _dateTimeOn.toString("HH:mm:ss dd-MM-yyyy"), QtCore.Qt.DisplayRole)
        index.model().itemFromIndex(index.parent().child(index.row(), 3)).setData(
            _dateTimeOff.toString("HH:mm:ss dd-MM-yyyy"), QtCore.Qt.DisplayRole)
        index.model().itemFromIndex(index.parent().child(index.row(), 5)).set_tag(state)
        index.model().itemFromIndex(index.parent().child(index.row(), 6)).setData(c_pin, QtCore.Qt.DisplayRole)
        return state

    @staticmethod
    def component_add_second_level_item_timer(item, c_name, c_type, c_time_on, c_time_off, c_pin, c_active):
        _nameItem = QtGui.QStandardItem(c_name)
        _timeTypeItem = StandardItemComponentType(c_type)
        _timeOnItem = QtGui.QStandardItem(c_time_on)
        _timeOffItem = QtGui.QStandardItem(c_time_off)
        _timeLeftItem = QtGui.QStandardItem(c_time_on)
        _pinItem = QtGui.QStandardItem(c_pin)
        _activeItem = QtGui.QStandardItem()
        _activeItem.setCheckable(True)
        if c_active == 1:
            _activeItem.setCheckState(QtCore.Qt.Checked)
            _stateItem = StandardItemState('1')
        else:
            _stateItem = StandardItemState('0')
        _activeItem.setEnabled(False)

        item.appendRow([_nameItem, _timeTypeItem, _timeOnItem, _timeOffItem, _timeLeftItem, _stateItem,
                        _pinItem, _activeItem])

    @staticmethod
    def component_modify_second_level_item_timer(index, c_name, c_time_on, c_time_off, c_pin):
        index.model().itemFromIndex(index.parent().child(index.row(), 0)).setData(c_name, QtCore.Qt.DisplayRole)
        index.model().itemFromIndex(index.parent().child(index.row(), 2)).setData(c_time_on, QtCore.Qt.DisplayRole)
        index.model().itemFromIndex(index.parent().child(index.row(), 3)).setData(c_time_off, QtCore.Qt.DisplayRole)
        index.model().itemFromIndex(index.parent().child(index.row(), 6)).setData(c_pin, QtCore.Qt.DisplayRole)

    # ----------------------------------------SENSORS---------------------------------------------------

    @staticmethod
    def sensor_add_first_level_item(item, s_name):
        item.appendRow(QtGui.QStandardItem(s_name))

    @staticmethod
    def sensor_add_second_level_item(item, sensor_name, sensor_type, sensor_pin, sensor_active):
        _nameItem = QtGui.QStandardItem(sensor_name)
        _sensorTypeItem = StandardItemSensorType(sensor_type)
        _currentDataItem = QtGui.QStandardItem('')
        _minItem = QtGui.QStandardItem('')
        _minTimeItem = QtGui.QStandardItem('')
        _minDateItem = QtGui.QStandardItem('')
        _maxItem = QtGui.QStandardItem('')
        _maxTimeItem = QtGui.QStandardItem('')
        _maxDateItem = QtGui.QStandardItem('')
        _pinItem = QtGui.QStandardItem(sensor_pin)
        _activeItem = QtGui.QStandardItem()
        _activeItem.setCheckable(True)
        if sensor_active == 1:
            _activeItem.setCheckState(QtCore.Qt.Checked)
        _activeItem.setEnabled(False)
        # adds new row with '_nameItem' in the first column and 'timeTypeItem' in the second and so forth...
        item.appendRow([_nameItem, _sensorTypeItem, _currentDataItem,
                        _minItem, _minTimeItem, _minDateItem,
                        _maxItem, _maxTimeItem, _maxDateItem, _pinItem, _activeItem])

    @staticmethod
    def sensor_modify_first_level_item(item, s_name):
        item.setData(s_name, QtCore.Qt.DisplayRole)

    @staticmethod
    def sensor_modify_second_level_item(index, sensor_name, sensor_pin):
        index.model().itemFromIndex(index.parent().child(index.row(), 0)).setData(sensor_name, QtCore.Qt.DisplayRole)
        index.model().itemFromIndex(index.parent().child(index.row(), 9)).setData(sensor_pin, QtCore.Qt.DisplayRole)

    @staticmethod
    def sensor_clear_row_item(index):
        for x in xrange(2, 9):
            index.model().itemFromIndex(index.parent().child(index.row(), x)).setData('', QtCore.Qt.DisplayRole)

    @staticmethod
    def sensor_reset_single_row_min_max(index):
        for x in xrange(3, 9):
            index.model().itemFromIndex(index.parent().child(index.row(), x)).setData('', QtCore.Qt.DisplayRole)

    def sensor_reset_all_min_max(self, model):
        _rootItem = model.item(0, 0)
        for i in xrange(_rootItem.rowCount()):
            _groupItem = _rootItem.child(i, 0)
            if _groupItem.hasChildren():
                for x in xrange(_groupItem.rowCount()):
                    self.sensor_reset_single_row_min_max(_groupItem.child(x, 0).index())

    # ----------------------------------------CONTROLS---------------------------------------------------

    @staticmethod
    def control_add_first_level_item(item, s_name):
        item.appendRow(QtGui.QStandardItem(s_name))

    @staticmethod
    def control_add_second_level_item_sensor(item, control_type, x_name, x_type, operator, goal_value,
                                             device_name, pause, protocol, pin, active, control_id):
        _controlType = StandardItemControlType(control_type)
        _controlType.set_id(control_id)
        _xNameItem = QtGui.QStandardItem(x_name)
        _operatorItem = QtGui.QStandardItem(operator)
        if control_type == '1':
            _xTypeItem = StandardItemSensorType(x_type)
            _dataItem = QtGui.QStandardItem()
            _goalValueItem = QtGui.QStandardItem(goal_value)
        else:
            _xTypeItem = StandardItemComponentType(x_type)
            _dataItem = StandardItemState('0')
            _goalValueItem = StandardItemState(goal_value)
        _goalNameItem = QtGui.QStandardItem(device_name)
        _pauseItem = QtGui.QStandardItem(pause)
        _timeLeftItem = StandardItemDownCounter(pause)
        _stateItem = StandardItemState('0')
        _protocolItem = QtGui.QStandardItem(protocol)
        _pinItem = QtGui.QStandardItem(pin)
        _activeItem = QtGui.QStandardItem()
        _activeItem.setCheckable(True)
        if active == 1:
            _activeItem.setCheckState(QtCore.Qt.Checked)
        _activeItem.setEnabled(False)
        item.appendRow([_controlType, _xNameItem, _xTypeItem, _dataItem, _operatorItem, _goalValueItem,
                        _goalNameItem, _pauseItem, _timeLeftItem, _stateItem, _protocolItem, _pinItem, _activeItem])

    @staticmethod
    def control_modify_second_level_item_sensor(index, sensor_name, sensor_type, operator,
                                                goal_value, device_name, pause, protocol, pin):
        index.model().itemFromIndex(index.parent().child(index.row(), 1)).setData(sensor_name, QtCore.Qt.DisplayRole)
        index.model().itemFromIndex(index.parent().child(index.row(), 2)).set_tag(sensor_type)
        index.model().itemFromIndex(index.parent().child(index.row(), 4)).setData(operator, QtCore.Qt.DisplayRole)
        index.model().itemFromIndex(index.parent().child(index.row(), 5)).setData(goal_value, QtCore.Qt.DisplayRole)
        index.model().itemFromIndex(index.parent().child(index.row(), 6)).setData(device_name, QtCore.Qt.DisplayRole)
        index.model().itemFromIndex(index.parent().child(index.row(), 7)).setData(pause, QtCore.Qt.DisplayRole)
        index.model().itemFromIndex(index.parent().child(index.row(), 8)).set_pause(pause)
        index.model().itemFromIndex(index.parent().child(index.row(), 10)).setData(protocol, QtCore.Qt.DisplayRole)
        index.model().itemFromIndex(index.parent().child(index.row(), 11)).setData(pin, QtCore.Qt.DisplayRole)

    @staticmethod
    def control_modify_second_level_item_component(index, component_name, component_type, operator,
                                                   goal_state, device_name, pause, protocol, pin):
        index.model().itemFromIndex(index.parent().child(index.row(), 1)).setData(component_name, QtCore.Qt.DisplayRole)
        index.model().itemFromIndex(index.parent().child(index.row(), 2)).set_tag(component_type)
        index.model().itemFromIndex(index.parent().child(index.row(), 4)).setData(operator, QtCore.Qt.DisplayRole)
        index.model().itemFromIndex(index.parent().child(index.row(), 5)).set_tag(goal_state)
        index.model().itemFromIndex(index.parent().child(index.row(), 6)).setData(device_name, QtCore.Qt.DisplayRole)
        index.model().itemFromIndex(index.parent().child(index.row(), 7)).setData(pause, QtCore.Qt.DisplayRole)
        index.model().itemFromIndex(index.parent().child(index.row(), 8)).set_pause(pause)
        index.model().itemFromIndex(index.parent().child(index.row(), 10)).setData(protocol, QtCore.Qt.DisplayRole)
        index.model().itemFromIndex(index.parent().child(index.row(), 11)).setData(pin, QtCore.Qt.DisplayRole)