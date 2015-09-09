from PyQt4 import QtGui, QtCore


class XAxisRangeDialogBox(QtGui.QDialog):
    def __init__(self, value, parent=None):
        super(XAxisRangeDialogBox, self).__init__(parent)
        self._xrange = value
        self._xAxisLabel = QtGui.QLabel('Dias:', self)
        self._xAxisSpinBox = QtGui.QSpinBox(self)
        self._dialogButtons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                                     QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        self._setup()

    def _setup(self):
        self._setup_layout()
        self._setup_spinbox()
        self._setup_connections()

    def _setup_layout(self):
        _xAxisLayout = QtGui.QHBoxLayout()
        _xAxisLayout.addWidget(self._xAxisLabel)
        _xAxisLayout.addWidget(self._xAxisSpinBox)

        _mainLayout = QtGui.QVBoxLayout(self)
        _mainLayout.addLayout(_xAxisLayout)
        _mainLayout.addWidget(self._dialogButtons)

        self.setLayout(_mainLayout)

    def _setup_spinbox(self):
        self._xAxisSpinBox.setMinimum(1)
        self._xAxisSpinBox.setMaximum(31)
        self._xAxisSpinBox.setSingleStep(1)
        self._setup_spinbox_initial_values()

    def _setup_spinbox_initial_values(self):
        self._xAxisSpinBox.setValue(self._xrange)

    def _setup_connections(self):
        self._dialogButtons.accepted.connect(self._validations)
        self._dialogButtons.rejected.connect(self.reject)

    def _validations(self):
        self.accept()

    def _get_x_axis_spinbox_value(self):
        return self._xAxisSpinBox.value()

    @staticmethod
    def get_data(value, parent=None):
        dialog = XAxisRangeDialogBox(value, parent)
        _result = dialog.exec_()
        _value = dialog._get_x_axis_spinbox_value()
        return _value, _result == QtGui.QDialog.Accepted