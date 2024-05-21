# This example shows how to embed RoboDK inside a generic QWidget window using Python and PySide6.

import sys
import ctypes
from robodk import robolink
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog
from PySide6.QtGui import QPalette, QColor


class MainWindow(QMainWindow):

	def __init__(self):
		super(MainWindow, self).__init__()

		#self.RDK = robolink.Robolink()

		self.RDK = robolink.Robolink(args=["-NEWINSTANCE"])
		self.setWindowTitle("RoboDK Interface Test")

		MainLayout = QHBoxLayout()

		# Keep a reference to the widget for the RDK window - fill it with red color
		self.RobotWidget = Color('#030337')
		MainLayout.addWidget(self.RobotWidget)
		self.RobotWidget.resizeEvent = self.windowResize

		# Create some buttons
		btnConnect = QPushButton('Connect')
		btnConnect.pressed.connect(self.connect)
		btnConnect.setMaximumSize(150,30)
		btnZoom = QPushButton('Zoom Fit')
		btnZoom.pressed.connect(self.zoomAll)
		btnZoom.setMaximumSize(150,30)
		btnLoad = QPushButton('Load')
		btnLoad.pressed.connect(self.loadFile)
		btnLoad.setMaximumSize(150,30)

		# Add the buttons to a vertical layout
		ButtonLayout = QVBoxLayout()
		ButtonLayout.addWidget(btnConnect)
		ButtonLayout.addWidget(btnZoom)
		ButtonLayout.addWidget(btnLoad)

		MainLayout.addLayout(ButtonLayout)

		centralWidget = QWidget()
		centralWidget.setLayout(MainLayout)
		self.setCentralWidget(centralWidget)

		self.resize(700, 500)
		self.show()

		self.connect()

	def __del__(self):
		print('MainWindow : __del__')
		self.RDK.CloseRoboDK()

	def closeEvent(self):
		print('MainWindow : closeEvent')
		try:
			self.RDK.CloseRoboDK()
			print('Closed RoboDK')
		except:
			print("Wasn't able to close the RDK object")

	def connect(self):
		# Connect to RDK and grab the main window

		RDK_PID = int(self.RDK.Command("MainProcess_ID"))
		print(f'RoboDK main process ID ---------> {RDK_PID}')
		
		rdk_wid_str = "Invalid handle"
		while not rdk_wid_str.isnumeric():
			import time
			time.sleep(0.1)
			rdk_wid_str = self.RDK.Command("MainWindow_ID")
			print("Waiting for the main RoboDK window to show")
			
		# Set the RDK window to eliminate toolbars and menu
		#self.RDK.setFlagsRoboDK( 1 + 2 )
		self.RDK.setWindowState(5)

		RDK_WID = int(rdk_wid_str)
		print(f'RoboDK main window ID ----------> {RDK_WID}')

		TargetID = self.RobotWidget.winId()
		print(f'Target QWidget ID --------------> {TargetID}')

		ctypes.windll.user32.SetParent(RDK_WID, TargetID)
		print('Finished switching the widget target')

	def XresizeEvent(self, Event):
		'''Adjust the size of the RDK window when the main form changes dimensions.
		'''

		print(Event)

	def windowResize(self, Event):
		'''Adjust the size of the RDK window when the widget changes dimensions.
		'''

		NewSize = Event.size()
		W = NewSize.width()
		H = NewSize.height()

		DimensionString = f'{W}x{H}'
		#print(DimensionString)

		#try:
		#	self.RDK.Command('SetSize3D', DimensionString)
		#except Exception as Err:
		#	print(Err)

	def zoomAll(self):
		# Zoom to extents - use 
		self.RDK.Command('FitAll')


	def loadFile(self):
		# Load a file

		Filter = 'RoboDK Files (*.rdk);;All files (*.*)'
		ProjectName = QFileDialog.getOpenFileName(self, 'Select a project to open', '', Filter)[0]

		if ProjectName != '':
			print(ProjectName)
			self.RDK.AddFile(ProjectName)


# Note: this is from a random website.  Remove this later.
class Color(QWidget):

	def __init__(self, color):
		super(Color, self).__init__()
		self.setAutoFillBackground(True)

		palette = self.palette()
		palette.setColor(QPalette.Window, QColor(color))
		self.setPalette(palette)


app = QApplication(sys.argv)
window = MainWindow()
app.aboutToQuit.connect(window.closeEvent)


app.exec()
