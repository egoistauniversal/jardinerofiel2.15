from PyQt4 import QtGui
from PyQt4 import QtCore
from dialog import sensorDialogBox, graphDialogBox
from misc import external, timeouts, custom, graphics
import math


class TabSensors(QtGui.QWidget):
    sensorUpdateControlNameSignal = QtCore.pyqtSignal(str, str, str)
    sensorRestartStatusBarTimeElapsed = QtCore.pyqtSignal()
    sensorSaveLastMinuteSignal = QtCore.pyqtSignal()
    sensorPrintNormalMessage = QtCore.pyqtSignal(str)
    sensorPrintAlertMessage = QtCore.pyqtSignal(str)
    controlUpdateSignal = QtCore.pyqtSignal(str, str, str)

    def __init__(self, db, serial):
        super(TabSensors, self).__init__()
        self._model = QtGui.QStandardItemModel(0, 11, self)
        self._myDataBase = db
        self._mySerial = serial
        self._myTreeView = custom.TreeView()
        self._primaryTimer = QtCore.QTimer(self)
        self._secondaryTimer = QtCore.QTimer(self)
        self._model.appendRow(QtGui.QStandardItem('Sensores'))
        self._myTimeouts = timeouts.Sensors(self._model)
        self._threshold = None
        self._myGraphics = graphics.Graphics(self._myDataBase)
        self._setup()

    def _setup(self):
        self._myTreeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._setup_model()
        self._setup_layouts()
        self._setup_connections()
        self._tree_expand_all()

    def _setup_model(self):
        self._model.setHeaderData(0, QtCore.Qt.Horizontal, 'Nombre')
        self._model.setHeaderData(1, QtCore.Qt.Horizontal, 'Tipo')
        self._model.setHeaderData(2, QtCore.Qt.Horizontal, 'Dato Actual')
        self._model.setHeaderData(3, QtCore.Qt.Horizontal, 'Minimo')
        self._model.setHeaderData(4, QtCore.Qt.Horizontal, 'Hora')
        self._model.setHeaderData(5, QtCore.Qt.Horizontal, 'Fecha')
        self._model.setHeaderData(6, QtCore.Qt.Horizontal, 'Maximo')
        self._model.setHeaderData(7, QtCore.Qt.Horizontal, 'Hora')
        self._model.setHeaderData(8, QtCore.Qt.Horizontal, 'Fecha')
        self._model.setHeaderData(9, QtCore.Qt.Horizontal, 'Pin')
        self._model.setHeaderData(10, QtCore.Qt.Horizontal, 'Programado')
        self._myTreeView.setModel(self._model)

    def _setup_layouts(self):
        _treeViewLayout = QtGui.QHBoxLayout()
        _treeViewLayout.addWidget(self._myTreeView)
        self.setLayout(_treeViewLayout)

    def _setup_connections(self):
        self._myTreeView.customContextMenuRequested.connect(self._open_context_menu)
        self._myTimeouts.timeoutSensorReadSignal.connect(self._serial_send_data)
        self._myTimeouts.timeoutSensorSaveLastMinuteSignal.connect(self._save_last_minute)
        self._primaryTimer.timeout.connect(self.timeout_start_timer)
        self._secondaryTimer.timeout.connect(self._serial_get_data)

    def read_structure_from_database(self):
        self._myDataBase.read_sensor_structure(self._model)

    # -----------------------------------ADD-------------------------------------------------------

    def _add_first_level_item(self):
        # Get data from Dialog box
        name, ok = sensorDialogBox.SensorFirstLevelItemDialog.get_data('Anadir')
        if ok:
            _myExternal = external.Generals()
            _myExternal.sensor_add_first_level_item(self._model.item(0, 0), name)
            self._myDataBase.sensor_group_table_insert_node(str(name))

    def _add_second_level_item(self, index, sensor_type='1'):
        name, pin, ok = sensorDialogBox.SecondLevelItemSensorDialog.get_data('Anadir sensor')
        if ok:
            item = index.model().itemFromIndex(index)
            _myExternal = external.Generals()
            _myExternal.sensor_add_second_level_item(item, name, sensor_type, pin, 1)
            group_name = item.data(QtCore.Qt.DisplayRole).toString()
            self._myDataBase.sensor_table_insert_row(str(group_name), str(name), str(sensor_type), str(pin))
            # if sensor_type is Temperature and Humidity (DHT11)
            if sensor_type == '2':
                _myExternal.sensor_add_second_level_item(item, name, '3', pin, 1)
                self._myDataBase.sensor_table_insert_row(str(group_name), str(name), '3', str(pin))
            elif sensor_type == '4':
                _myExternal.sensor_add_second_level_item(item, name, '5', pin, 1)
                self._myDataBase.sensor_table_insert_row(str(group_name), str(name), '5', str(pin))

    # -------------------------------------Modify---------------------------------------------

    def _modify_first_level_item(self, index):
        _nameStr = index.model().itemFromIndex(index).data(QtCore.Qt.DisplayRole).toString()
        name, ok = sensorDialogBox.SensorFirstLevelItemDialog.get_data('Modificar ' + _nameStr, name=_nameStr)
        if ok:
            _myExternal = external.Generals()
            _myExternal.sensor_modify_first_level_item(index.model().itemFromIndex(index), name)
            self._myDataBase.sensor_group_table_modify_node(str(_nameStr), str(name))

    def _modify_second_level_items(self, index):
        _nameStr = index.parent().child(index.row(), 0).data(QtCore.Qt.DisplayRole).toString()
        _typeStr = index.model().itemFromIndex(index.parent().child(index.row(), 1)).get_tag()
        _pinStr = index.parent().child(index.row(), 9).data(QtCore.Qt.DisplayRole).toString()
        name, pin, ok = sensorDialogBox.SecondLevelItemSensorDialog.get_data('Modificar sensor ' + _nameStr,
                                                                             name=_nameStr, pin=_pinStr)
        if ok:
            _myExternal = external.Generals()
            if _pinStr != pin:
                _myExternal.sensor_clear_row_item(index)
            _myExternal.sensor_modify_second_level_item(index, name, pin)

            if _typeStr == '2':
                index = index.parent().child(index.row() + 1, 0)
                _myExternal.sensor_modify_second_level_item(index, name, pin)
                # if _pinStr != pin:
                # _myExternal.sensor_clear_row_item(index)
            elif _typeStr == '3':
                index = index.parent().child(index.row() - 1, 0)
                _myExternal.sensor_modify_second_level_item(index, name, pin)
                # if _pinStr != pin:
                # _myExternal.sensor_clear_row_item(index)

            if _typeStr == '4':
                index = index.parent().child(index.row() + 1, 0)
                _myExternal.sensor_modify_second_level_item(index, name, pin)

            elif _typeStr == '5':
                index = index.parent().child(index.row() - 1, 0)
                _myExternal.sensor_modify_second_level_item(index, name, pin)

            self._myDataBase.sensor_table_modify_row(str(_nameStr), str(name), str(pin))
            if _nameStr != name:
                self._update_control_name(_nameStr, name, _typeStr)

    # -------------------------------------Reset---------------------------------------------

    def _reset_single_row_min_max(self, index):
        _name = index.parent().child(index.row(), 0).data(QtCore.Qt.DisplayRole).toString()
        yes = QtGui.QMessageBox().question(self, 'Resetear Min y Max',
                                           'Estas seguro que quieres resetear los maximos y minimos del sensor ' +
                                           _name + '???',
                                           QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if yes == QtGui.QMessageBox.Yes:
            _myExternal = external.Generals()
            _myExternal.sensor_reset_single_row_min_max(index)

    def _reset_single_row(self, index):
        _name = index.parent().child(index.row(), 0).data(QtCore.Qt.DisplayRole).toString()
        yes = QtGui.QMessageBox().question(self, 'Resetear Fila',
                                           'Estas seguro que quieres resetear el sensor ' + _name + '???',
                                           QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if yes == QtGui.QMessageBox.Yes:
            _myExternal = external.Generals()
            _myExternal.sensor_clear_row_item(index)

    # -------------------------------------Remove---------------------------------------------

    def _remove_node(self, index):
        yes = QtGui.QMessageBox().question(self, 'Eliminar Nodo', 'Estas seguro que quieres eleminar este Nodo???',
                                           QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if yes == QtGui.QMessageBox.Yes:
            level = self._get_item_level(index)
            if level == 1:
                self._remove_first_level_node(index)
            else:
                self._remove_second_level_node(index)

    def _remove_first_level_node(self, index):
        _nameStr = index.model().itemFromIndex(index).data(QtCore.Qt.DisplayRole).toString()
        parent = index.model().itemFromIndex(index).parent()
        # Remove from model
        parent.removeRow(index.row())
        # Remove sensor from database
        _pinList = self._myDataBase.sensor_group_table_delete_node(str(_nameStr))
        for _pin in _pinList:
            # As the pin is going to be cleared in the arduino the state can be anything
            # and it's not going to be used on the arduino
            self._serial_clear_pin(_pin)

    def _remove_second_level_node(self, index):
        _nameStr = index.parent().child(index.row(), 0).data(QtCore.Qt.DisplayRole).toString()
        _typeStr = index.model().itemFromIndex(index.parent().child(index.row(), 1)).get_tag()
        _pinStr = index.parent().child(index.row(), 9).data(QtCore.Qt.DisplayRole).toString()
        parent = index.model().itemFromIndex(index).parent()
        _indexRow = index.row()
        # Remove from model
        parent.removeRow(_indexRow)
        if _typeStr == '2':
            parent.removeRow(_indexRow)
        elif _typeStr == '3':
            parent.removeRow(_indexRow - 1)

        parent.removeRow(_indexRow)
        if _typeStr == '4':
            parent.removeRow(_indexRow)
        elif _typeStr == '5':
            parent.removeRow(_indexRow - 1)

        # Remove sensor from database
        self._myDataBase.sensor_table_delete_row(str(_nameStr))
        self._serial_clear_pin(_pinStr)

    # ---------------------------------------ACTIVATE / DEACTIVATE---------------------------------------------

    def _activate_deactivate_second_level_node(self, index):
        _name = index.parent().child(index.row(), 0).data(QtCore.Qt.DisplayRole).toString()
        if index.model().itemFromIndex(index.parent().child(index.row(), 10)).checkState():
            yes = QtGui.QMessageBox().question(self, 'Desactivar Nodo',
                                               'Estas seguro que quieres desactivar la programacion del sensor ' +
                                               _name + '???',
                                               QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if yes == QtGui.QMessageBox.Yes:
                index.model().itemFromIndex(index.parent().child(index.row(), 10)).setCheckState(QtCore.Qt.Unchecked)
                self._myDataBase.sensor_table_modify_active_row(str(_name), 0)
                _type = index.model().itemFromIndex(index.parent().child(index.row(), 1)).get_tag()
                if _type == '2':
                    index.model().itemFromIndex(index.parent().child(index.row() + 1, 10)).setCheckState(
                        QtCore.Qt.Unchecked)
                elif _type == '3':
                    index.model().itemFromIndex(index.parent().child(index.row() - 1, 10)).setCheckState(
                        QtCore.Qt.Unchecked)

                if _type == '4':
                    index.model().itemFromIndex(index.parent().child(index.row() + 1, 10)).setCheckState(
                        QtCore.Qt.Unchecked)
                elif _type == '5':
                    index.model().itemFromIndex(index.parent().child(index.row() - 1, 10)).setCheckState(
                        QtCore.Qt.Unchecked)
        else:
            index.model().itemFromIndex(index.parent().child(index.row(), 10)).setCheckState(QtCore.Qt.Checked)
            self._myDataBase.sensor_table_modify_active_row(str(_name), 1)
            _type = index.model().itemFromIndex(index.parent().child(index.row(), 1)).get_tag()
            if _type == '2':
                index.model().itemFromIndex(index.parent().child(index.row() + 1, 10)).setCheckState(QtCore.Qt.Checked)
            elif _type == '3':
                index.model().itemFromIndex(index.parent().child(index.row() - 1, 10)).setCheckState(QtCore.Qt.Checked)

            if _type == '4':
                index.model().itemFromIndex(index.parent().child(index.row() + 1, 10)).setCheckState(QtCore.Qt.Checked)
            elif _type == '5':
                index.model().itemFromIndex(index.parent().child(index.row() - 1, 10)).setCheckState(QtCore.Qt.Checked)

    # --------------------------------------- Graphics---------------------------------------------

    def _graph_sensor(self, index):
        _nameStr = index.parent().child(index.row(), 0).data(QtCore.Qt.DisplayRole).toString()
        _typeStr = index.model().itemFromIndex(index.parent().child(index.row(), 1)).get_tag()
        _days, ok = graphDialogBox.XAxisRangeDialogBox.get_data(1)
        if ok:
            self._myGraphics.update_graphic(str(_nameStr), _typeStr, _days)
            self._myGraphics.setGeometry(QtCore.QRect(100, 100, 400, 200))
            self._myGraphics.showMaximized()

    # --------------------------------------- Context Menu---------------------------------------------

    def _open_context_menu(self, point):
        _currentIndex = self._myTreeView.indexAt(point)
        # if it's been clicked on any element from the state
        if _currentIndex.isValid():
            # Get item's level
            level = self._get_item_level(_currentIndex)
            if level == 0:
                self._show_root_context_menu(point)
            elif level == 1:
                self._show_first_level_context_menu(point, _currentIndex)
            elif level == 2:
                self._show_second_level_context_menu(point, _currentIndex)

    def _show_root_context_menu(self, point):
        _mainContextMenu = QtGui.QMenu()
        _mainContextMenu.addAction('Anadir Grupo', self._add_first_level_item)
        _mainContextMenu.exec_(self.mapToGlobal(point))

    def _show_first_level_context_menu(self, point, index):
        _custom = custom.ContextMenuOptions()
        _subMenuAnadir = QtGui.QMenu()
        _subMenuAnadir.setTitle('Anadir')
        _subMenuAnadir.addAction(_custom.get_sensor_context_menu_name_options(1),
                                 lambda: self._add_second_level_item(index, sensor_type='1'))

        # The DHT11 sensor will have two sensor_types : 2 and 3 as this one can read temperature and humidity
        _subMenuAnadir.addAction(_custom.get_sensor_context_menu_name_options(2),
                                 lambda: self._add_second_level_item(index, sensor_type='2'))

        _subMenuAnadir.addAction(_custom.get_sensor_context_menu_name_options(4),
                                 lambda: self._add_second_level_item(index, sensor_type='4'))

        _subMenuAnadir.addAction(_custom.get_sensor_context_menu_name_options(6),
                                 lambda: self._add_second_level_item(index, sensor_type='6'))

        _mainContextMenu = QtGui.QMenu()
        _mainContextMenu.addMenu(_subMenuAnadir)
        _mainContextMenu.addAction('Modificar', lambda: self._modify_first_level_item(index))
        _mainContextMenu.addAction('Eliminar', lambda: self._remove_node(index))
        _mainContextMenu.exec_(self.mapToGlobal(point))

    def _show_second_level_context_menu(self, point, index):
        _mainContextMenu = QtGui.QMenu()
        _mainContextMenu.addAction('Grafico', lambda: self._graph_sensor(index))
        _mainContextMenu.addAction('Resetear Min y Max Fila', lambda: self._reset_single_row_min_max(index))
        _mainContextMenu.addAction('Resetear Fila', lambda: self._reset_single_row(index))
        _mainContextMenu.addSeparator()
        _mainContextMenu.addAction('Modificar', lambda: self._modify_second_level_items(index))
        _mainContextMenu.addAction('Eliminar', lambda: self._remove_node(index))
        _mainContextMenu.addSeparator()
        if index.model().itemFromIndex(index.parent().child(index.row(), 10)).checkState():
            _mainContextMenu.addAction('Desactivar Programacion',
                                       lambda: self._activate_deactivate_second_level_node(index))
        else:
            _mainContextMenu.addAction('Activar Programacion',
                                       lambda: self._activate_deactivate_second_level_node(index))
        _mainContextMenu.exec_(self.mapToGlobal(point))

    # ------------------------------------SERIAL-------------------------------------------

    def _serial_send_data(self, s_pin, s_type):
        _data = '2' + '$' + '1' + '$' + str(s_pin) + '$' + str(s_type) + ';'
        self._mySerial.send_data(_data)
        self._secondaryTimer.start()

    def _serial_get_data(self):
        self._secondaryTimer.stop()
        _value = self._mySerial.read_data()
        self.update_data(self._myTimeouts.get_parent(), self._myTimeouts.get_row(), _value)

    def _serial_clear_pin(self, s_pin):
        _data = '2' + '$' + '3' + '$' + str(s_pin) + '$' + '0' + ';'
        self._mySerial.send_data(_data)

    # ------------------------------------UPDATE-------------------------------------------

    def update_data(self, parent, row, current_value):
        try:
            if parent:
                _name = parent.child(row, 0).data(QtCore.Qt.DisplayRole).toString()
                _type = parent.child(row, 1).get_tag()
                _previous_value = parent.child(row, 2).data(QtCore.Qt.DisplayRole).toString()
                if _previous_value.size() != 0:
                    threshold = float(current_value) - float(_previous_value)
                    if math.fabs(threshold) < self._threshold:
                        parent.child(row, 2).setData(current_value, QtCore.Qt.DisplayRole)
                        # Send data to TabControl
                        self.controlUpdateSignal.emit(_name, _type, current_value)
                        self._save_to_database(parent, row, current_value)
                        self._update_min(parent, row, current_value)
                        self._update_max(parent, row, current_value)
                    else:
                        # _name = parent.child(row, 0).data(QtCore.Qt.DisplayRole).toString()
                        self.sensorPrintAlertMessage.emit('ATENCION, posible error de lectura del sensor: ' + _name)
                        self.sensorPrintAlertMessage.emit('Valor actual: ' + current_value +
                                                          ' Valor previo: ' + _previous_value)
                        self.sensorPrintAlertMessage.emit('Valor: ' + current_value + ' ignorado')
                else:
                    if float(current_value) != 85 and float(current_value) != -127:
                        parent.child(row, 2).setData(current_value, QtCore.Qt.DisplayRole)
                        self._update_min(parent, row, current_value)
                        self._update_max(parent, row, current_value)
                        self._save_to_database(parent, row, current_value)
                    else:
                        # _name = parent.child(row, 0).data(QtCore.Qt.DisplayRole).toString()
                        self.sensorPrintAlertMessage.emit('ATENCION, posible error de lectura del sensor: ' + _name)
                        self.sensorPrintAlertMessage.emit('Valor: ' + current_value + ' ignorado')
        except Exception, e:
            self.sensorPrintAlertMessage.emit('Error al actualizar datos: ' + e.args[0])

    def _update_min(self, parent, row, value):
        _minStr = parent.child(row, 3).data(QtCore.Qt.DisplayRole).toString()
        if _minStr.size() > 0:
            if float(value) < float(_minStr):
                parent.child(row, 3).setData(value, QtCore.Qt.DisplayRole)
                self._update_min_date_time(parent, row)
        else:
            parent.child(row, 3).setData(value, QtCore.Qt.DisplayRole)
            self._update_min_date_time(parent, row)

    def _update_max(self, parent, row, value):
        _maxStr = parent.child(row, 6).data(QtCore.Qt.DisplayRole).toString()
        if _maxStr.size() > 0:
            if float(value) > float(_maxStr):
                parent.child(row, 6).setData(value, QtCore.Qt.DisplayRole)
                self._update_max_date_time(parent, row)
        else:
            parent.child(row, 6).setData(value, QtCore.Qt.DisplayRole)
            self._update_max_date_time(parent, row)

    @staticmethod
    def _update_min_date_time(parent, row):
        _currentDatetime = QtCore.QDateTime().currentDateTime()
        x = _currentDatetime.toString("HH:mm:ss")
        parent.child(row, 4).setData(x, QtCore.Qt.DisplayRole)
        x = _currentDatetime.toString("dd-MM-yyyy")
        parent.child(row, 5).setData(x, QtCore.Qt.DisplayRole)

    @staticmethod
    def _update_max_date_time(parent, row):
        _currentDatetime = QtCore.QDateTime().currentDateTime()
        x = _currentDatetime.toString("HH:mm:ss")
        parent.child(row, 7).setData(x, QtCore.Qt.DisplayRole)
        x = _currentDatetime.toString("dd-MM-yyyy")
        parent.child(row, 8).setData(x, QtCore.Qt.DisplayRole)

    def _save_last_minute(self):
        self.sensorSaveLastMinuteSignal.emit()
        self._myDataBase.check_file_size()

    # -------------------------------------------------------------------------------------------------

    def _save_to_database(self, parent, row, value):
        _name = parent.child(row, 0).data(QtCore.Qt.DisplayRole).toString()
        _type = parent.child(row, 1).get_tag()
        _currentDatetime = QtCore.QDateTime().currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        self._myDataBase.data_table_insert_row(str(_name), str(_type), str(_currentDatetime), float(value))

    # -----------------------------------------------------------------------------------
    @staticmethod
    def _get_item_level(index):
        parent = index.model().itemFromIndex(index).parent()
        count = 0
        while parent:
            count += 1
            parent = parent.parent()
        return count

    def timer_start(self):
        self._primaryTimer.start()

    def timeout_start_timer(self):
        self.sensorRestartStatusBarTimeElapsed.emit()
        self._myTimeouts.start_timer()

    def reset_all_min_max(self):
        _myExternal = external.Generals()
        _myExternal.sensor_reset_all_min_max(self._model)

    def set_timer_interval(self, interval_a, interval_b, interval_c):
        self._primaryTimer.setInterval(interval_a)
        self._myTimeouts.set_timer_interval(interval_b)
        self._secondaryTimer.setInterval(interval_c)

    def get_timer_interval(self):
        return self._primaryTimer.interval()

    def _tree_expand_all(self):
        # TODO learn how to expand the tree on start up
        self._myTreeView.expandAll()
        _rootItem = self._model.item(0, 0)
        for i in xrange(_rootItem.rowCount()):
            self._myTreeView.setExpanded(_rootItem.child(i, 0).index(), True)

    def set_font_size(self, size):
        _treeViewFont = QtGui.QFont()
        _treeViewFont.setPixelSize(size)
        self._myTreeView.setFont(_treeViewFont)

    def set_sensor_threshold(self, threshold):
        self._threshold = threshold

    def _update_control_name(self, previous_name, new_name, c_type):
        self.sensorUpdateControlNameSignal.emit(previous_name, new_name, c_type)
