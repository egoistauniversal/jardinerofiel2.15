from PyQt4 import QtGui

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure

# TODO check if we can change x axis messurement


class TabGraphics(QtGui.QWidget):
    def __init__(self, database):
        super(TabGraphics, self).__init__()
        self._canvas = MyMplCanvas(database)
        self._navigationToolBar = NavigationToolbar(self._canvas, self)
        self._setup()

    def _setup(self):
        self._layouts()
        self._canvas.update_figure(['1', '2'])

    def _layouts(self):
        _mainLayout = QtGui.QVBoxLayout(self)
        _mainLayout.addWidget(self._canvas)
        _mainLayout.addWidget(self._navigationToolBar)

        self.setLayout(_mainLayout)

    def update_graphic(self, sensor_type):
        self._canvas.update_figure(sensor_type)

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
        self._sensorTypeNamesList = ['Temperaturas', 'Temperaturas', 'Humedad', 'PH', 'EC']

        # initialize the canvas where the Figure renders into
        FigureCanvas.__init__(self, self.fig)
        self._xAxisRangeValue = None
        self._xAxisRange = None
        # self._x = [x for x in xrange(self._xAxisRange)]
        self._x = None
        self._y = []
        self._setup()

    def _setup(self):
        self._axes.set_color_cycle(['r', 'g', 'b', 'c', 'm', 'y', 'k'])
        self.set_x_axis_range_value(1)
        self._fill_up_axis_x()

    def update_figure(self, sensor_type):
        # We want the axes cleared every time plot() is called self.axes.hold(False)
        self._axes.hold(False)
        _sensorIdList, _sensorNameList = self._myDataBase.data_table_select_active_sensors(sensor_type)
        # if _sensorIdList contains data plot result
        if _sensorIdList:
            for _sensorId, _sensorName in zip(_sensorIdList, _sensorNameList):
                self._y = self._myDataBase.data_table_select_data(_sensorId, self._xAxisRange)
                self._axes.plot(self._x, self._y, linestyle='-', linewidth=1.0, label=_sensorName)
                self._axes.hold(True)

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
        self._xAxisRange = self._xAxisRangeValue * 1440
        self._fill_up_axis_x()

    def get_x_axis_range_value(self):
        return self._xAxisRangeValue