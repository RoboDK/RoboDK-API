# This example shows how to listen to events
# Listening to events should be done with a dedicated Robolink instance. This same instance should only be used for events.
# Note: Refer to Event_Loop.py example for a more complete example with events

from robolink import *

# List of events that are reported via the event loop
EVENT_PROGSLIDER_CHANGED=20     # A program slider was opened, changed, or closed (RoboDK 5.6.4 required)
EVENT_PROGSLIDER_SET=21         # The index of a program slider changed (RoboDK 5.6.4 required)


class RobolinkEvents(Robolink):
    """Extension of the Robolink class to support events"""
    def __init__(self):
        Robolink.__init__(self)
        self._SliderList = None
        
    def EventsListen(self, filter_events=None):
        """Start this connection as an event communication channel. 
        You can optionally past the list of events you want to listen to. Other events will be ignored.
        Use EventsLoop to wait for a new event or use EventsLoop as an example to implement an event loop."""
        try:
            import socket
            self.COM = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                
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
        
        if filter_events is None:
            self._send_line("RDK_EVT")
            
        else:
            print("Filtering by desired events (RoboDK v5.6.4 or later required)")
            self._send_line("RDK_EVT_FILTER")
            nevents = len(filter_events)
            self._send_int(nevents)
            for i in range(nevents):
                self._send_int(filter_events[i])
            
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

        if evt == EVENT_PROGSLIDER_CHANGED:
            from robodk import robomath
            self._SliderList = item.setParam("ProgSlider", robomath.Mat(0,0))
            if self._SliderList is not None:
                self._SliderList = self._SliderList.Cols()
                print("Event: The program slider was updated. NUM VALUES: " + str(len(self._SliderList)))
                for jnt_xyz in self._SliderList:
                    print(jnt_xyz)
                    
            else:
                print("Event: The program slider was Deleted")            
            
        elif evt == EVENT_PROGSLIDER_SET:
            from robodk import robomath
            slider_index = self._rec_int()
            print("Event: The program slider index changed. INDEX = " + str(slider_index))
            if self._SliderList is None:
                print("We missed the EVENT_PROGSLIDER_CHANGED event. Recalculating...")
                self._SliderList = item.setParam("ProgSlider", robomath.Mat(0,0))
                self._SliderList = self._SliderList.Cols()
                
            print(self._SliderList[slider_index])
        
        else:
            print("Unknown event ID:" + str(evt))
            raise Exception("Unknown event received. You can filter by desired events.")
        
        return True

# Example to filter for certain events (all other events are not reported)
# Setting an empty list will provide all events
#
WantedEvents = []
WantedEvents.append(EVENT_PROGSLIDER_CHANGED)
WantedEvents.append(EVENT_PROGSLIDER_SET)

RDKEVT = RobolinkEvents()
# RDKEVT.EventsListen() # Listen for all events
RDKEVT.EventsListen(WantedEvents)
RDKEVT.EventsLoop()





