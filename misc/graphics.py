from PyQt4 import QtGui

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure

# TODO check if we can change x axis messurement


class Graphics(QtGui.QWidget):
    def __init__(self, database):
        QtGui.QWidget.__init__(self)
        # super(Graphics, self).__init__()
        self._canvas = MyMplCanvas(database)
        self._navigationToolBar = NavigationToolbar(self._canvas, self)
        self._setup()

    def _setup(self):
        self._layouts()

    def _layouts(self):
        _mainLayout = QtGui.QVBoxLayout(self)
        _mainLayout.addWidget(self._canvas)
        _mainLayout.addWidget(self._navigationToolBar)

        self.setLayout(_mainLayout)

    def update_graphic(self, sensor_name, sensor_type, days):
        self._canvas.update_figure(sensor_name, sensor_type, days)

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
        self._x = []
        self._y = []
        self._xDateTime = []

        self._setup()

    def _setup(self):
        self._axes.set_color_cycle(['r', 'g', 'b', 'c', 'm', 'y', 'k'])
        self.set_x_axis_range_value(1)
        self._fill_up_axis_x()

    def update_figure(self, sensor_name, sensor_type, days):
        # We want the axes cleared every time plot() is called self.axes.hold(False)
        self._axes.hold(False)
        _sensor_id = self._myDataBase.data_table_select_sensor_id(sensor_name, sensor_type)
        if _sensor_id:
            self._x, self._y, self._xDateTime = self._myDataBase.data_table_select_data_time_by_days(_sensor_id, days)
            self._axes.plot(self._x, self._y, linestyle='-', linewidth=1.0, label=sensor_name)
            self._axes.hold(True)
            self._axes.set_xticklabels(self._xDateTime, rotation='vertical')
            # self._axes.xticks(self._x, self._xDateTime, rotation='vertical')


            # Legend position 1: upper right, 2: upper left, etc
            _legend = self._axes.legend(loc=1)
            # set the linewidth of each legend object
            for _leg in _legend.legendHandles:
                _leg.set_linewidth(3.0)

            self._axes.set_title(self._sensorTypeNamesList[int(sensor_type[0])-1])
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
