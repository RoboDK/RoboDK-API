# This example shows how to modify settings related to robot machining and program events such as the speed. 
# The new values apply to all robot machining and curve follow projects in the station

# More information here:
# https://robodk.com/doc/en/PythonAPI/examples.html#robot-machining-settings

from robodk.robolink import *  # RoboDK API
from robodk import roboapps, robodialogs

from PySide6.QtWidgets import QApplication, QMainWindow, QLineEdit, QProgressBar, QDoubleSpinBox, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout
from PySide6 import QtCore

RDK = Robolink()

class set_speed(QMainWindow):

    def __init__(self):

        super(set_speed, self).__init__()
        
        self.rapid_edit = QDoubleSpinBox()
        self.op_edit = QDoubleSpinBox()
        self.rapid_edit.setRange(0,1000000)
        self.op_edit.setRange(0,1000000)
        
        
        rapid_w = QWidget()
        frm_layout = QFormLayout()
        rapid_w.setLayout(frm_layout) # self is the parent widget

        frm_layout.addRow('Rapid Speed (mm/s):', self.rapid_edit)
        frm_layout.addRow('Operation speed (mm/s):', self.op_edit)
        frm_w = QWidget()
        frm_w.setLayout(frm_layout)

        upd_layout = QHBoxLayout()
        upd_btn = QPushButton('Update')
        self.upd_bar = QProgressBar()
        upd_layout.addWidget(upd_btn)
        upd_layout.addWidget(self.upd_bar)
        upd_w = QWidget()
        upd_w.setLayout(upd_layout)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(frm_w)
        main_layout.addWidget(upd_w)

        main_w = QWidget()
        main_w.setLayout(main_layout)

        self.setWindowTitle("Update project speeds")
        self.setCentralWidget(main_w)
        
        mach_list = RDK.ItemList(ITEM_TYPE_MACHINING)
        if len(mach_list) == 0:
            self.rapid_edit.setValue(1000)
            self.op_edit.setValue(50)            
            
        else:            
            op_speed = mach_list[0].setParam("Machining")["SpeedOperation"]
            rapid_speed = mach_list[0].setParam("ProgEvents")["RapidSpeed"]
            
            self.rapid_edit.setValue(rapid_speed)
            self.op_edit.setValue(op_speed)
            
        upd_btn.clicked.connect(self.update)      

    def update(self):
        
        mach_list = RDK.ItemList(ITEM_TYPE_MACHINING)
        len_mach_list = len(mach_list)
        if len_mach_list == 0:
            return
        
        self.upd_bar.setMaximum(len_mach_list)
        i  =  0
        for m in mach_list:

            # Read Program Events settings for selected machining project
            machiningsettings = m.setParam("Machining")
            
            # Read Program Events settings for selected machining project
            progevents = m.setParam("ProgEvents")
            
            # Update one value, for example, make the normals not visible
            MachiningUpdate = {}
            MachiningUpdate["RapidSpeed"] = float(self.rapid_edit.value())
            MachiningUpdate["SpeedOperation"] = float(self.op_edit.value())
            
            print("Updating robot machining settings: %s" % m.Name())
            status = m.setParam("Machining", MachiningUpdate)
            print(status)

            # Update some values, for example, set custom tool change and set arc start and arc end commands
            ProgEventsUpdate = {}
            ProgEventsUpdate["RapidSpeed"] = float(self.rapid_edit.value())
            
            print("Updating program events: %s" % m.Name())
            status = m.setParam("ProgEvents", ProgEventsUpdate)
            print(status)

            m.setParam("UpdatePath")  # recalculate toolpath

            # Update machining project (validates robot feasibility)
            status = m.Update()

            i+=1
            self.upd_bar.setValue(i)
            

if __name__ == "__main__":

    #RDK = Robolink()
    if getattr(robodialogs, 'QT_API', None) == 'PySide6':
        app = roboapps.get_qt_app(True, True)  # QApplication with the RoboDK icon and theme
    else:
        # The robodk package in use predates 6.1.0 and runs its dialogs on PySide2: its QApplication would be a Qt 5 one,
        # and this Qt 6 window would fail with "QWidget: Must construct a QApplication before a QWidget".
        print('The robodk package in use does not support PySide6 (update it to 6.1.0 or newer). Running without the RoboDK theme.')
        app = QApplication.instance() or QApplication([])
    
    window = set_speed()
    window.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint)
    window.show()

    app.exec()



