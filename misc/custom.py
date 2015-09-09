from PyQt4 import QtCore, QtGui


class TreeView(QtGui.QTreeView):
    def __init__(self):
        super(TreeView, self).__init__()
        self._setup()

    def _setup(self):
        self.setItemsExpandable(True)

    def edit(self, index, trigger, event):
        if trigger == QtGui.QAbstractItemView.DoubleClicked:
            # print 'DoubleClick Killed!'
            return False
        return QtGui.QTreeView.edit(self, index, trigger, event)

    # ----------------------------------STANDARD ITEMS--------------------------------------------------------


class StandardItemState(QtGui.QStandardItem):
    def __init__(self, estate):
        super(StandardItemState, self).__init__()
        self._state = ''
        self.set_tag(estate)

    def set_tag(self, state):
        self._state = state
        self.setIcon(Icons.get_state_icon(state))

    def get_tag(self):
        return self._state

    def get_tag_bool(self):
        if self._state == '0':
            return False
        else:
            return True


class StandardItemComponentType(QtGui.QStandardItem):
    def __init__(self, tag):
        super(StandardItemComponentType, self).__init__()
        self._tag = ''
        self.set_tag(tag)

    def set_tag(self, tag):
        self._tag = tag
        self.setIcon(Icons.get_component_icon(tag))
        self.setToolTip(ContextMenuOptions.get_component_context_menu_name_options(int(tag)))

    def get_tag(self):
        return self._tag


class StandardItemSensorType(QtGui.QStandardItem):
    def __init__(self, tag):
        super(StandardItemSensorType, self).__init__()
        self._tag = ''
        self.set_tag(tag)

    def set_tag(self, tag):
        self._tag = tag
        self.setIcon(Icons.get_sensor_icon(tag))
        self.setToolTip(ContextMenuOptions.get_sensor_type_name_options(int(tag)))

    def get_tag(self):
        return self._tag


class StandardItemControlType(QtGui.QStandardItem):
    def __init__(self, tag):
        super(StandardItemControlType, self).__init__()
        self._id = None
        self._tag = ''
        self.set_tag(tag)

    def set_id(self, control_id):
        self._id = control_id

    def set_tag(self, tag):
        self._tag = tag
        self.setIcon(Icons.get_control_icon(tag))
        self.setToolTip(ContextMenuOptions.get_control_context_menu_name_options(int(tag)))

    def get_id(self):
        return self._id

    def get_tag(self):
        return self._tag


class StandardItemDownCounter(QtGui.QStandardItem):
    def __init__(self, pause):
        super(StandardItemDownCounter, self).__init__()
        self._timer = QtCore.QTimer()
        self._time = QtCore.QTime(0, 0, 0)
        self._pause = ''
        self._setup(pause)

    def _setup(self, pause):
        self._timer.setInterval(1000)
        self.set_pause(pause)
        self.setData(self._time.toString('HH:mm:ss'), QtCore.Qt.DisplayRole)
        self._timer.timeout.connect(self._countdown)

    def start_timer(self):
        self._timer.start()
        self.setData(self._pause, QtCore.Qt.DisplayRole)

    def stop_timer(self):
        self._timer.stop()

    def timer_is_active(self):
        return self._timer.isActive()

    def set_pause(self, pause):
        self._pause = pause

    def _countdown(self):
        _time = self.data(QtCore.Qt.DisplayRole).toTime()
        _time = _time.addSecs(-1)
        if _time <= QtCore.QTime(0, 0, 0):
            self.stop_timer()
        self.setData(_time.toString('HH:mm:ss'), QtCore.Qt.DisplayRole)

    # -----------------------------------------NAME OPTIONS---------------------------------------------------


class ContextMenuOptions(QtCore.QObject):

    @staticmethod
    def get_component_context_menu_name_options(option):
        return {1: 'Reloj',
                2: 'Temporizador',
                3: 'xxxxx'}[option]

    @staticmethod
    def get_sensor_context_menu_name_options(option):
        return {1: 'Temperatura (DS18B20)',
                2: 'Temperatura y Humedad (DHT11)',
                4: 'PH',
                5: 'EC',
                6: 'Luz'}[option]

    @staticmethod
    def get_sensor_type_name_options(option):
        return {1: 'Temperatura (DS18B20)',
                2: 'Temperatura (DHT11)',
                3: 'Humedad (DHT11)',
                4: 'PH',
                5: 'EC',
                6: 'Luz'}[option]

    @staticmethod
    def get_control_context_menu_name_options(option):
        return {1: 'Sensor',
                2: 'Componentes'}[option]

    # -----------------------------------------ICONS------------------------------------------------------


class Icons(QtCore.QObject):

    @staticmethod
    def get_component_icon(value):
        _iconList = ['images/component/clock.png', 'images/component/timer.png', 'images/component/semiTimer.png']
        return QtGui.QIcon(_iconList[int(value)-1])

    @staticmethod
    def get_sensor_icon(value):
        _iconList = ['images/sensor/thermometer01.jpeg', 'images/sensor/thermometer02.png',
                     'images/sensor/humidity.jpeg', 'images/sensor/ph.jpg', 'images/sensor/ec.jpeg',
                     'images/sensor/light.jpg']
        return QtGui.QIcon(_iconList[int(value)-1])

    @staticmethod
    def get_control_icon(value):
        _iconList = ['images/control/sensor.png', 'images/control/component.png']
        return QtGui.QIcon(_iconList[int(value)-1])

    @staticmethod
    def get_state_icon(value):
        _iconList = ['images/state/off.png', 'images/state/on.png']
        return QtGui.QIcon(_iconList[int(value)])