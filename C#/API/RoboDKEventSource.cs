#region Namespaces

using System;
using System.Diagnostics;
using System.Linq;
using System.Net.Sockets;
using RoboDk.API.Model;

#endregion

namespace RoboDk.API
{
    internal sealed class RoboDKEventSource : IRoboDKEventSource
    {
        #region Fields

        private readonly RoboDK _roboDkApiConnection;
        private readonly RoboDK _roboDkEventConnection;

        #endregion

        #region Constructors

        internal RoboDKEventSource(IRoboDK roboDk)
        {
            _roboDkApiConnection = (RoboDK)roboDk;
            _roboDkEventConnection = (RoboDK)_roboDkApiConnection.CloneRoboDkConnection(RoboDK.ConnectionType.Event);
        }

        #endregion

        #region Properties

        public int EventProtocolVersion => _roboDkEventConnection.EventChannelVersion;

        #endregion

        #region Public Methods

        public EventResult WaitForEvent(int timeout = 1000)
        {
            try
            {
                _roboDkEventConnection.ReceiveTimeout = timeout;
                var eventType = (EventType)_roboDkEventConnection.rec_int();
                var item = _roboDkEventConnection.rec_item(_roboDkApiConnection);

                // We are in context of an asynchronous background thread
                // Do not try to read any items properties or call any other RoboDK method.
                // e.g.:    itemName = item.Name(); -> Call may conflict with other RoboDK Calls running in the main thread!!!

                //Debug.WriteLine($"{_roboDkApiConnection.Name}: RoboDK event({(int)eventType}): {eventType.ToString()}. Port:{_roboDkEventConnection.RoboDKClientPort}, {_roboDkApiConnection.RoboDKClientPort}");

                switch (eventType)
                {
                    case EventType.NoEvent:
                    case EventType.SelectionTreeChanged:
                    case EventType.ItemMoved:
                    // this should never happen
                    case EventType.ReferencePicked:
                    case EventType.ReferenceReleased:
                    case EventType.ToolModified:
                    case EventType.IsoCubeCreated:
                    case EventType.Moved3DView:
                    case EventType.Selection3DClick:
                    case EventType.RobotMoved:
                        return new EventResult(eventType, item);

                    case EventType.ItemMovedPose:
                        var nvalues = _roboDkEventConnection.rec_int(); // this is 16 for RoboDK v4.2.0
                        var relativePose = _roboDkEventConnection.rec_pose();
                        if (nvalues > 16)
                        {
                            // future compatibility
                        }

                        return new ItemMovedEventResult(item, relativePose);

                    case EventType.Selection3DChanged:
                        var data = _roboDkEventConnection.rec_array();
                        var poseAbs = new Mat(data, true);
                        var xyzijk = data.Skip(16).Take(6).ToArray(); // { data[16], data[17], data[18], data[19], data[20], data[21] };
                        var clickedOffset = new Mat(xyzijk);
                        var featureType = (ObjectSelectionType)Convert.ToInt32(data[22]);
                        var featureId = Convert.ToInt32(data[23]);

                        Debug.WriteLine("Additional event data - Absolute position (PoseAbs):");
                        Debug.WriteLine($"{poseAbs}");
                        Debug.WriteLine($"Selected Point: {xyzijk[0]}, {xyzijk[1]}, {xyzijk[2]}"); // point selected in relative coordinates
                        Debug.WriteLine($"Normal Vector : {xyzijk[3]}, {xyzijk[4]}, {xyzijk[5]}");
                        Debug.WriteLine($"Feature Type:{featureType} and ID:{featureId}");

                        return new SelectionChangedEventResult(item, featureType, featureId, clickedOffset);

                    case EventType.KeyPressed:
                        var keyStateParam = _roboDkEventConnection.rec_int(); // 1 = key pressed, 0 = key released
                        var keyId = _roboDkEventConnection.rec_int(); // Key id as per Qt mappings: https://doc.qt.io/qt-5/qt.html#Key-enum
                        var modifiers = _roboDkEventConnection.rec_int(); // Modifier bits as per Qt mappings: https://doc.qt.io/qt-5/qt.html#KeyboardModifier-enum

                        var keyState = keyStateParam > 0 ? KeyPressedEventResult.KeyPressState.Pressed : KeyPressedEventResult.KeyPressState.Released;
                        Debug.WriteLine($"Key_id({keyId}) {keyState.ToString()}  Modifiers: 0x{modifiers:X8}");

                        return new KeyPressedEventResult(item, keyId, keyState, modifiers);

                    case EventType.CollisionMapChanged:
                        //Debug.WriteLine($"RoboDK Event: {eventType}");
                        return new EventResult(EventType.CollisionMapChanged, null);

                    case EventType.CollisionMapTooLarge:
                        //Debug.WriteLine($"RoboDK Event: {eventType}");
                        return new EventResult(EventType.CollisionMapTooLarge, null);

                    case EventType.NewMeasurement:
                        //Debug.WriteLine($"RoboDK Event: {eventType}");
                        int ignored = _roboDkEventConnection.rec_int(); // 1 = key pressed, 0 = key released
                        int measurementId = _roboDkEventConnection.rec_int(); // 1 = key pressed, 0 = key released
                        return new EventResult(EventType.NewMeasurement, null);

                    default:
                        Debug.WriteLine($"unknown RoboDK Event: {eventType}");

                        // In debug target we fail -> Exception.
                        // In Release we send a NoEvent event
                        Debug.Fail($"unknown RoboDK Event: {eventType}");
                        return new EventResult(EventType.NoEvent, null);
                }
            }
            catch (SocketException socketException)
            {
                return new EventResult(EventType.NoEvent, null);
            }
            catch (ObjectDisposedException e)
            {
                return new EventResult(EventType.NoEvent, null);
            }
        }

        public void Close()
        {
            _roboDkEventConnection.Dispose();
        }

        #endregion

    }
}