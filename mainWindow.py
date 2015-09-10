from PyQt4 import QtGui, QtCore

from dialog import configDialogBox
from misc import browser, serialusb, database
from tabs import tabComponents, tabSensors, tabControls
from misc.files import Standard, Intervals, Pins


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self._mySerialUSB = serialusb.SerialUSB()
        self._myTabs = QtGui.QTabWidget(self)
        self._myLog = browser.Browser()
        if not self._mySerialUSB.error:
            self._standardToolBar = self.addToolBar('General')
            self._myLog.print_normal_message(self._mySerialUSB.message)
            self._myDataBase = database.DataBase()
            self._myTabComponents = tabComponents.TabComponents(self._myDataBase, self._mySerialUSB)
            self._myTabSensors = tabSensors.TabSensors(self._myDataBase, self._mySerialUSB)
            self._myTabControl = tabControls.TabControl(self._myDataBase, self._mySerialUSB)
            self._statusBarTimer = QtCore.QTimer(self)
            self._statusBarTimeElapsed = QtCore.QTime()
            self._requestSensorDataFirstTime = QtCore.QTimer(self)
            self._startTimersTimer = QtCore.QTimer(self)
            self._setup()
        else:
            self._setup_user_interface()
            self._myLog.print_alert_message(self._mySerialUSB.message)

    def _setup(self):
        self._myTabs.addTab(self._myTabComponents, 'Componentes')
        self._myTabs.addTab(self._myTabSensors, 'Sensores')
        self._myTabs.addTab(self._myTabControl, 'Controles')
        self._setup_user_interface()
        self._setup_menubar()
        self._setup_general_toolbar()
        self._connections()
        self._setup_files()
        self._myTabSensors.read_structure_from_database()
        self._requestSensorDataFirstTime.singleShot(2000, self._request_sensor_data_first_time)
        self._startTimersTimer.singleShot(6000, self._start_timers)

    def _connections(self):
        self._myTabComponents.componentUpdateControlStateSignal.connect(self._control_update_components)
        self._myTabComponents.componentUpdateControlNameSignal.connect(self._control_update_name_components)
        self._myTabSensors.sensorRestartStatusBarTimeElapsed.connect(self._restart_statusbar_time_elapsed)
        self._myTabSensors.sensorPrintAlertMessage.connect(self._print_alert_message)
        self._myTabSensors.controlUpdateSignal.connect(self._control_update_sensor)
        self._myTabSensors.sensorUpdateControlNameSignal.connect(self._control_update_name_sensors)
        self._myDataBase.dbNormalMessageSignal.connect(self._print_normal_message)
        self._myDataBase.dbAlertMessageSignal.connect(self._print_alert_message)
        self._statusBarTimer.timeout.connect(self._update_statusbar)

    def _setup_user_interface(self):
        self.setWindowTitle('Jardinero Fiel V2.15')
        self.showMaximized()

        self.setCentralWidget(self._myTabs)

        _dockLog = QtGui.QDockWidget('Log', self)
        _dockLog.setMaximumHeight(300)
        _dockLog.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)
        _dockLog.setWidget(self._myLog)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, _dockLog)

        self.statusBar().showMessage('Ready')

    def _setup_menubar(self):
        _standardAction = QtGui.QAction('Standard', self)
        _standardAction.triggered.connect(self._open_standard_dialogbox)

        _pinAction = QtGui.QAction(QtGui.QIcon(), 'Pines', self)
        _pinAction.triggered.connect(self._open_pins_dialogbox)

        _IntervalAction = QtGui.QAction(QtGui.QIcon(), 'Intervalos', self)
        _IntervalAction.triggered.connect(self._open_intervals_dialogbox)

        _exitAction = QtGui.QAction(QtGui.QIcon(), 'Exit', self)
        _exitAction.triggered.connect(self.close)

        _menubar = self.menuBar()
        _fileMenu = _menubar.addMenu('File')
        _fileMenu.addAction(_exitAction)
        _settingsMenu = _menubar.addMenu('Settings')
        _settingsMenu.addAction(_standardAction)
        _settingsMenu.addAction(_pinAction)
        _settingsMenu.addAction(_IntervalAction)

    def _setup_files(self):
        _standardFile = Standard()
        _list = _standardFile.read()
        self._myTabComponents.set_font_size(int(_list[0]))
        self._myTabSensors.set_font_size(int(_list[0]))
        self._myTabSensors.set_sensor_threshold(int(_list[1]))
        self._myTabControl.set_font_size(int(_list[0]))

        Pins()

        _intervalFile = Intervals()
        _list = _intervalFile.read()
        self._setup_timers(_list)

    @staticmethod
    def _open_pins_dialogbox():
        configDialogBox.PinsDialogBox.get_data()

    def _open_intervals_dialogbox(self):
        _ok = configDialogBox.IntervalsDialogBox.get_data()
        if _ok:
            _intervalFile = Intervals()
            _list = _intervalFile.read()
            self._setup_timers(_list)

    def _open_standard_dialogbox(self):
        _ok = configDialogBox.StandardDialogBox.get_data()
        if _ok:
            _standardFile = Standard()
            _list = _standardFile.read()
            self._myTabComponents.set_font_size(int(_list[0]))
            self._myTabSensors.set_font_size(int(_list[0]))
            self._myTabSensors.set_sensor_threshold(int(_list[1]))

    def _request_sensor_data_first_time(self):
        self._myTabSensors.timeout_start_timer()

    def _setup_timers(self, l):
        self._myTabComponents.set_timer_interval(int(l[0]))
        self._myTabSensors.set_timer_interval(int(l[1]), int(l[2]), int(l[3]))
        self._statusBarTimeElapsed = self._get_time(self._myTabSensors.get_timer_interval())
        self._statusBarTimeElapsed.restart()

    def _start_timers(self):
        self._myTabControl.read_structure_from_database()
        self._myTabComponents.read_structure_from_database()
        self._myTabComponents.init_control_state()
        self._myTabComponents.timer_start()
        self._myTabSensors.timer_start()
        self._statusBarTimeElapsed = self._get_time(self._myTabSensors.get_timer_interval())
        self._statusBarTimer.start(1000)
        self._statusBarTimeElapsed.start()

    def _restart_statusbar_time_elapsed(self):
        self._statusBarTimeElapsed.restart()

    # -------------------------------------TOOLBARS-----------------------------------------------

    def _setup_general_toolbar(self):
        _logClearAction = QtGui.QAction(QtGui.QIcon('images/standardToolBar/clear.png'), 'Limpiar Log', self)
        _logClearAction.triggered.connect(self._toolbutton_log_clear_action)
        _dataResetMinMaxAction = QtGui.QAction(QtGui.QIcon('images/standardToolBar/reset.png'),
                                               'Resetear Todos los Maximos y Minimos', self)
        _dataResetMinMaxAction.triggered.connect(self._toolbutton_data_reset_min_max_action)

        self._standardToolBar.addAction(_logClearAction)
        self._standardToolBar.addAction(_dataResetMinMaxAction)

    # -------------------------------------TOOL_BUTTONS-----------------------------------------------

    def _toolbutton_log_clear_action(self):
        self._myLog.clear()

    def _toolbutton_data_reset_min_max_action(self):
        reply = QtGui.QMessageBox().question(self, 'Message',
                                             'Estas seguro que quieres resetear todos los Maximos y Minimos?',
                                             QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self._myTabSensors.reset_all_min_max()

    # ----------------------------------------------------------------------

    def _print_normal_message(self, msg):
        self._myLog.print_normal_message(msg)

    def _print_alert_message(self, msg):
        self._myLog.print_alert_message(msg)

    def _update_statusbar(self):
        _elapsedTime = self._get_time(self._myTabSensors.get_timer_interval() - self._statusBarTimeElapsed.elapsed())
        self.statusBar().showMessage('Proxima lectura de sensores en: ' + _elapsedTime.toString('HH:mm:ss'))

    @staticmethod
    def _get_time(milliseconds):
        _secs = milliseconds / 1000
        _mins = (_secs / 60) % 60
        _hours = (_secs / 3600)
        _secs %= 60
        return QtCore.QTime(_hours, _mins, _secs)

    # ------------------------------------------------------------------------------------

    def _control_update_sensor(self, s_name, s_type, s_data):
        self._myTabControl.update_sensor_data(s_name, s_type, s_data)

    def _control_update_components(self, c_name, c_type, c_state):
        self._myTabControl.update_component_state(c_name, c_type, c_state)

    def _control_update_name_components(self, previous_name, new_name, c_type):
        self._myTabControl.update_component_name(previous_name, new_name, c_type)

    def _control_update_name_sensors(self, previous_name, new_name, s_type):
        self._myTabControl.update_sensor_name(previous_name, new_name, s_type)

    def closeEvent(self, event):
        if not self._mySerialUSB.error:
            reply = QtGui.QMessageBox().question(self, 'Message',
                                                 'Estas seguro que quieres cerrar el programa?',
                                                 QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                # self._mySerialUSB.close()
                event.accept()
            else:
                event.ignore()
