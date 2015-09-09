from PyQt4 import QtCore
import sqlite3
from misc import external


class DataBase(QtCore.QObject):
    dbComponentArduinoSignal = QtCore.pyqtSignal(str, str, str, str)
    dbControlArduinoSignal = QtCore.pyqtSignal(str, str)
    dbNormalMessageSignal = QtCore.pyqtSignal(str)
    dbAlertMessageSignal = QtCore.pyqtSignal(str)

    def __init__(self):
        QtCore.QObject.__init__(self)
        # find user home directory
        self._directory = QtCore.QDir(QtCore.QDir().home().path() + '/jf/db')
        # Create directory if it doesn't exist
        if not self._directory.exists():
            QtCore.QDir().mkpath(self._directory.path())
        self._fileName = QtCore.QString('/jardinerofiel.sqlite')
        self._dbFile = QtCore.QFile(self._directory.path() + self._fileName)
        self._setup()

    def _setup(self):
        self._setup_database()

    def _setup_database(self):
        # if file is empty create tables
        if self._dbFile.size() == 0:
            try:
                connection = sqlite3.connect(str(self._dbFile.fileName()))
                with connection:
                    cur = connection.cursor()

                    cur.execute("CREATE TABLE component_group("
                                "id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                                "name TEXT NOT NULL, "
                                "enabled INTEGER NOT NULL)")

                    cur.execute("CREATE TABLE component("
                                "id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                                "group_id INTEGER NOT NULL, "
                                "name TEXT NOT NULL, "
                                "type TEXT NOT NULL, "
                                "switch_on TEXT NOT NULL, "
                                "switch_off TEXT NOT NULL, "
                                "pin TEXT NOT NULL, "
                                "active INTEGER NOT NULL, "
                                "enabled INTEGER NOT NULL)")

                    cur.execute("CREATE TABLE sensor_group("
                                "id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                                "name TEXT NOT NULL, "
                                "enabled INTEGER NOT NULL)")

                    cur.execute("CREATE TABLE sensor("
                                "id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                                "group_id INTEGER NOT NULL, "
                                "name TEXT NOT NULL, "
                                "type TEXT NOT NULL, "
                                "pin TEXT NOT NULL, "
                                "active INTEGER NOT NULL, "
                                "enabled INTEGER NOT NULL)")

                    cur.execute("CREATE TABLE control_group("
                                "id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                                "name TEXT NOT NULL, "
                                "enabled INTEGER NOT NULL)")

                    cur.execute("CREATE TABLE control("
                                "id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                                "group_id INTEGER NOT NULL, "
                                "control_type TEXT NOT NULL, "
                                "x_name TEXT NOT NULL, "
                                "x_type TEXT NOT NULL, "
                                "operator TEXT NOT NULL, "
                                "goal_value TEXT NOT NULL, "
                                "device_name TEXT NOT NULL, "
                                "pause TEXT NOT NULL, "
                                "protocol TEXT NOT NULL, "
                                "pin TEXT NOT NULL, "
                                "active INTEGER NOT NULL, "
                                "enabled INTEGER NOT NULL)")

                    cur.execute("CREATE TABLE data("
                                "id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                                "sensor_id INTEGER NOT NULL, "
                                "data REAL NOT NULL, "
                                "date_time TEXT NOT NULL, "
                                "enabled INTEGER NOT NULL)")
            except sqlite3.Error, e:
                self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])

    # --------------------------------------------------READ STRUCTURE-----------------------------------------------

    def read_component_structure(self, model):
        _external = external.Generals()
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("SELECT component_group.id, component_group.name FROM component_group "
                            "WHERE component_group.enabled=1")
                group_rows = cur.fetchall()
                for group_row in group_rows:
                    _external.component_add_first_level_item(model.item(0, 0), group_row[1])
                    cur.execute("SELECT component.name, component.type, component.switch_on, "
                                "component.switch_off, component.pin, component.active "
                                "FROM component "
                                "WHERE component.group_id=? "
                                "AND component.enabled=1", (group_row[0],))
                    component_rows = cur.fetchall()
                    for row in component_rows:
                        model_row_count = model.item(0, 0).rowCount() - 1
                        item = model.item(0, 0).child(model_row_count, 0)
                        if row[1] == '1':
                            _state = _external.component_add_second_level_item_clock(item, row[0], row[1],
                                                                                     QtCore.QString(row[2]),
                                                                                     QtCore.QString(row[3]),
                                                                                     row[4], row[5])
                            if row[5] == 0:
                                self.dbComponentArduinoSignal.emit('1', '1', row[4], '0')
                            else:
                                self.dbComponentArduinoSignal.emit('1', '1', row[4], _state)

                        elif row[1] == '2':
                            _external.component_add_second_level_item_timer(item, row[0], row[1],
                                                                            QtCore.QString(row[2]),
                                                                            QtCore.QString(row[3]), row[4], row[5])
                            if row[5] == 0:
                                self.dbComponentArduinoSignal.emit('1', '1', row[4], '0')
                            else:
                                self.dbComponentArduinoSignal.emit('1', '1', row[4], '1')

        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])

    def read_sensor_structure(self, model):
        _external = external.Generals()
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("SELECT sensor_group.id, sensor_group.name FROM sensor_group "
                            "WHERE sensor_group.enabled=1")
                group_rows = cur.fetchall()
                for group_row in group_rows:
                    _external.sensor_add_first_level_item(model.item(0, 0), group_row[1])
                    cur.execute("SELECT sensor.name, sensor.type, sensor.pin, sensor.active FROM sensor "
                                "WHERE sensor.group_id=? AND sensor.enabled=1", (group_row[0],))
                    sensor_rows = cur.fetchall()
                    for row in sensor_rows:
                        model_row_count = model.item(0, 0).rowCount() - 1
                        item = model.item(0, 0).child(model_row_count, 0)
                        _external.sensor_add_second_level_item(item, row[0], row[1], row[2], row[3])
        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])

    def read_control_structure(self, model):
        _external = external.Generals()
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("SELECT control_group.id, control_group.name FROM control_group "
                            "WHERE control_group.enabled=1")
                group_rows = cur.fetchall()
                for group_row in group_rows:
                    _external.control_add_first_level_item(model.item(0, 0), group_row[1])
                    cur.execute("SELECT control.control_type, control.x_name, control.x_type, "
                                "control.operator, control.goal_value, control.device_name, control.pause, "
                                "control.protocol, control.pin, control.active, control.id FROM control "
                                "WHERE control.group_id=? AND control.enabled=1", (group_row[0],))
                    sensor_rows = cur.fetchall()
                    for row in sensor_rows:
                        model_row_count = model.item(0, 0).rowCount() - 1
                        item = model.item(0, 0).child(model_row_count, 0)
                        _external.control_add_second_level_item_sensor(item, QtCore.QString(row[0]), row[1],
                                                                       QtCore.QString(row[2]), row[3], row[4],
                                                                       row[5], row[6], row[7], row[8], row[9], row[10])
                        self.dbControlArduinoSignal.emit(row[8], '0')

        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])

    # ---------------------------------COMPONENTS_GROUP TABLE-------------------------------------------

    def component_group_table_name_exist(self, group_name):
        exist = False
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("SELECT component_group.id FROM component_group WHERE component_group.name=? "
                            "AND component_group.enabled=1",
                            (group_name,))
                if len(cur.fetchall()) > 0:
                    exist = True
        except sqlite3.Error, e:
            print "Error %s:" % e.args[0]
        return exist

    def component_group_table_insert_node(self, group_name):
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("INSERT INTO component_group VALUES (NULL, ?, ?)",
                            (group_name, 1))
        except sqlite3.Error, e:
            print "Error %s:" % e.args[0]

    def component_group_table_modify_node(self, previous_name, new_name):
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("UPDATE component_group SET name=? "
                            "WHERE component_group.id IN "
                            "(SELECT component_group.id FROM component_group "
                            "WHERE component_group.name=? AND component_group.enabled=1)",
                            (new_name, previous_name))
        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])

    def component_group_table_delete_node(self, group_name):
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("SELECT component.pin FROM component WHERE component.group_id IN"
                            "(SELECT component_group.id FROM component_group "
                            "WHERE component_group.name=? AND component_group.enabled=1)", (group_name,))

                pins = cur.fetchall()
                _pinList = []
                for pin in pins:
                    _pinList.append(pin[0])

                cur.execute("UPDATE component SET enabled=0 "
                            "WHERE component.group_id IN "
                            "(SELECT component_group.id FROM component_group "
                            "WHERE component_group.name=? AND component_group.enabled=1)", (group_name,))

                cur.execute("UPDATE component_group SET enabled=0 "
                            "WHERE component_group.name=? and component_group.enabled=1", (group_name,))
                return _pinList
        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])

    # ---------------------------------COMPONENTS TABLE-------------------------------------------

    def component_table_name_exist(self, name):
        exist = False
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("SELECT component.id FROM component WHERE component.name=?"
                            "AND component.enabled=1",
                            (name,))
                if len(cur.fetchall()) > 0:
                    exist = True
        except sqlite3.Error, e:
            print "Error %s:" % e.args[0]
        return exist

    def component_table_select_component_names(self):
        _nameList = []
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("SELECT component.name, component.type FROM component WHERE component.enabled=1")
                rows = cur.fetchall()
                for row in rows:
                    _li = [row[0], row[1]]
                    _nameList.append(_li)
        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])
        return _nameList

    def component_table_insert_row(self, group_name, c_name, c_type, c_on, c_off, c_pin, c_active):
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("SELECT component_group.id FROM component_group "
                            "WHERE component_group.name=? "
                            "AND component_group.enabled=1", (group_name,))
                row = cur.fetchone()
                cur.execute("INSERT INTO component VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (row[0], c_name, c_type, c_on, c_off, c_pin, c_active, 1))
        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])

    def component_table_modify(self, previous_name, c_name, c_on, c_off, c_pin):
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("UPDATE component SET name=?, switch_on=?, switch_off=?, pin=? WHERE component.id IN "
                            "(SELECT component.id FROM component "
                            "WHERE component.name=? AND component.enabled=1)",
                            (c_name, c_on, c_off, c_pin, previous_name))
        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])

    def component_table_modify_active(self, c_name, c_active):
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("UPDATE component SET active=? WHERE component.name=? AND component.enabled=1",
                            (c_active, c_name))
        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])

    def component_table_delete_row(self, component_name):
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("SELECT component.pin FROM component "
                            "WHERE component.name=? AND component.enabled=1", (component_name,))
                _pin = cur.fetchone()

                cur.execute("UPDATE component SET enabled=0 "
                            "WHERE component.name=? AND component.enabled=1", (component_name,))
                return _pin[0]

        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])

    # ---------------------------------------------SENSORS_GROUP TABLE----------------------------------------

    def sensor_group_table_name_exist(self, group_name):
        exist = False
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("SELECT sensor_group.id FROM sensor_group WHERE sensor_group.name=?"
                            "AND sensor_group.enabled=1",
                            (group_name,))
                if len(cur.fetchall()) > 0:
                    exist = True
        except sqlite3.Error, e:
            print "Error %s:" % e.args[0]
        return exist

    def sensor_group_table_insert_node(self, group_name):
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("INSERT INTO sensor_group VALUES (NULL, ?, ?)",
                            (group_name, 1))
        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])

    def sensor_group_table_modify_node(self, previous_name, new_name):
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("UPDATE sensor_group SET name=? "
                            "WHERE sensor_group.id IN "
                            "(SELECT sensor_group.id FROM sensor_group "
                            "WHERE sensor_group.name=? AND sensor_group.enabled=1)", (new_name, previous_name))
        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])

    def sensor_group_table_delete_node(self, group_name):
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()

                cur.execute("SELECT sensor.pin FROM sensor WHERE sensor.group_id IN "
                            "(SELECT sensor_group.id FROM sensor_group WHERE sensor_group.name=? "
                            "AND sensor_group.enabled=1)", (group_name,))
                pins = cur.fetchall()
                _pinList = []
                for pin in pins:
                    _pinList.append(pin[0])

                # Update Data table
                cur.execute("UPDATE data SET enabled=0 WHERE data.id IN "
                            "(SELECT sensor_group.id FROM sensor_group "
                            "INNER JOIN sensor ON sensor_group.id = sensor.group_id "
                            "WHERE sensor_group.name=? AND sensor_group.enabled=1)",
                            (group_name,))

                # Update sensor table
                cur.execute("UPDATE sensor SET enabled=0 "
                            "WHERE sensor.group_id IN "
                            "(SELECT sensor_group.id FROM sensor_group "
                            "WHERE sensor_group.name=? AND sensor_group.enabled=1)", (group_name,))

                # Update sensor_group table
                cur.execute("UPDATE sensor_group SET enabled=0 "
                            "WHERE sensor_group.name=? and sensor_group.enabled=1", (group_name,))
                return _pinList
        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])

    # ---------------------------------------------SENSOR TABLE----------------------------------------

    def sensor_table_name_exist(self, name):
        exist = False
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("SELECT sensor.id FROM sensor WHERE sensor.name=?"
                            "AND sensor.enabled=1",
                            (name,))
                if len(cur.fetchall()) > 0:
                    exist = True
        except sqlite3.Error, e:
            print "Error %s:" % e.args[0]
        return exist

    def sensor_table_select_sensor_names(self):
        _nameList = []
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("SELECT sensor.name, sensor.type FROM sensor WHERE sensor.enabled=1")
                rows = cur.fetchall()
                for row in rows:
                    _li = [row[0], row[1]]
                    _nameList.append(_li)
        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])
        return _nameList

    def sensor_table_insert_row(self, group_name, sensor_name, sensor_type, sensor_pin):
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("SELECT sensor_group.id FROM sensor_group "
                            "WHERE sensor_group.name=? AND sensor_group.enabled=1", (group_name,))
                row = cur.fetchone()
                cur.execute("INSERT INTO sensor VALUES (NULL, ?, ?, ?, ?, ?, ?)",
                            (row[0], sensor_name, sensor_type, sensor_pin, 1, 1))
        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])

    def sensor_table_modify_row(self, previous_name, new_name, new_pin):
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("UPDATE sensor SET name=?, pin=? WHERE sensor.id IN "
                            "(SELECT sensor.id FROM sensor "
                            "WHERE sensor.name=? AND sensor.enabled=1)", (new_name, new_pin, previous_name))
        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])

    def sensor_table_modify_active_row(self, c_name, c_active):
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("UPDATE sensor SET active=? WHERE sensor.name=? AND sensor.enabled=1",
                            (c_active, c_name))
        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])

    def sensor_table_delete_row(self, sensor_name):
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("UPDATE data SET enabled=0 WHERE data.sensor_id IN "
                            "(SELECT sensor.id FROM sensor "
                            "WHERE sensor.name = ? AND sensor.enabled=1)", (sensor_name,))

                cur.execute("UPDATE sensor SET enabled=0 "
                            "WHERE sensor.name=? AND sensor.enabled=1", (sensor_name,))
        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])

    # ---------------------------------------CONTROL GROUP TABLE----------------------------------------------------

    def control_group_table_name_exist(self, group_name):
        exist = False
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("SELECT control_group.id FROM control_group WHERE control_group.name=?"
                            "AND control_group.enabled=1",
                            (group_name,))
                if len(cur.fetchall()) > 0:
                    exist = True
        except sqlite3.Error, e:
            print "Error %s:" % e.args[0]
        return exist

    def control_group_table_insert_node(self, group_name):
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("INSERT INTO control_group VALUES (NULL, ?, ?)",
                            (group_name, 1))
        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])

    def control_group_table_modify_node(self, previous_name, new_name):
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("UPDATE control_group SET name=? "
                            "WHERE control_group.id IN "
                            "(SELECT control_group.id FROM control_group "
                            "WHERE control_group.name=? AND control_group.enabled=1)", (new_name, previous_name))
        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])

    def control_table_modify_active_row(self, control_id, c_active):
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("UPDATE control SET active=? WHERE control.id=? AND control.enabled=1",
                            (c_active, control_id))
        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])

    def control_group_table_delete_node(self, group_name):
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("SELECT control.pin FROM control WHERE control.group_id IN"
                            "(SELECT control_group.id FROM control_group "
                            "WHERE control_group.name=? AND control_group.enabled=1)", (group_name,))

                pins = cur.fetchall()
                _pinList = []
                for pin in pins:
                    _pinList.append(pin[0])

                cur.execute("UPDATE control SET enabled=0 "
                            "WHERE control.group_id IN "
                            "(SELECT control_group.id FROM control_group "
                            "WHERE control_group.name=? AND control_group.enabled=1)", (group_name,))

                cur.execute("UPDATE control_group SET enabled=0 "
                            "WHERE control_group.name=? and control_group.enabled=1", (group_name,))
                return _pinList
        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])

    # ---------------------------------------CONTROL TABLE----------------------------------------------------

    def control_table_insert_row(self, group_name, control_type, x_name, x_type, operator, goal_value,
                                 goal_name, pause, protocol, pin, active):
        _id = -1
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("SELECT control_group.id FROM control_group "
                            "WHERE control_group.name=? AND control_group.enabled=1", (group_name,))
                row = cur.fetchone()
                cur.execute("INSERT INTO control VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (row[0], control_type, x_name, x_type, operator, goal_value, goal_name,
                             pause, protocol, pin, active, 1))
                cur.execute("SELECT last_insert_rowid()")
                row = cur.fetchone()
                _id = row[0]
        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])
        return _id

    def control_table_modify_row(self, control_id, x_name, x_type, operator, goal_value, device_name, pause,
                                 protocol, pin):
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("UPDATE control SET x_name=?, x_type=?, operator=?, goal_value=?, device_name=?, pause=?, "
                            "protocol=?, pin=? "
                            "WHERE control.id=? and control.enabled=1",
                            (x_name, x_type, operator, goal_value, device_name, pause, protocol, pin, control_id))
        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])

    def control_table_modify_name_row(self, control_id, x_name):
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("UPDATE control SET x_name=? WHERE control.id=? and control.enabled=1",
                            (x_name, control_id))
        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])

    def control_table_delete_row(self, control_id):
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("SELECT control.pin FROM control "
                            "WHERE control.id=? AND control.enabled=1", (control_id,))
                _pin = cur.fetchone()

                cur.execute("UPDATE control SET enabled=0 "
                            "WHERE control.id=? AND control.enabled=1", (control_id,))
                return _pin[0]

        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])

    # ---------------------------------------DATA----------------------------------------------------

    def data_table_insert_row(self, sensor_name, sensor_type, date_time, value):
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("SELECT sensor.id "
                            "FROM sensor "
                            "WHERE sensor.name=? AND sensor.type=? AND sensor.enabled=1", (sensor_name, sensor_type))
                _sensor_id = cur.fetchone()
                cur.execute("INSERT INTO data VALUES (NULL, ?, ?, ?, ?)", (_sensor_id[0], value, date_time, 1))
        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])

    def data_table_select_active_sensors(self, sensor_type):
        _sensorIdList = []
        _sensorNameList = []
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                if len(sensor_type) < 2:
                    cur = connection.cursor()
                    cur.execute("SELECT sensor.id, sensor.name FROM sensor WHERE sensor.type=? "
                                "AND sensor.enabled=1", (sensor_type[0]))
                    rows = cur.fetchall()
                    for row in rows:
                        _sensorIdList.append(row[0])
                        _sensorNameList.append(row[1])
                else:
                    cur = connection.cursor()
                    cur.execute("SELECT sensor.id, sensor.name FROM sensor WHERE sensor.type IN (?, ?) "
                                "AND sensor.enabled=1", (sensor_type[0], sensor_type[1]))
                    rows = cur.fetchall()
                    for row in rows:
                        _sensorIdList.append(row[0])
                        _sensorNameList.append(row[1])
        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])
        return _sensorIdList, _sensorNameList

    def data_table_select_data(self, sensor_id, limit):
        _dataList = []
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("SELECT data.data FROM data WHERE data.sensor_id=? "
                            "ORDER BY datetime(data.date_time) DESC LIMIT ?", (sensor_id, limit))
                rows = cur.fetchall()
                for row in rows:
                    _dataList.append(row[0])
                # reverse list
                # _dataList = _dataList[::-1]

                if len(_dataList) < limit:
                    self._fill_up_data_list(_dataList, limit)
        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])
        return _dataList

    @staticmethod
    def _fill_up_data_list(data_list, limit):
        t = limit - len(data_list)
        for x in xrange(t):
            data_list.append(0)

    # -----------------------------------------------------------------------------------------------

    def get_pin_list(self):
        _pinList = []
        try:
            connection = sqlite3.connect(str(self._dbFile.fileName()))
            with connection:
                cur = connection.cursor()
                cur.execute("SELECT component.pin FROM component WHERE component.enabled=1")
                rows = cur.fetchall()
                for row in rows:
                    _pinList.append(row[0])

                cur.execute("SELECT sensor.pin FROM sensor WHERE sensor.enabled=1")
                rows = cur.fetchall()
                for row in rows:
                    _pinList.append(row[0])

                cur.execute("SELECT control.pin FROM control WHERE control.enabled=1")
                rows = cur.fetchall()
                for row in rows:
                    _pinList.append(row[0])

        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])
        return _pinList

    def check_file_size(self):
        # print self._dbFile.size()
        # If database size reach a certain limit create a new database file, in this case is 100M
        if self._dbFile.size() > 100000000:
            self._dbFile.close()
            _auxFile = QtCore.QFile(self._directory.path() + self._fileName)
            _auxFileName = self._directory.path() + '/' + QtCore.QDate().currentDate().toString(
                'yyyy-MM-dd') + '_' + self._fileName.mid(1)
            _auxFile.rename(_auxFileName)
            _auxFile.close()
            self._dbFile = QtCore.QFile(self._directory.path() + self._fileName)
            self._setup_database()
            self._copy_tables(str(_auxFile.fileName()), str(self._dbFile.fileName()))

    # ------------------------------------------COPY TABLES-------------------------------------

    def _copy_tables(self, source, destination):
        try:
            _source_conn = sqlite3.connect(source)
            _destination_conn = sqlite3.connect(destination)
            with _source_conn:
                self.dbNormalMessageSignal.emit('Realizando copia de base de datos')
                self._copy_component_group_table(_source_conn, _destination_conn)
                self._copy_component_table(_source_conn, _destination_conn)
                self._copy_sensor_group_table(_source_conn, _destination_conn)
                self._copy_sensor_table(_source_conn, _destination_conn)
                self._copy_control_group_table(_source_conn, _destination_conn)
                self._copy_control_table(_source_conn, _destination_conn)
                self.dbNormalMessageSignal.emit('Copia de base de datos finalizada')
        except sqlite3.Error, e:
            self.dbAlertMessageSignal.emit("Error %s:" % e.args[0])

    @staticmethod
    def _copy_component_group_table(src_conn, dest_conn):
        cur_origin = src_conn.cursor()
        cur_origin.execute("SELECT component_group.name, component_group.enabled FROM component_group")
        rows = cur_origin.fetchall()
        with dest_conn:
            cur_destination = dest_conn.cursor()
            for row in rows:
                cur_destination.execute("INSERT INTO component_group VALUES (NULL, ?, ?)", (row[0], row[1]))

    @staticmethod
    def _copy_component_table(src_conn, dest_conn):
        cur_origin = src_conn.cursor()
        cur_origin.execute("SELECT component.group_id, component.name, component.type, component.switch_on, "
                           "component.switch_off, component.pin, component.active, component.enabled FROM component")
        rows = cur_origin.fetchall()
        with dest_conn:
            cur_destination = dest_conn.cursor()
            for row in rows:
                cur_destination.execute("INSERT INTO component VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)",
                                        (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

    @staticmethod
    def _copy_sensor_group_table(src_conn, dest_conn):
        cur_origin = src_conn.cursor()
        cur_origin.execute("SELECT sensor_group.name, sensor_group.enabled FROM sensor_group")
        rows = cur_origin.fetchall()
        with dest_conn:
            cur_destination = dest_conn.cursor()
            for row in rows:
                cur_destination.execute("INSERT INTO sensor_group VALUES (NULL, ?, ?)", (row[0], row[1]))

    @staticmethod
    def _copy_sensor_table(src_conn, dest_conn):
        cur_origin = src_conn.cursor()
        cur_origin.execute("SELECT sensor.group_id, sensor.name, sensor.type, sensor.pin, sensor.active, "
                           "sensor.enabled FROM sensor")
        rows = cur_origin.fetchall()
        with dest_conn:
            cur_destination = dest_conn.cursor()
            for row in rows:
                cur_destination.execute("INSERT INTO sensor VALUES (NULL, ?, ?, ?, ?, ?, ?)",
                                        (row[0], row[1], row[2], row[3], row[4], row[5]))

    @staticmethod
    def _copy_control_group_table(src_conn, dest_conn):
        cur_origin = src_conn.cursor()
        cur_origin.execute("SELECT control_group.name, control_group.enabled FROM control_group")
        rows = cur_origin.fetchall()
        with dest_conn:
            cur_destination = dest_conn.cursor()
            for row in rows:
                cur_destination.execute("INSERT INTO control_group VALUES (NULL, ?, ?)", (row[0], row[1]))

    @staticmethod
    def _copy_control_table(src_conn, dest_conn):
        cur_origin = src_conn.cursor()
        cur_origin.execute("SELECT control.group_id, control.control_type, control.x_name, control.x_type, "
                           "control.operator, control.goal_value, control.device_name, control.pause, control.protocol,"
                           "control.pin, control.active, control.enabled FROM control")
        rows = cur_origin.fetchall()
        with dest_conn:
            cur_destination = dest_conn.cursor()
            for row in rows:
                cur_destination.execute("INSERT INTO control VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                        (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8],
                                         row[9], row[10], row[11]))