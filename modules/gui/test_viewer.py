from PyQt5 import QtGui, QtCore, QtWidgets
import sys


class Main(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super(Main, self).__init__(parent)

        # main button
        self.addButton = QtWidgets.QPushButton('button to add other widgets')
        self.addButton.clicked.connect(self.addWidget)

        # scroll area widget contents - layout
        self.scrollLayout = QtWidgets.QFormLayout()

        # scroll area widget contents
        self.scrollWidget = QtWidgets.QWidget()
        self.scrollWidget.setLayout(self.scrollLayout)

        # scroll area
        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollWidget)

        # main layout
        self.mainLayout = QtWidgets.QVBoxLayout()

        # add all main to the main vLayout
        self.mainLayout.addWidget(self.addButton)
        self.mainLayout.addWidget(self.scrollArea)

        # central widget
        self.centralWidget = QtWidgets.QWidget()
        self.centralWidget.setLayout(self.mainLayout)

        # set central widget
        self.setCentralWidget(self.centralWidget)

    def addWidget(self):
        self.scrollLayout.addRow(Test())


class Test(QtWidgets.QWidget):
  def __init__( self, parent=None):
      super(Test, self).__init__(parent)

      self.pushButton = QtWidgets.QPushButton('I am in Test widget')

      layout = QtWidgets.QHBoxLayout()
      layout.addWidget(self.pushButton)
      self.setLayout(layout)



app = QtWidgets.QApplication(sys.argv)
myWidget = Main()
myWidget.show()
app.exec_()