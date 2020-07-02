# This example shows how to implement RoboDK's event loop

from robolink import *

EVENT_SELECTION_TREE_CHANGED = 1
EVENT_ITEM_MOVED = 2 # obsolete after RoboDK 4.2.0. Use EVENT_ITEM_MOVED_POSE instead
EVENT_REFERENCE_PICKED = 3
EVENT_REFERENCE_RELEASED = 4
EVENT_TOOL_MODIFIED = 5
EVENT_CREATED_ISOCUBE = 6
EVENT_SELECTION_3D_CHANGED = 7
EVENT_3DVIEW_MOVED = 8
EVENT_ROBOT_MOVED = 9
EVENT_KEY = 10
EVENT_ITEM_MOVED_POSE = 11
EVENT_COLLISIONMAP_RESET=12
EVENT_COLLISIONMAP_TOO_LARGE=13
EVENT_CALIB_MEASUREMENT=14

class RobolinkEvents(Robolink):
    def EventsListen(self):
        """Start this connection as an event communication channel. 
        Use EventsLoop to wait for a new event or use EventsLoop as an example to implement an event loop."""
        try:
        #if True:
            import socket
            #self.COM.close()
            self.COM = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #if self.NODELAY:
            #    self.COM.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                
            self.COM.connect((self.IP, self.PORT))                
            connected = self._is_connected()
            if connected > 0:
                self._verify_connection()
                self.COM.settimeout(self.TIMEOUT)
            else:
                print("Failed to reconnect (1)")
                return False
        except:
            print("Failed to reconnect (2)")
            return False
        
        self._send_line("RDK_EVT") #, _COM_EVT);
        self._send_int(0) # , _COM_EVT);
        response = self._rec_line()#_COM_EVT);
        ver_evt = self._rec_int()#_COM_EVT);
        status = self._rec_int()#_COM_EVT);
        if (response != "RDK_EVT" or status != 0):
            return false
        
        self.COM.settimeout(3600)            
        print("Events loop started")
        return True
        
    
    
    def EventsLoop(self):
        """Run the RoboDK event loop. This is loop blocks until RoboDK finishes execution. Run this loop as a separate thread or create a similar loop to customize the event loop behavior."""        
        while self._is_connected():            
            self.ProcessEvent()
            
        print("Event loop disconnected")
    

    def ProcessEvent(self):
        """Wait and process next event"""
        # Create a separate connection to the API
        rdk = Robolink()
        
        def WaitForEvent():
            evt = self._rec_int()#_COM_EVT);
            itm = self._rec_item() #_COM_EVT);
            # Important: Change the API channel to the new Robolink connection that does not deal with events
            itm.link = rdk 
            return evt, itm
        
        evt, item = WaitForEvent()
        
        print("")
        print("**** New RoboDK event ****")

        if item.Valid():
            print("  Item: " + item.Name() + " -> Type: " + str(item.type))
        else:
            print("  (Item not applicable)")

        if evt == EVENT_SELECTION_TREE_CHANGED:
            print("Event: Selection changed (the tree was selected)")
        
        elif evt == EVENT_ITEM_MOVED:
            print("Event: Item Moved")
            
        elif evt == EVENT_REFERENCE_PICKED:
            print("Event: Reference Picked")
            
        elif evt == EVENT_REFERENCE_RELEASED:
            print("Event: Reference Released")
            
        elif evt == EVENT_TOOL_MODIFIED:
            print("Event: Tool Modified")
            
        elif evt == EVENT_3DVIEW_MOVED:
            print("Event: 3D view moved") # use ViewPose to retrieve the pose of the camera
            
        elif evt == EVENT_ROBOT_MOVED:
            print("Event: Robot moved")            

        # Important: The following events require consuming additional data from the _COM_EVT buffer
        elif evt == EVENT_SELECTION_3D_CHANGED:
            print("Event: Selection changed");
            # data contains the following information (24 values):
            # pose (16), xyz selection (3), ijk normal (3), picked feature id (1), picked id (1)
            data = self._rec_array().list()
            print(data)
            pose_abs = Mat([data[:4],data[4:8],data[8:12],data[12:16]]).tr()
            xyz = [ data[16], data[17], data[18] ]
            ijk = [ data[19], data[20], data[21] ]
            feature_type = int(data[22])
            feature_id = int(data[23])
            print("Additional event data - Absolute position (PoseAbs):")
            print(pose_abs)
            print("Additional event data - Point and Normal (point selected in relative coordinates)")
            print(str(xyz[0]) + "," + str(xyz[1]) + "," + str(xyz[2]));
            print(str(ijk[0]) + "," + str(ijk[1]) + "," + str(ijk[2]));
            print("Feature Type and ID");
            print(str(feature_type) + "-" + str(feature_id))
        
        elif evt == EVENT_KEY:
            key_press = self._rec_int()
            key_id = self._rec_int() # Key id as per Qt mappings: https://doc.qt.io/qt-5/qt.html#Key-enum
            modifiers = self._rec_int() # Modifier bits as per Qt mappings: https://doc.qt.io/qt-5/qt.html#KeyboardModifier-enum
            print("Event: Key pressed: " + str(key_id) + " " + ("Pressed" if (key_press > 0) else "Released") + ". Modifiers: " + str(modifiers))
        
        elif evt == EVENT_ITEM_MOVED_POSE:
            nvalues = self._rec_int();
            pose_rel = self._rec_pose();
            if (nvalues > 16):
                # future compatibility
                pass
                
            print("Event: item moved. Relative pose: " + str(pose_rel))
            
            
        elif evt == EVENT_CALIB_MEASUREMENT:
            print("Event: Robot calibration measurement change")
            data = self._rec_array().list()
            status = data[0]        # Measurement status (see below)
            measure_id = data[1]    # Number id (first measurement is 1)
            
            move_started = (status == 0)        # True if the robot is moving to the next point
            move_done = (status == 1)           # True if the robot completed the movement
            measurement_done = (status == 2)    # True if the measurement is done            
            
            # Save the calibration table as a CSV file (Important: the first line should be ignored)
            table = item.setParam("SaveTableCalib", rdk.getParam("PATH_OPENSTATION") + "/CalibValues.csv")            
        
        else:
            print("Unknown event ID:" + str(evt))
        
        return True
        
        
RDKEVT = RobolinkEvents()
RDKEVT.EventsListen()
RDKEVT.EventsLoop()





