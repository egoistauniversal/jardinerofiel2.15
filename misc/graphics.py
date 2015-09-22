from PyQt4 import QtGui
from PyQt4 import QtCore

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure

class Graphics(QtGui.QWidget):
    def __init__(self, database):
        QtGui.QWidget.__init__(self)
        # super(Graphics, self).__init__()
        self._database = database
        self._canvas = MyMplCanvas(database)
        self._navigationToolBar = NavigationToolbar(self._canvas, self)
        self.thread = Worker()
        self._setup()

    def _setup(self):
        self._layouts()
        self._connections()

    def _connections(self):
        self.thread.mysignal.connect(self.set_axis_data)

    def _layouts(self):
        _mainLayout = QtGui.QVBoxLayout(self)
        _mainLayout.addWidget(self._canvas)
        _mainLayout.addWidget(self._navigationToolBar)

        self.setLayout(_mainLayout)

    def update_graphic(self, sensor_name, sensor_type, days):
        self.thread.render(self._database, sensor_name, sensor_type, days)
        # self._canvas.update_figure(sensor_name, sensor_type, days)

    def set_axis_data(self, x, y, xdatetime, sensor_name, sensor_type):
        self._canvas.update_figure(x, y, xdatetime, sensor_name, sensor_type)

    def set_x_axis_range(self, value):
        self._canvas.set_x_axis_range_value(value)

    def get_x_axis_range(self):
        return self._canvas.get_x_axis_range_value()


class MyMplCanvas(FigureCanvas):
    """Class to represent the FigureCanvas widget"""
    def __init__(self, database):
        self._myDataBase = database
        self.fig = Figure()
        self._axes = self.fig.add_subplot(111)
        self._sensorTypeNamesList = ['Temperatura', 'Temperatura', 'Humedad', 'PH', 'EC', 'Luz']

        # initialize the canvas where the Figure renders into
        FigureCanvas.__init__(self, self.fig)
        self._xAxisRangeValue = None
        self._xAxisRange = None
        self._setup()

    def _setup(self):
        self._axes.set_color_cycle(['r', 'g', 'b', 'c', 'm', 'y', 'k'])
        self.set_x_axis_range_value(1)
        # self._fill_up_axis_x()

    def update_figure(self, x, y, xdatetime, sensor_name, sensor_type):
        # We want the axes cleared every time plot() is called self.axes.hold(False)
        self._axes.hold(False)

        self._axes.plot(x, y, linestyle='-', linewidth=1.0, label=sensor_name)
        self._axes.hold(True)
        self._axes.set_xticklabels(xdatetime, rotation='vertical')

        # Legend position 1: upper right, 2: upper left, etc
        _legend = self._axes.legend(loc=1)
        # set the linewidth of each legend object
        for _leg in _legend.legendHandles:
            _leg.set_linewidth(3.0)

        self._axes.set_title(self._sensorTypeNamesList[sensor_type-1])
        self._axes.set_xlabel('Minutos')
        # force a redraw of the Figure
        self.fig.canvas.draw()

    def _fill_up_axis_x(self):
        self._x = [x for x in xrange(self._xAxisRange)]

    def set_x_axis_range_value(self, value):
        self._xAxisRangeValue = value
        self._xAxisRange = self._xAxisRangeValue * 10
        self._fill_up_axis_x()

    def get_x_axis_range_value(self):
        return self._xAxisRangeValue

class Worker(QtCore.QThread):
    mysignal = QtCore.pyqtSignal(list, list, list, str, int)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self._database = None
        self._sensor_name = None
        self._sensor_type = None
        self._days = None
        self._x = []
        self._y = []
        self._xDateTime = []

    def render(self, database, sensor_name, sensor_type, days):
        self._database = database
        self._sensor_name = sensor_name
        self._sensor_type = sensor_type
        self._days = days
        self.start()

    def run(self):
        _sensor_id = self._database.data_table_select_sensor_id(self._sensor_name, self._sensor_type)
        # print _sensor_id
        if _sensor_id:
            self._x, self._y, self._xDateTime = \
                self._database.data_table_select_data_time_by_days(_sensor_id, self._days)
            self.mysignal.emit(self._x, self._y, self._xDateTime, str(self._sensor_name), int(self._sensor_type))
