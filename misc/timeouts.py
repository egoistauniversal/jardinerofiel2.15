from PyQt4 import QtCore
import operator


class Sensors(QtCore.QObject):
    timeoutSensorReadSignal = QtCore.pyqtSignal(str, str)
    timeoutSensorUpdateGraphicSignal = QtCore.pyqtSignal()

    def __init__(self, model):
        QtCore.QObject.__init__(self)
        self._timer = QtCore.QTimer(self)
        self._rootItem = model.item(0, 0)
        self._groupItem = None
        self._groupMaxRows = 0
        self._groupRow = 0
        self._childMaxRows = 0
        self._childRow = -1
        self._setup()

    def _setup(self):
        self._connections()

    def _connections(self):
        self._timer.timeout.connect(self._read)

    def start_timer(self):
        self._timer.start()

    def _read(self):
        self._groupMaxRows = self._rootItem.rowCount()
        if self._groupRow < self._groupMaxRows:
            self._groupItem = self._rootItem.child(self._groupRow, 0)
            self._childMaxRows = self._groupItem.rowCount()
            self._childRow += 1
            if self._childRow < self._childMaxRows:
                # Execute only if the checkbox is checked
                if self._groupItem.child(self._childRow, 10).checkState() == QtCore.Qt.Checked:
                    _sensorType = self._groupItem.child(self._childRow, 1).get_tag()
                    _sensorPin = self._groupItem.child(self._childRow, 9).data(QtCore.Qt.DisplayRole).toString()
                    self.timeoutSensorReadSignal.emit(str(_sensorPin), str(_sensorType))
            else:
                self._childRow = -1
                self._groupRow += 1
        else:
            # When the lecture of sensors is finished...
            self._timer.stop()
            self._childRow = -1
            self._groupRow = 0
            # self.timeoutSensorUpdateGraphicSignal.emit()

    def get_parent(self):
        return self._groupItem

    def get_row(self):
        return self._childRow

    def set_timer_interval(self, interval):
        self._timer.setInterval(interval)


class Components(QtCore.QObject):
    componentChangeStateSignal = QtCore.pyqtSignal(str, str, str, str)
    componentUpdateControlStateSignal = QtCore.pyqtSignal(str, str, str)

    def timeout(self, model, interval):
        _rootItem = model.item(0, 0)
        for i in xrange(_rootItem.rowCount()):
            _groupItem = _rootItem.child(i, 0)
            if _groupItem.hasChildren():
                for x in xrange(_groupItem.rowCount()):
                    # Execute only if the checkbox is checked
                    if _groupItem.child(x, 7).checkState():
                        _componentTimerTypeItem = _groupItem.child(x, 1)
                        _timerType = _componentTimerTypeItem.get_tag()
                        if _timerType == '1':
                            self._clock(_groupItem, x)
                        elif _timerType == '2':
                            self._timer(_groupItem, x, interval)
                        elif _timerType == '3':
                            pass

    def _clock(self, item, x):
        # Get date and time strings from treeview
        aux = item.child(x, 2).data(QtCore.Qt.DisplayRole).toString()
        # format from string to QDateTime
        _dateTimeOn = QtCore.QDateTime().fromString(aux, "HH:mm:ss dd-MM-yyyy")
        # Get date and time strings from treeview
        aux = item.child(x, 3).data(QtCore.Qt.DisplayRole).toString()
        # format from string to QDateTime
        _dateTimeOff = QtCore.QDateTime().fromString(aux, "HH:mm:ss dd-MM-yyyy")
        _isOn = item.child(x, 5).get_tag_bool()
        _currentDateTime = QtCore.QDateTime().currentDateTime()
        if _isOn:
            if len(item.child(x, 4).data(QtCore.Qt.DisplayRole).toString()) == 0:
                item.child(x, 4).setData(_dateTimeOff.toString("HH:mm:ss"), QtCore.Qt.DisplayRole)
            if item.child(x, 4).data(QtCore.Qt.DisplayRole).toTime() <= QtCore.QTime(0, 0, 0, 0):
                # if _dateTimeOff <= _currentDateTime:
                _dateTimeOff = _dateTimeOff.addDays(1)
                item.child(x, 3).setData(_dateTimeOff.toString("HH:mm:ss dd-MM-yyyy"), QtCore.Qt.DisplayRole)
                item.child(x, 5).set_tag('0')
                pin = item.child(x, 6).data(QtCore.Qt.DisplayRole).toString()
                self.componentChangeStateSignal.emit('1', '2', pin, '0')
                _name = item.child(x, 0).data(QtCore.Qt.DisplayRole).toString()
                _type = item.child(x, 1).get_tag()
                _state = item.child(x, 5).get_tag()
                self.componentUpdateControlStateSignal.emit(_name, _type, _state)
                # Time span between two QDateTime
                _dateTimeSpan = self._date_time_span(_currentDateTime, _dateTimeOn)
                item.child(x, 4).setData(_dateTimeSpan.toString("HH:mm:ss"), QtCore.Qt.DisplayRole)
            else:
                # Time span between two QDateTime
                _dateTimeSpan = self._date_time_span(_currentDateTime, _dateTimeOff)
                item.child(x, 4).setData(_dateTimeSpan.toString("HH:mm:ss"), QtCore.Qt.DisplayRole)
        else:
            if len(item.child(x, 4).data(QtCore.Qt.DisplayRole).toString()) == 0:
                item.child(x, 4).setData(_dateTimeOn.toString("HH:mm:ss"), QtCore.Qt.DisplayRole)
            if item.child(x, 4).data(QtCore.Qt.DisplayRole).toTime() <= QtCore.QTime(0, 0, 0, 0):
                # if _dateTimeOn <= _currentDateTime:
                _dateTimeOn = _dateTimeOn.addDays(1)
                item.child(x, 2).setData(_dateTimeOn.toString("HH:mm:ss dd-MM-yyyy"), QtCore.Qt.DisplayRole)
                item.child(x, 5).set_tag('1')
                pin = item.child(x, 6).data(QtCore.Qt.DisplayRole).toString()
                self.componentChangeStateSignal.emit('1', '2', pin, '1')
                _name = item.child(x, 0).data(QtCore.Qt.DisplayRole).toString()
                _type = item.child(x, 1).get_tag()
                _state = item.child(x, 5).get_tag()
                self.componentUpdateControlStateSignal.emit(_name, _type, _state)
                # Time span between two QDateTime
                _dateTimeSpan = self._date_time_span(_currentDateTime, _dateTimeOff)
                item.child(x, 4).setData(_dateTimeSpan.toString("HH:mm:ss"), QtCore.Qt.DisplayRole)
            else:
                # Time span between two QDateTime
                _dateTimeSpan = self._date_time_span(_currentDateTime, _dateTimeOn)
                item.child(x, 4).setData(_dateTimeSpan.toString("HH:mm:ss"), QtCore.Qt.DisplayRole)

    @staticmethod
    def _date_time_span(now_date_time, my_date_time):
        # Time span between two QDateTime
        _secondsLeft = now_date_time.secsTo(my_date_time)
        return QtCore.QDateTime().fromTime_t(_secondsLeft)

    # --------------------------------------------------------------------------------

    def _timer(self, item, x, interval):
        # Get time from treeview string
        temp = item.child(x, 2).data(QtCore.Qt.DisplayRole).toString()
        # format from string to QDateTime
        _timeOn = QtCore.QTime().fromString(temp, "HH:mm:ss")
        # Get time from treeview string
        temp = item.child(x, 3).data(QtCore.Qt.DisplayRole).toString()
        # format from string to QDateTime
        _timeOff = QtCore.QTime().fromString(temp, "HH:mm:ss")
        temp = item.child(x, 4).data(QtCore.Qt.DisplayRole).toString()
        _timeLeft = QtCore.QTime().fromString(temp, "HH:mm:ss")
        _timeLeft = _timeLeft.addMSecs(-interval)
        _isOn = item.child(x, 5).get_tag_bool()
        _zeroTime = QtCore.QTime(0, 0, 0)
        _pin = item.child(x, 6).data(QtCore.Qt.DisplayRole).toString()
        if _isOn:
            if _timeLeft <= _zeroTime:
                item.child(x, 4).setData(_timeOff.toString("HH:mm:ss"), QtCore.Qt.DisplayRole)
                item.child(x, 5).set_tag('0')
                self.componentChangeStateSignal.emit('1', '2', _pin, '0')
                _name = item.child(x, 0).data(QtCore.Qt.DisplayRole).toString()
                _type = item.child(x, 1).get_tag()
                _state = item.child(x, 5).get_tag()
                self.componentUpdateControlStateSignal.emit(_name, _type, _state)
            else:
                item.child(x, 4).setData(_timeLeft.toString("HH:mm:ss"), QtCore.Qt.DisplayRole)
        else:
            if _timeLeft <= _zeroTime:
                item.child(x, 4).setData(_timeOn.toString("HH:mm:ss"), QtCore.Qt.DisplayRole)
                item.child(x, 5).set_tag('1')
                self.componentChangeStateSignal.emit('1', '2', _pin, '1')
                _name = item.child(x, 0).data(QtCore.Qt.DisplayRole).toString()
                _type = item.child(x, 1).get_tag()
                _state = item.child(x, 5).get_tag()
                self.componentUpdateControlStateSignal.emit(_name, _type, _state)
            else:
                item.child(x, 4).setData(_timeLeft.toString("HH:mm:ss"), QtCore.Qt.DisplayRole)


class Controls(QtCore.QObject):
    controlChangeStateSignal = QtCore.pyqtSignal(str, str)

    def __init__(self):
        QtCore.QObject.__init__(self)
        self._sensorOperators = {'>': operator.gt, '<': operator.lt, '>=': operator.ge, '<=': operator.le}
        self._componentOperators = {'==': operator.eq, '!=': operator.ne}

    def update_data(self, model, x_control_type, x_name, x_type, x_data):
        _rootItem = model.item(0, 0)
        for i in xrange(_rootItem.rowCount()):
            _groupItem = _rootItem.child(i, 0)
            if _groupItem.hasChildren():
                for row in xrange(_groupItem.rowCount()):
                    # Execute only if the checkbox is checked
                    # if _groupItem.child(row, 12).checkState():
                    _controlTypeItem = _groupItem.child(row, 0)
                    _controlType = _controlTypeItem.get_tag()
                    if _controlType == x_control_type:
                        if _controlType == '1':
                            self._sensor_data(_groupItem, row, x_name, x_type, x_data)
                        elif _controlType == '2':
                            self._component_data(_groupItem, row, x_name, x_type, x_data)
                        elif _controlType == '3':
                            pass

    def _sensor_data(self, item, row, s_name, s_type, s_data):
        _nameItem = item.child(row, 1).data(QtCore.Qt.DisplayRole).toString()
        _typeItem = item.child(row, 2).get_tag()
        if s_name == _nameItem and s_type == _typeItem:
            item.child(row, 3).setData(s_data, QtCore.Qt.DisplayRole)
            if item.child(row, 12).checkState():
                _dataItem = item.child(row, 3).data(QtCore.Qt.DisplayRole).toString()
                _operatorItem = item.child(row, 4).data(QtCore.Qt.DisplayRole).toString()
                _goalValueItem = item.child(row, 5).data(QtCore.Qt.DisplayRole).toString()
                _pauseItem = item.child(row, 7).data(QtCore.Qt.DisplayRole).toTime()
                _operatorFunction = self._sensorOperators[str(_operatorItem)]
                _isOnItem = item.child(row, 9).get_tag_bool()
                _pin = item.child(row, 11).data(QtCore.Qt.DisplayRole).toString()
                if _operatorFunction(float(_dataItem), float(_goalValueItem)):
                    if not _isOnItem:
                        if _pauseItem != QtCore.QTime(0, 0, 0):
                            if not item.child(row, 8).timer_is_active():
                                item.child(row, 8).start_timer()
                                item.child(row, 9).set_tag('1')
                                self.controlChangeStateSignal.emit(_pin, '1')
                        else:
                            item.child(row, 9).set_tag('1')
                            self.controlChangeStateSignal.emit(_pin, '1')
                else:
                    if _isOnItem:
                        if _pauseItem != QtCore.QTime(0, 0, 0):
                            if not item.child(row, 8).timer_is_active():
                                item.child(row, 8).start_timer()
                                item.child(row, 9).set_tag('0')
                                self.controlChangeStateSignal.emit(_pin, '0')
                        else:
                            item.child(row, 9).set_tag('0')
                            self.controlChangeStateSignal.emit(_pin, '0')

    def _component_data(self, item, row, c_name, c_type, c_state):
        _nameItem = item.child(row, 1).data(QtCore.Qt.DisplayRole).toString()
        _typeItem = item.child(row, 2).get_tag()
        if c_name == _nameItem and c_type == _typeItem:
            item.child(row, 3).set_tag(c_state)
            if item.child(row, 12).checkState():
                _dataItem = item.child(row, 3).get_tag()
                _operatorItem = item.child(row, 4).data(QtCore.Qt.DisplayRole).toString()
                _goalValueItem = item.child(row, 5).get_tag()
                _pauseItem = item.child(row, 7).data(QtCore.Qt.DisplayRole).toTime()
                _operatorFunction = self._componentOperators[str(_operatorItem)]
                _isOnItem = item.child(row, 9).get_tag_bool()
                _pin = item.child(row, 11).data(QtCore.Qt.DisplayRole).toString()
                if _operatorFunction(_dataItem, _goalValueItem):
                    if not _isOnItem:
                        if _pauseItem != QtCore.QTime(0, 0, 0):
                            if not item.child(row, 8).timer_is_active():
                                item.child(row, 8).start_timer()
                                item.child(row, 9).set_tag('1')
                                self.controlChangeStateSignal.emit(_pin, '1')
                        else:
                            item.child(row, 9).set_tag('1')
                            self.controlChangeStateSignal.emit(_pin, '1')
                else:
                    if _isOnItem:
                        if _pauseItem != QtCore.QTime(0, 0, 0):
                            if not item.child(row, 8).timer_is_active():
                                item.child(row, 8).start_timer()
                                item.child(row, 9).set_tag('0')
                                self.controlChangeStateSignal.emit(_pin, '0')
                        else:
                            item.child(row, 9).set_tag('0')
                            self.controlChangeStateSignal.emit(_pin, '0')

    # ----------------------------------------UPDATE------------------------------------------------

    def update_name(self, model, x_control_type, previous_name, x_new_name, x_type):
        _id = None
        _rootItem = model.item(0, 0)
        for i in xrange(_rootItem.rowCount()):
            _groupItem = _rootItem.child(i, 0)
            if _groupItem.hasChildren():
                for row in xrange(_groupItem.rowCount()):
                    # Execute only if the checkbox is checked
                    # if _groupItem.child(row, 12).checkState():
                    _controlTypeItem = _groupItem.child(row, 0)
                    _controlType = _controlTypeItem.get_tag()
                    if _controlType == x_control_type:
                        if _controlType == '1':
                            _id = self._sensor_name(_groupItem, row, previous_name, x_new_name, x_type)
                        elif _controlType == '2':
                            _id = self._component_name(_groupItem, row, previous_name, x_new_name, x_type)
                        elif _controlType == '3':
                            pass
        return _id

    @staticmethod
    def _sensor_name(item, row, previous_name, new_name, s_type):
        _nameItem = item.child(row, 1).data(QtCore.Qt.DisplayRole).toString()
        _typeItem = item.child(row, 2).get_tag()
        if previous_name == _nameItem and s_type == _typeItem:
            item.child(row, 1).setData(new_name, QtCore.Qt.DisplayRole)
            return item.child(row, 0).get_id()

    @staticmethod
    def _component_name(item, row, previous_name, new_name, c_type):
        _nameItem = item.child(row, 1).data(QtCore.Qt.DisplayRole).toString()
        _typeItem = item.child(row, 2).get_tag()
        if previous_name == _nameItem and c_type == _typeItem:
            item.child(row, 1).setData(new_name, QtCore.Qt.DisplayRole)
            return item.child(row, 0).get_id()