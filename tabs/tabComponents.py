from PyQt4 import QtGui, QtCore
from dialog import componentDialogBox
from misc import external, timeouts, custom


class TabComponents(QtGui.QWidget):
    componentUpdateControlStateSignal = QtCore.pyqtSignal(str, str, str)
    componentUpdateControlNameSignal = QtCore.pyqtSignal(str, str, str)

    def __init__(self, db, serial):
        super(TabComponents, self).__init__()
        self._model = QtGui.QStandardItemModel(0, 8, self)
        self._myDataBase = db
        self._mySerial = serial
        self._myTreeView = custom.TreeView()
        self._mainTimer = QtCore.QTimer(self)
        self._myTimeouts = timeouts.Components()
        self._setup()

    def _setup(self):
        self._setup_model()
        self._setup_layouts()
        self._setup_connections()
        self._myTreeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

    def _setup_model(self):
        self._model.appendRow(QtGui.QStandardItem('Componentes'))
        self._model.setHeaderData(0, QtCore.Qt.Horizontal, 'Nombre')
        self._model.setHeaderData(1, QtCore.Qt.Horizontal, 'Tipo')
        self._model.setHeaderData(2, QtCore.Qt.Horizontal, 'Encendido')
        self._model.setHeaderData(3, QtCore.Qt.Horizontal, 'Apagado')
        self._model.setHeaderData(4, QtCore.Qt.Horizontal, 'Restante')
        self._model.setHeaderData(5, QtCore.Qt.Horizontal, 'Estado')
        self._model.setHeaderData(6, QtCore.Qt.Horizontal, 'Pin')
        self._model.setHeaderData(7, QtCore.Qt.Horizontal, 'Programado')
        self._myTreeView.setModel(self._model)

    def _setup_layouts(self):
        _treeViewLayout = QtGui.QHBoxLayout()
        _treeViewLayout.addWidget(self._myTreeView)
        self.setLayout(_treeViewLayout)

    def _setup_connections(self):
        self._myTreeView.customContextMenuRequested.connect(self._open_context_menu)
        self._myDataBase.dbComponentArduinoSignal.connect(self._serial_send_data)
        self._myTimeouts.componentChangeStateSignal.connect(self._serial_send_data)
        self._myTimeouts.componentUpdateControlStateSignal.connect(self._update_control_state)
        self._mainTimer.timeout.connect(self._time_out)

    # -------------------------------------------ADD------------------------------------------------------------

    def _add_first_level_item(self):
        # Get data from Dialog box
        _name, _ok = componentDialogBox.ComponentFirstLevelItemDialog.get_data('Anadir Componente')
        if _ok:
            self._model.item(0, 0).appendRow(QtGui.QStandardItem(_name))
            self._myDataBase.component_group_table_insert_node(str(_name))

    def _add_second_level_item_clock(self, index):
        # Get data from Dialog box
        name, _timeType, _timeOn, _timeOff, pin, ok = \
            componentDialogBox.SecondLevelItemsClockDialog.get_data('Anadir Reloj')
        if ok:
            item = index.model().itemFromIndex(index)
            _myExternal = external.Generals()
            state = _myExternal.component_add_second_level_item_clock(item, name, _timeType, _timeOn, _timeOff, pin, 1)
            group_name = item.data(QtCore.Qt.DisplayRole).toString()
            self._myDataBase.component_table_insert_row(str(group_name), str(name), str(_timeType),
                                                        str(_timeOn), str(_timeOff), str(pin), 1)
            self._mySerial.send_data('1' + '$' + '1' + '$' + str(pin) + '$' + str(state) + ';')

    def _add_second_level_items_timer(self, index):
        # Get data from Dialog box
        name, _timeType, _timeOn, _timeOff, pin, ok = \
            componentDialogBox.SecondLevelItemsTimerDialog.get_data('Anadir Temporizador')
        if ok:
            item = index.model().itemFromIndex(index)
            _myExternal = external.Generals()
            _myExternal.component_add_second_level_item_timer(item, name, _timeType, _timeOn, _timeOff, pin, 1)
            group_name = item.data(QtCore.Qt.DisplayRole).toString()
            self._myDataBase.component_table_insert_row(str(group_name), str(name), str(_timeType),
                                                        str(_timeOn), str(_timeOff), str(pin), 1)
            self._mySerial.send_data('1' + '$' + '1' + '$' + str(pin) + '$' + '1' + ';')

    # -------------------------------------Modify---------------------------------------------

    def _modify_first_level_item(self, index):
        _nameStr = index.model().itemFromIndex(index).data(QtCore.Qt.DisplayRole).toString()
        _name, _ok = componentDialogBox.ComponentFirstLevelItemDialog.get_data('Modificar ' + _nameStr, name=_nameStr)
        if _ok:
            index.model().itemFromIndex(index).setData(_name, QtCore.Qt.DisplayRole)
            self._myDataBase.component_group_table_modify_node(str(_nameStr), str(_name))

    def _modify_second_level_items(self, index):
        _nameStr = index.parent().child(index.row(), 0).data(QtCore.Qt.DisplayRole).toString()
        _timeTypeStr = index.model().itemFromIndex(index.parent().child(index.row(), 1)).get_tag()
        _timeOnStr = index.parent().child(index.row(), 2).data(QtCore.Qt.DisplayRole).toString().mid(0, 8)
        _timeOffStr = index.parent().child(index.row(), 3).data(QtCore.Qt.DisplayRole).toString().mid(0, 8)
        _pinStr = index.parent().child(index.row(), 6).data(QtCore.Qt.DisplayRole).toString()
        _xName = None
        _xTimeType = None
        if _timeTypeStr == '1':
            # _xTimeType is necessary in order to get the data from the box dialog but it is not used.
            _xName, _xTimeType, _timeOn, _timeOff, pin, ok = \
                componentDialogBox.SecondLevelItemsClockDialog.get_data('Modificar ' + _nameStr, name=_nameStr,
                                                                        time_on=_timeOnStr, time_off=_timeOffStr,
                                                                        pin=_pinStr)
            if ok:
                _external = external.Generals()
                state = _external.component_modify_second_level_item_clock(index, _xName, _timeOn, _timeOff, pin)
                self._myDataBase.component_table_modify(str(_nameStr), str(_xName), str(_timeOn), str(_timeOff),
                                                        str(pin))
                if _pinStr == pin:
                    # Set State in the Arduino
                    self._mySerial.send_data('1' + '$' + '2' + '$' + str(pin) + '$' + str(state) + ';')
                else:
                    # Clear pin in the Arduino
                    self._mySerial.send_data('1' + '$' + '3' + '$' + str(pin) + '$' + str(state) + ';')
                    # Set new pin and state in the arduino
                    self._mySerial.send_data('1' + '$' + '1' + '$' + str(pin) + '$' + str(state) + ';')
                self.componentUpdateControlStateSignal.emit(_xName, '1', state)
        elif _timeTypeStr == '2':
            # _xTimeType is necessary in order to get the data from the box dialog but it is not used.
            _xName, _xTimeType, _timeOn, _timeOff, pin, ok = \
                componentDialogBox.SecondLevelItemsTimerDialog.get_data('Modificar ' + _nameStr, name=_nameStr,
                                                                        time_on=_timeOnStr, time_off=_timeOffStr,
                                                                        pin=_pinStr)
            if ok:
                _external = external.Generals()
                _external.component_modify_second_level_item_timer(index, _xName, _timeOn, _timeOff, pin)
                self._myDataBase.component_table_modify(str(_nameStr), str(_xName), str(_timeOn), str(_timeOff),
                                                        str(pin))
                if _pinStr != pin:
                    # Clear pin in the Arduino
                    self._mySerial.send_data('1' + '$' + '1' + '$' + str(pin) + '$' + '0' + ';')
                    # Set new pin and state in the arduino
                    self._mySerial.send_data('1' + '$' + '1' + '$' + str(pin) + '$' + '1' + ';')

        elif _timeTypeStr == '3':
            pass

        if _nameStr != _xName:
            self._update_control_name(_nameStr, _xName, _xTimeType)

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
        _pinList = self._myDataBase.component_group_table_delete_node(str(name))
        for _pin in _pinList:
            # As the pin is going to be cleared in the arduino the state can be anything
            self._mySerial.send_data('1' + '$' + '3' + '$' + str(_pin) + '$' + '0' + ';')

    def _remove_second_level_node(self, index):
        _nameStr = index.parent().child(index.row(), 0).data(QtCore.Qt.DisplayRole).toString()
        parent = index.model().itemFromIndex(index).parent()
        # Remove group from model
        parent.removeRow(index.row())
        # Remove group from database
        _pin = self._myDataBase.component_table_delete_row(str(_nameStr))
        # As the pin is going to be cleared in the arduino the state can be anything
        self._mySerial.send_data('1' + '$' + '3' + '$' + str(_pin) + '$' + '0' + ';')

    # ---------------------------------------ACTIVATE / DEACTIVATE---------------------------------------------
    def _activate_deactivate_second_level_node(self, index):
        _name = index.parent().child(index.row(), 0).data(QtCore.Qt.DisplayRole).toString()
        if index.model().itemFromIndex(index.parent().child(index.row(), 7)).checkState():
            yes = QtGui.QMessageBox().question(self, 'Desactivar Nodo',
                                               'Estas seguro que quieres desactivar la programacion del componente ' +
                                               _name + '???',
                                               QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if yes == QtGui.QMessageBox.Yes:
                index.model().itemFromIndex(index.parent().child(index.row(), 7)).setCheckState(QtCore.Qt.Unchecked)
                self._myDataBase.component_table_modify_active(str(_name), 0)
        else:
            _external = external.Generals()
            _timeOn = index.model().itemFromIndex(index.parent().child(index.row(), 2)).data(
                QtCore.Qt.DisplayRole).toString()
            _dateTimeOnItem = _external.get_date_time_data_type(_timeOn)
            _timeOff = index.model().itemFromIndex(index.parent().child(index.row(), 3)).data(
                QtCore.Qt.DisplayRole).toString()
            _dateTimeOffItem = _external.get_date_time_data_type(_timeOff)
            _state, _dateTimeOn, _dateTimeOff = _external.get_date_time_state(_dateTimeOnItem, _dateTimeOffItem)

            index.model().itemFromIndex(index.parent().child(index.row(), 2)).setData(
                _dateTimeOn.toString('HH:mm:ss dd-MM-yyyy'))
            index.model().itemFromIndex(index.parent().child(index.row(), 3)).setData(
                _dateTimeOff.toString('HH:mm:ss dd-MM-yyyy'))

            if _state == '0':
                index.model().itemFromIndex(index.parent().child(index.row(), 5)).set_tag('0')
            else:
                index.model().itemFromIndex(index.parent().child(index.row(), 5)).set_tag('1')

            _pin = index.parent().child(index.row(), 6).data(QtCore.Qt.DisplayRole).toString()
            self._serial_send_data('1', '2', _pin, _state)
            index.model().itemFromIndex(index.parent().child(index.row(), 7)).setCheckState(QtCore.Qt.Checked)
            self._myDataBase.component_table_modify_active(str(_name), 1)

            _name = index.parent().child(index.row(), 0).data(QtCore.Qt.DisplayRole).toString()
            _type = index.model().itemFromIndex(index.parent().child(index.row(), 1)).get_tag()
            self._update_control_state(_name, _type, _state)

    def _switch_on_off_second_level_node(self, index):
        _state = index.model().itemFromIndex(index.parent().child(index.row(), 5)).get_tag()
        _pin = index.parent().child(index.row(), 6).data(QtCore.Qt.DisplayRole).toString()
        _name = index.parent().child(index.row(), 0).data(QtCore.Qt.DisplayRole).toString()
        _type = index.model().itemFromIndex(index.parent().child(index.row(), 1)).get_tag()
        if _state == '0':
            index.model().itemFromIndex(index.parent().child(index.row(), 5)).set_tag('1')
            self._serial_send_data('1', '2', _pin, '1')
            self._update_control_state(_name, _type, '1')
        else:
            index.model().itemFromIndex(index.parent().child(index.row(), 5)).set_tag('0')
            self._serial_send_data('1', '2', _pin, '0')
            self._update_control_state(_name, _type, '0')

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
        _subMenuAnadir.addAction(_custom.get_component_context_menu_name_options(1),
                                 lambda: self._add_second_level_item_clock(index))
        _subMenuAnadir.addAction(_custom.get_component_context_menu_name_options(2),
                                 lambda: self._add_second_level_items_timer(index))
        _subMenuAnadir.addAction(_custom.get_component_context_menu_name_options(3), )

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
        if index.model().itemFromIndex(index.parent().child(index.row(), 7)).checkState():
            _mainContextMenu.addAction('Desactivar Programacion',
                                       lambda: self._activate_deactivate_second_level_node(index))
        else:
            _mainContextMenu.addAction('Activar Programacion',
                                       lambda: self._activate_deactivate_second_level_node(index))
            if index.model().itemFromIndex(index.parent().child(index.row(), 5)).get_tag() == '0':
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

    # -----------------------------------Timer--------------------------------------------

    def timer_start(self):
        self._mainTimer.start()

    def _time_out(self):
        self._myTimeouts.timeout(self._model, self._mainTimer.interval())

    def _serial_send_data(self, array_type, function, c_pin, c_state):
        self._mySerial.send_data(str(array_type) + '$' + str(function) + '$' + str(c_pin) + '$' + str(c_state) + ';')

    def set_timer_interval(self, interval):
        self._mainTimer.setInterval(interval)

    def init_control_state(self):
        _rootItem = self._model.item(0, 0)
        for i in xrange(_rootItem.rowCount()):
            _groupItem = _rootItem.child(i, 0)
            if _groupItem.hasChildren():
                for x in xrange(_groupItem.rowCount()):
                    # Execute only if the checkbox is checked
                    if _groupItem.child(x, 7).checkState():
                        _name = _groupItem.child(x, 0).data(QtCore.Qt.DisplayRole).toString()
                        _type = _groupItem.child(x, 1).get_tag()
                        if _groupItem.child(x, 5).get_tag_bool():
                            self.componentUpdateControlStateSignal.emit(_name, _type, '1')
                        else:
                            self.componentUpdateControlStateSignal.emit(_name, _type, '0')

    def _update_control_state(self, c_name, c_type, c_state):
        self.componentUpdateControlStateSignal.emit(c_name, c_type, c_state)

    def _update_control_name(self, previous_name, new_name, c_type):
        self.componentUpdateControlNameSignal.emit(previous_name, new_name, c_type)

    def set_font_size(self, size):
        _treeViewFont = QtGui.QFont()
        _treeViewFont.setPixelSize(size)
        self._myTreeView.setFont(_treeViewFont)

    def read_structure_from_database(self):
        self._myDataBase.read_component_structure(self._model)