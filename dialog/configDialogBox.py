from PyQt4 import QtGui, QtCore
from misc import files


class StandardDialogBox(QtGui.QDialog):
    def __init__(self, parent=None):
        super(StandardDialogBox, self).__init__(parent)
        self._treeViewFontSizeLabel = QtGui.QLabel('Tamano de la fuente:', self)
        self._treeViewFontSizeSpinBox = QtGui.QSpinBox(self)

        self._sensorThresholdLabel = QtGui.QLabel('Rango umbral de los Sensores:', self)
        self._sensorThresholdSpinBox = QtGui.QSpinBox(self)

        self._dialogButtons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                                     QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        self._setup()

    def _setup(self):
        self._setup_layout()
        self._setup_spinbox()
        self._setup_spinbox_initial_values()
        self._setup_connections()

    def _setup_layout(self):
        _fontSizeLayout = QtGui.QHBoxLayout()
        _fontSizeLayout.addWidget(self._treeViewFontSizeLabel)
        _fontSizeLayout.addWidget(self._treeViewFontSizeSpinBox)

        _sensorThresholdLayout = QtGui.QHBoxLayout()
        _sensorThresholdLayout.addWidget(self._sensorThresholdLabel)
        _sensorThresholdLayout.addWidget(self._sensorThresholdSpinBox)

        _mainLayout = QtGui.QVBoxLayout(self)
        _mainLayout.addLayout(_fontSizeLayout)
        _mainLayout.addLayout(_sensorThresholdLayout)
        _mainLayout.addWidget(self._dialogButtons)

        self.setLayout(_mainLayout)

    def _setup_spinbox(self):
        self._treeViewFontSizeSpinBox.setMinimum(10)
        self._treeViewFontSizeSpinBox.setMaximum(20)
        self._treeViewFontSizeSpinBox.setSingleStep(1)
        
        self._sensorThresholdSpinBox.setMinimum(5)
        self._sensorThresholdSpinBox.setMaximum(50)
        self._sensorThresholdSpinBox.setSingleStep(1)

    def _setup_spinbox_initial_values(self):
        _file = files.Standard()
        _list = _file.read()
        self._treeViewFontSizeSpinBox.setValue(int(_list[0]))
        self._sensorThresholdSpinBox.setValue(int(_list[1]))

    def _setup_connections(self):
        self._dialogButtons.accepted.connect(self._validations)
        self._dialogButtons.rejected.connect(self.reject)

    def _validations(self):
        _list = [str(self._treeViewFontSizeSpinBox.value()), str(self._sensorThresholdSpinBox.value())]
        _file = files.Standard()
        _file.write(_list)
        self.accept()

    @staticmethod
    def get_data(parent=None):
        dialog = StandardDialogBox(parent)
        result = dialog.exec_()
        return result == QtGui.QDialog.Accepted

    # ------------------------------------------PINS-------------------------------------------


class PinsDialogBox(QtGui.QDialog):
    def __init__(self, parent=None):
        super(PinsDialogBox, self).__init__(parent)
        self.setWindowTitle('Pines')

        self._AnalogPinsLabel = QtGui.QLabel('Pines Analogicos:', self)
        self._analogPinsSlider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self._AnalogPinsSliderValueLabel = QtGui.QLabel('', self)

        self._digitalPinsLabel = QtGui.QLabel('Pines Digitales:', self)
        self._digitalPinsSlider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self._digitalPinsSliderValueLabel = QtGui.QLabel('', self)

        self._dialogButtons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                                     QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        self._setup()

    def _setup(self):
        self._setup_layout()
        self._setup_geometry()
        self._setup_labels()
        self._setup_connections()
        self._setup_sliders()

    def _setup_layout(self):
        _gridLayout = QtGui.QGridLayout()

        _gridLayout.addWidget(self._AnalogPinsLabel, 0, 0)
        _gridLayout.addWidget(self._analogPinsSlider, 0, 1)
        _gridLayout.addWidget(self._AnalogPinsSliderValueLabel, 0, 2)

        _gridLayout.addWidget(self._digitalPinsLabel, 1, 0)
        _gridLayout.addWidget(self._digitalPinsSlider, 1, 1)
        _gridLayout.addWidget(self._digitalPinsSliderValueLabel, 1, 2)

        _mainLayout = QtGui.QVBoxLayout(self)
        _mainLayout.addLayout(_gridLayout)
        _mainLayout.addWidget(self._dialogButtons)

        self.setLayout(_mainLayout)

    def _setup_geometry(self):
        self.setGeometry(300, 300, 600, 200)

    def _setup_labels(self):
        self._AnalogPinsSliderValueLabel.setAlignment(QtCore.Qt.AlignRight)
        self._AnalogPinsSliderValueLabel.setFixedWidth(50)
        self._AnalogPinsSliderValueLabel.setText(str(self._analogPinsSlider.value()))

        self._digitalPinsSliderValueLabel.setAlignment(QtCore.Qt.AlignRight)
        self._digitalPinsSliderValueLabel.setFixedWidth(50)
        self._digitalPinsSliderValueLabel.setText(str(self._digitalPinsSlider.value()))

    def _setup_sliders(self):
        self._analogPinsSlider.setMinimum(0)
        self._analogPinsSlider.setMaximum(15)
        self._analogPinsSlider.setSingleStep(1)
        self._analogPinsSlider.setTickInterval(1)

        self._digitalPinsSlider.setMinimum(0)
        self._digitalPinsSlider.setMaximum(54)
        self._digitalPinsSlider.setSingleStep(1)
        self._digitalPinsSlider.setTickInterval(1)

        self._setup_sliders_initial_values()

    def _setup_sliders_initial_values(self):
        _file = files.Pins()
        _list = _file.read()
        self._analogPinsSlider.setValue(int(_list[0]))
        self._analog_pin_slider_value_changed()
        self._digitalPinsSlider.setValue(int(_list[1]))
        self._digital_pin_slider_value_changed()

    def _setup_connections(self):
        self._analogPinsSlider.valueChanged.connect(self._analog_pin_slider_value_changed)
        self._digitalPinsSlider.valueChanged.connect(self._digital_pin_slider_value_changed)
        self._dialogButtons.accepted.connect(self._validations)
        self._dialogButtons.rejected.connect(self.reject)

    def _validations(self):
        _list = [str(self._analogPinsSlider.value()), str(self._digitalPinsSlider.value())]
        _file = files.Pins()
        _file.write(_list)
        self.accept()

    # ---------------------------------------Sliders Value Changed-------------------------

    def _analog_pin_slider_value_changed(self):
        self._AnalogPinsSliderValueLabel.setText(str(self._analogPinsSlider.value()))

    def _digital_pin_slider_value_changed(self):
        self._digitalPinsSliderValueLabel.setText(str(self._digitalPinsSlider.value()))

    @staticmethod
    def get_data(parent=None):
        dialog = PinsDialogBox(parent)
        result = dialog.exec_()
        return result == QtGui.QDialog.Accepted

    # -----------------------------------------------INTERVALS--------------------------------------------------


class IntervalsDialogBox(QtGui.QDialog):
    def __init__(self, parent=None):
        super(IntervalsDialogBox, self).__init__(parent)
        self.setWindowTitle('Intervalos')

        self._componentLabel = QtGui.QLabel('Componentes Intervalo:', self)
        self._componentSlider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self._componentSliderValueLabel = QtGui.QLabel('', self)

        self._sensorLabel = QtGui.QLabel('Sensores Intervalo:', self)
        self._sensorSlider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self._sensorSliderValueLabel = QtGui.QLabel('', self)

        self._sensorRequestOneDataLabel = QtGui.QLabel('Solicitud de datos entre sensores:', self)
        self._sensorRequestOneDataSlider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self._sensorRequestOneDataValueLabel = QtGui.QLabel('', self)

        self._sensorGetOneDataLabel = QtGui.QLabel('Obtener datos entre sensores:', self)
        self._sensorGetOneDataSlider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self._sensorGetOneDataValueLabel = QtGui.QLabel('', self)

        self._dialogButtons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                                     QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        self._setup()

    def _setup(self):
        self._setup_layout()
        self._setup_geometry()
        self._setup_labels()
        self._setup_connections()
        self._setup_sliders()

    def _setup_layout(self):
        _gridLayout = QtGui.QGridLayout()

        _gridLayout.addWidget(self._componentLabel, 0, 0)
        _gridLayout.addWidget(self._componentSlider, 0, 1)
        _gridLayout.addWidget(self._componentSliderValueLabel, 0, 2)

        _gridLayout.addWidget(self._sensorLabel, 1, 0)
        _gridLayout.addWidget(self._sensorSlider, 1, 1)
        _gridLayout.addWidget(self._sensorSliderValueLabel, 1, 2)

        _gridLayout.addWidget(self._sensorRequestOneDataLabel, 2, 0)
        _gridLayout.addWidget(self._sensorRequestOneDataSlider, 2, 1)
        _gridLayout.addWidget(self._sensorRequestOneDataValueLabel, 2, 2)

        _gridLayout.addWidget(self._sensorGetOneDataLabel, 3, 0)
        _gridLayout.addWidget(self._sensorGetOneDataSlider, 3, 1)
        _gridLayout.addWidget(self._sensorGetOneDataValueLabel, 3, 2)

        _mainLayout = QtGui.QVBoxLayout(self)
        _mainLayout.addLayout(_gridLayout)
        _mainLayout.addWidget(self._dialogButtons)

        self.setLayout(_mainLayout)

    def _setup_geometry(self):
        self.setGeometry(300, 300, 600, 200)

    def _setup_sliders(self):
        self._componentSlider.setMinimum(1)
        self._componentSlider.setMaximum(60)
        self._componentSlider.setSingleStep(5)
        self._componentSlider.setTickInterval(5)

        self._sensorSlider.setMinimum(5)
        self._sensorSlider.setMaximum(120)
        self._sensorSlider.setSingleStep(5)
        self._sensorSlider.setTickInterval(5)

        self._sensorRequestOneDataSlider.setMinimum(1)
        self._sensorRequestOneDataSlider.setMaximum(10)
        self._sensorRequestOneDataSlider.setSingleStep(1)
        self._sensorRequestOneDataSlider.setTickInterval(1)

        self._sensorGetOneDataSlider.setMinimum(1)
        self._sensorGetOneDataSlider.setMaximum(10)
        self._sensorGetOneDataSlider.setSingleStep(1)
        self._sensorGetOneDataSlider.setTickInterval(1)

        self._setup_sliders_initial_values()

    def _setup_labels(self):
        self._componentSliderValueLabel.setAlignment(QtCore.Qt.AlignRight)
        self._componentSliderValueLabel.setFixedWidth(50)
        self._componentSliderValueLabel.setText(str(self._componentSlider.value() * 1000))

        self._sensorSliderValueLabel.setAlignment(QtCore.Qt.AlignRight)
        self._sensorSliderValueLabel.setFixedWidth(50)
        self._sensorSliderValueLabel.setText(str(self._sensorSlider.value() * 1000))

        self._sensorRequestOneDataValueLabel.setAlignment(QtCore.Qt.AlignRight)
        self._sensorRequestOneDataValueLabel.setFixedWidth(50)
        self._sensorRequestOneDataValueLabel.setText(str(self._sensorRequestOneDataSlider.value() * 100))

        self._sensorGetOneDataValueLabel.setAlignment(QtCore.Qt.AlignRight)
        self._sensorGetOneDataValueLabel.setFixedWidth(50)
        self._sensorGetOneDataValueLabel.setText(str(self._sensorGetOneDataSlider.value() * 100))

    def _setup_sliders_initial_values(self):
        _file = files.Intervals()
        _list = _file.read()
        self._componentSlider.setValue(int(_list[0])/1000)
        self._component_slider_value_changed()
        self._sensorSlider.setValue(int(_list[1])/1000)
        self._sensor_slider_value_changed()
        self._sensorRequestOneDataSlider.setValue(int(_list[2])/100)
        self._sensor_slider_request_value_changed()
        self._sensorGetOneDataSlider.setValue(int(_list[3])/100)
        self._sensor_slider_get_value_changed()

    def _setup_connections(self):
        self._componentSlider.valueChanged.connect(self._component_slider_value_changed)
        self._sensorSlider.valueChanged.connect(self._sensor_slider_value_changed)
        self._sensorRequestOneDataSlider.valueChanged.connect(self._sensor_slider_request_value_changed)
        self._sensorGetOneDataSlider.valueChanged.connect(self._sensor_slider_get_value_changed)
        self._dialogButtons.accepted.connect(self._validations)
        self._dialogButtons.rejected.connect(self.reject)

    def _validations(self):
        _list = [str(self._componentSlider.value()*1000), str(self._sensorSlider.value()*1000),
                 str(self._sensorRequestOneDataSlider.value()*100), str(self._sensorGetOneDataSlider.value()*100)]
        _file = files.Intervals()
        _file.write(_list)
        self.accept()

    # ---------------------------------------Sliders Value Changed-------------------------

    def _component_slider_value_changed(self):
        self._componentSliderValueLabel.setText(str(self._componentSlider.value() * 1000))

    def _sensor_slider_value_changed(self):
        self._sensorSliderValueLabel.setText(str(self._sensorSlider.value() * 1000))

    def _sensor_slider_request_value_changed(self):
        self._sensorRequestOneDataValueLabel.setText(str(self._sensorRequestOneDataSlider.value() * 100))

    def _sensor_slider_get_value_changed(self):
        self._sensorGetOneDataValueLabel.setText(str(self._sensorGetOneDataSlider.value() * 100))

    @staticmethod
    def get_data(parent=None):
        dialog = IntervalsDialogBox(parent)
        result = dialog.exec_()
        return result == QtGui.QDialog.Accepted