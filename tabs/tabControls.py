from PyQt4 import QtGui, QtCore
from dialog import controlDialogBox
from misc import external, timeouts, custom


class TabControl(QtGui.QWidget):
    def __init__(self, db, serial):
        super(TabControl, self).__init__()
        self._model = QtGui.QStandardItemModel(0, 13, self)
        self._myDataBase = db
        self._mySerial = serial
        self._myTreeView = custom.TreeView()
        self._myTimeouts = timeouts.Controls()
        self._setup()

    def _setup(self):
        self._setup_layout()
        self._setup_model()
        self._setup_connections()
        self._myTreeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

    def _setup_layout(self):
        _treeViewLayout = QtGui.QHBoxLayout()
        _treeViewLayout.addWidget(self._myTreeView)
        self.setLayout(_treeViewLayout)

    def _setup_model(self):
        self._model.appendRow(QtGui.QStandardItem('Controles'))
        self._model.setHeaderData(0, QtCore.Qt.Horizontal, 'Control')
        self._model.setHeaderData(1, QtCore.Qt.Horizontal, 'Nombre')
        self._model.setHeaderData(2, QtCore.Qt.Horizontal, 'Tipo')
        self._model.setHeaderData(3, QtCore.Qt.Horizontal, 'Dato')
        self._model.setHeaderData(4, QtCore.Qt.Horizontal, 'Operador')
        self._model.setHeaderData(5, QtCore.Qt.Horizontal, 'Objetivo')
        self._model.setHeaderData(6, QtCore.Qt.Horizontal, 'Dispositivo')
        self._model.setHeaderData(7, QtCore.Qt.Horizontal, 'Pausa')
        self._model.setHeaderData(8, QtCore.Qt.Horizontal, 'Restante')
        self._model.setHeaderData(9, QtCore.Qt.Horizontal, 'Estado')
        self._model.setHeaderData(10, QtCore.Qt.Horizontal, 'Protocolo')
        self._model.setHeaderData(11, QtCore.Qt.Horizontal, 'Pin')
        self._model.setHeaderData(12, QtCore.Qt.Horizontal, 'Programado')
        self._myTreeView.setModel(self._model)

    def _setup_connections(self):
        self._myTreeView.customContextMenuRequested.connect(self._open_context_menu)
        self._myDataBase.dbControlArduinoSignal.connect(self._serial_data_from_database)
        self._myTimeouts.controlChangeStateSignal.connect(self._serial_change_arduino_state_pin)

    # -------------------------------------------ADD------------------------------------------------------------

    def _add_first_level_item(self):
        # Get data from Dialog box
        _name, _ok = controlDialogBox.FirstLevelItemDialog.get_data('Anadir Grupo')
        if _ok:
            _myExternal = external.Generals()
            _myExternal.sensor_add_first_level_item(self._model.item(0, 0), _name)
            self._myDataBase.control_group_table_insert_node(str(_name))

    def _add_second_level_item_sensor(self, index):
        _myExternal = external.Generals()
        _sensorName, _sensorType, _operator, _goalValue, _deviceName, _pause, _protocol, _pin, _ok = \
            controlDialogBox.SecondLevelItemSensorDialog.get_data('Anadir control sensor')
        if _ok:
            _controlType = '1'
            item = index.model().itemFromIndex(index)
            group_name = item.data(QtCore.Qt.DisplayRole).toString()
            _id = self._myDataBase.control_table_insert_row(str(group_name), str(_controlType), str(_sensorName),
                                                            str(_sensorType), str(_operator), str(_goalValue),
                                                            str(_deviceName), str(_pause), str(_protocol), str(_pin), 1)
            if _id != -1:
                _myExternal.control_add_second_level_item_sensor(item, _controlType, _sensorName, _sensorType,
                                                                 _operator, _goalValue, _deviceName, _pause, _protocol,
                                                                 _pin, 1, _id)
                self._serial_setup_arduino_pin(_pin, '0')

    def _add_second_level_item_component(self, index):
        _myExternal = external.Generals()
        _componentName, _componentType, _operator, _goalState, _deviceName, _pause, _protocol, _pin, _ok = \
            controlDialogBox.SecondLevelItemComponentDialog.get_data('Anadir control componente')
        if _ok:
            _controlType = '2'
            item = index.model().itemFromIndex(index)
            group_name = item.data(QtCore.Qt.DisplayRole).toString()
            _id = self._myDataBase.control_table_insert_row(str(group_name), str(_controlType), str(_componentName),
                                                            str(_componentType), str(_operator), str(_goalState),
                                                            str(_deviceName), str(_pause), str(_protocol), str(_pin), 1)
            if _id != -1:
                _myExternal.control_add_second_level_item_sensor(item, _controlType, _componentName, _componentType,
                                                                 _operator, _goalState, _deviceName, _pause, _protocol,
                                                                 _pin, 1, _id)
                self._serial_setup_arduino_pin(_pin, '0')

    # --------------------------------------MODIFY------------------------------------------------------------

    def _modify_first_level_item(self, index):
        _nameStr = index.model().itemFromIndex(index).data(QtCore.Qt.DisplayRole).toString()
        _name, _ok = controlDialogBox.FirstLevelItemDialog.get_data('Modificar ' + _nameStr, name=_nameStr)
        if _ok:
            index.model().itemFromIndex(index).setData(_name, QtCore.Qt.DisplayRole)
            self._myDataBase.control_group_table_modify_node(str(_nameStr), str(_name))

    def _modify_second_level_items(self, index):
        _myExternal = external.Generals()
        _controlType = index.model().itemFromIndex(index.parent().child(index.row(), 0)).get_tag()
        _xNameStr = index.parent().child(index.row(), 1).data(QtCore.Qt.DisplayRole).toString()
        _xTypeStr = index.model().itemFromIndex(index.parent().child(index.row(), 2)).get_tag()
        _operatorStr = index.parent().child(index.row(), 4).data(QtCore.Qt.DisplayRole).toString()
        _deviceNameStr = index.parent().child(index.row(), 6).data(QtCore.Qt.DisplayRole).toString()
        _pauseStr = index.parent().child(index.row(), 7).data(QtCore.Qt.DisplayRole).toString()
        _protocolStr = index.parent().child(index.row(), 10).data(QtCore.Qt.DisplayRole).toString()
        _pinStr = index.parent().child(index.row(), 11).data(QtCore.Qt.DisplayRole).toString()

        if _controlType == '1':
            _goalValueStr = index.parent().child(index.row(), 5).data(QtCore.Qt.DisplayRole).toString()
            _xName, _xType, _operator, _goalValue, _deviceName, _pause, _protocol, _pin, _ok = \
                controlDialogBox.SecondLevelItemSensorDialog.get_data('Modificar ' + _xNameStr, sensor_name=_xNameStr,
                                                                      sensor_type=_xTypeStr, operator=_operatorStr,
                                                                      goal_value=_goalValueStr,
                                                                      device_name=_deviceNameStr, pause=_pauseStr,
                                                                      protocol=_protocolStr, pin=_pinStr)
            if _ok:
                _id = index.model().itemFromIndex(index.parent().child(index.row(), 0)).get_id()
                self._myDataBase.control_table_modify_row(_id, str(_xName), str(_xType), str(_operator),
                                                          str(_goalValue), str(_deviceName), str(_pause),
                                                          str(_protocol), str(_pin))
                _myExternal.control_modify_second_level_item_sensor(index, _xName, _xType, _operator, _goalValue,
                                                                    _deviceName, _pause, _protocol, _pin)

        elif _controlType == '2':
            _goalStateStr = index.model().itemFromIndex(index.parent().child(index.row(), 5)).get_tag()
            _xName, _xType, _operator, _goalState, _deviceName, _pause, _protocol, _pin, _ok = \
                controlDialogBox.SecondLevelItemComponentDialog.get_data('Modificar ' + _xNameStr,
                                                                         sensor_name=_xNameStr, sensor_type=_xTypeStr,
                                                                         operator=_operatorStr,
                                                                         goal_value=_goalStateStr,
                                                                         device_name=_deviceNameStr, pause=_pauseStr,
                                                                         protocol=_protocolStr, pin=_pinStr)
            if _ok:
                _id = index.model().itemFromIndex(index.parent().child(index.row(), 0)).get_id()
                self._myDataBase.control_table_modify_row(_id, str(_xName), str(_xType), str(_operator),
                                                          str(_goalState), str(_deviceName), str(_pause),
                                                          str(_protocol), str(_pin))
                _myExternal.control_modify_second_level_item_component(index, _xName, _xType, _operator, _goalState,
                                                                       _deviceName, _pause, _protocol, _pin)

    # ----------------------------------------------REMOVE--------------------------------------------------

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
        name = index.model().itemFromIndex(index).data(QtCore.Qt.DisplayRole).toString()
        parent = index.model().itemFromIndex(index).parent()
        # Remove group from model
        parent.removeRow(index.row())
        # Remove group from database and return a list of pins to delete on the Arduino
        _pinList = self._myDataBase.control_group_table_delete_node(str(name))
        for _pin in _pinList:
            # As the pin is going to be cleared in the arduino the state can be anything
            self._serial_clear_arduino_pin(_pin, '0')

    def _remove_second_level_node(self, index):
        _control_id = index.model().itemFromIndex(index.parent().child(index.row(), 0)).get_id()
        parent = index.model().itemFromIndex(index).parent()
        # Remove group from model
        parent.removeRow(index.row())
        # Remove group from database
        _pin = self._myDataBase.control_table_delete_row(_control_id)
        # As the pin is going to be cleared in the arduino the state can be anything
        self._serial_clear_arduino_pin(_pin, '0')

    # ---------------------------------------ACTIVATE / DEACTIVATE---------------------------------------------

    def _activate_deactivate_second_level_node(self, index):
        _control_id = index.model().itemFromIndex(index.parent().child(index.row(), 0)).get_id()
        _xName = index.parent().child(index.row(), 1).data(QtCore.Qt.DisplayRole).toString()
        _deviceName = index.parent().child(index.row(), 6).data(QtCore.Qt.DisplayRole).toString()

        if index.model().itemFromIndex(index.parent().child(index.row(), 12)).checkState():
            yes = QtGui.QMessageBox().question(self, 'Desactivar Nodo',
                                               'Estas seguro que quieres desactivar la programacion del ' +
                                               _xName + ' conectado al dispositivo ' + _deviceName + '?',
                                               QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if yes == QtGui.QMessageBox.Yes:
                index.model().itemFromIndex(index.parent().child(index.row(), 12)).setCheckState(QtCore.Qt.Unchecked)
                self._myDataBase.control_table_modify_active_row(_control_id, 0)
        else:
            index.model().itemFromIndex(index.parent().child(index.row(), 12)).setCheckState(QtCore.Qt.Checked)
            self._myDataBase.control_table_modify_active_row(_control_id, 1)
            _xType = index.model().itemFromIndex(index.parent().child(index.row(), 2)).get_tag()
            _controlType = index.model().itemFromIndex(index.parent().child(index.row(), 0)).get_tag()
            if _controlType == '1':
                _data = index.parent().child(index.row(), 3).data(QtCore.Qt.DisplayRole).toString()
                self.update_sensor_data(_xName, _xType, _data)
            elif _controlType == '2':
                _state = index.model().itemFromIndex(index.parent().child(index.row(), 3)).get_tag()
                self.update_component_state(_xName, _xType, _state)

    def _switch_on_off_second_level_node(self, index):
        _state = index.model().itemFromIndex(index.parent().child(index.row(), 9)).get_tag()
        _pin = index.parent().child(index.row(), 11).data(QtCore.Qt.DisplayRole).toString()
        if _state == '0':
            index.model().itemFromIndex(index.parent().child(index.row(), 9)).set_tag('1')
            self._serial_change_arduino_state_pin(_pin, '1')
        else:
            index.model().itemFromIndex(index.parent().child(index.row(), 9)).set_tag('0')
            self._serial_change_arduino_state_pin(_pin, '0')

    # ---------------------------------------Context Menu---------------------------------------------

    def _open_context_menu(self, point):
        _currentIndex = self._myTreeView.indexAt(point)
        # if it's been clicked on any element from the state AND if the item has parent then...
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
        _subMenuAnadir.addAction(_custom.get_control_context_menu_name_options(1),
                                 lambda: self._add_second_level_item_sensor(index))
        _subMenuAnadir.addAction(_custom.get_control_context_menu_name_options(2),
                                 lambda: self._add_second_level_item_component(index))

        _mainContextMenu = QtGui.QMenu()
        _mainContextMenu.addMenu(_subMenuAnadir)
        _mainContextMenu.addAction('Modificar', lambda: self._modify_first_level_item(index))
        _mainContextMenu.addAction('Eliminar', lambda: self._remove_node(index))
        _mainContextMenu.exec_(self.mapToGlobal(point))

    def _show_second_level_context_menu(self, point, index):
        _mainContextMenu = QtGui.QMenu()
        _mainContextMenu.addAction('Modificar', lambda: self._modify_second_level_items(index))
        _mainContextMenu.addAction('Eliminar', lambda: self._remove_node(index))
        _mainContextMenu.addSeparator()
        if index.model().itemFromIndex(index.parent().child(index.row(), 12)).checkState():
                _mainContextMenu.addAction('Desactivar Programacion',
                                           lambda: self._activate_deactivate_second_level_node(index))
        else:
            _mainContextMenu.addAction('Activar Programacion',
                                       lambda: self._activate_deactivate_second_level_node(index))
            if index.model().itemFromIndex(index.parent().child(index.row(), 9)).get_tag() == '0':
                _mainContextMenu.addAction('Encender', lambda: self._switch_on_off_second_level_node(index))
            else:
                _mainContextMenu.addAction('Apagar', lambda: self._switch_on_off_second_level_node(index))
        _mainContextMenu.exec_(self.mapToGlobal(point))

    # -------------------------------------------------------------------------------

    @staticmethod
    def _get_item_level(index):
        parent = index.model().itemFromIndex(index).parent()
        count = 0
        while parent:
            count += 1
            parent = parent.parent()
        return count

    def set_font_size(self, size):
        _treeViewFont = QtGui.QFont()
        _treeViewFont.setPixelSize(size)
        self._myTreeView.setFont(_treeViewFont)

    def read_structure_from_database(self):
        self._myDataBase.read_control_structure(self._model)

    def update_sensor_data(self, s_name, s_type, s_data):
        self._myTimeouts.update_data(self._model, '1', s_name, s_type, s_data)

    def update_component_state(self, c_name, c_type, c_state):
        self._myTimeouts.update_data(self._model, '2', c_name, c_type, c_state)

    def update_component_name(self, previous_name, new_name, c_type):
        _id = self._myTimeouts.update_name(self._model, '2', previous_name, new_name, c_type)
        if _id:
            self._myDataBase.control_table_modify_name_row(_id, str(new_name))

    def update_sensor_name(self, previous_name, new_name, s_type):
        _id = self._myTimeouts.update_name(self._model, '1', previous_name, new_name, s_type)
        if _id:
            self._myDataBase.control_table_modify_name_row(_id, str(new_name))

    def _serial_data_from_database(self, c_pin, c_state):
        self._serial_setup_arduino_pin(c_pin, c_state)

    def _serial_setup_arduino_pin(self, c_pin, c_state):
        _data = '3' + '$' + '1' + '$' + str(c_pin) + '$' + str(c_state) + ';'
        self._mySerial.send_data(_data)

    def _serial_change_arduino_state_pin(self, c_pin, c_state):
        _data = '3' + '$' + '2' + '$' + str(c_pin) + '$' + str(c_state) + ';'
        self._mySerial.send_data(_data)

    def _serial_clear_arduino_pin(self, c_pin, c_state):
        _data = '3' + '$' + '3' + '$' + str(c_pin) + '$' + str(c_state) + ';'
        self._mySerial.send_data(_data)