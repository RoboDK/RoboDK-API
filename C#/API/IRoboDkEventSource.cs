#region Namespaces

using RoboDk.API.Model;

#endregion

namespace RoboDk.API
{
    public interface IRoboDKEventSource
    {
        #region Properties

        /// <summary>
        /// RoboDK Event protocol version.
        /// </summary>
        int EventProtocolVersion { get; }

        #endregion

        #region Public Methods

        /// <summary>
        /// Wait for a new RoboDK event. This function blocks until a new RoboDK event occurs.
        /// In case of a timeout EventType.NoEvent will be returned.
        /// For any other socket error the method re-throws the socket exception.
        /// </summary>
        /// <param name="timeout"></param>
        /// <returns>Event received from RoboDK.</returns>
        EventResult WaitForEvent(int timeout = 1000);

        /// <summary>
        /// Close Event Channel.
        /// An ObjectDisposedException will be thrown if WaitForEvent is called after closing the event channel.
        /// </summary>
        void Close();

        #endregion
    }

    public class EventResult
    {
        #region Constructors

        public EventResult(EventType eventType, IItem item)
        {
            EventType = eventType;
            Item = item;
        }

        #endregion

        #region Properties

        public EventType EventType { get; }

        public IItem Item { get; }

        #endregion
    }

    public class SelectionChangedEventResult : EventResult
    {
        #region Constructors

        public SelectionChangedEventResult(
            IItem item,
            ObjectSelectionType objectSelection,
            int shapeId,
            Mat clickedOffset) : base(EventType.Selection3DChanged, item)
        {
            ObjectSelectionType = objectSelection;
            ShapeId = shapeId;
            ClickedOffset = clickedOffset;
        }

        #endregion

        #region Properties

        public ObjectSelectionType ObjectSelectionType { get; }

        public int ShapeId { get; }

        public Mat ClickedOffset { get; }

        #endregion
    }

    public class ItemMovedEventResult : EventResult
    {
        #region Constructors

        /// <summary>
        /// Item moved event
        /// </summary>
        /// <param name="item"></param>
        /// <param name="relativePose">Relative pose (pose with respect to parent)</param>
        public ItemMovedEventResult(
            IItem item,
            Mat relativePose) : base(EventType.ItemMovedPose, item)
        {
            RelativePose = relativePose;
        }

        #endregion

        #region Properties

        public Mat RelativePose { get; }

        #endregion
    }

    public class KeyPressedEventResult : EventResult
    {
        public enum KeyPressState
        {
            Released = 0,
            Pressed = 1
        }

        #region Constructors

        /// <summary>
        /// Key pressed event.
        /// </summary>
        /// <param name="item"></param>
        /// <param name="keyId">Key id as per Qt mappings: https://doc.qt.io/qt-5/qt.html#Key-enum </param>
        /// <param name="keyState">Pressed or Released</param>
        /// <param name="modifiers">Modifier bits as per Qt mappings: https://doc.qt.io/qt-5/qt.html#KeyboardModifier-enum </param>
        public KeyPressedEventResult(
            IItem item,
            int keyId,
            KeyPressState keyState,
            int modifiers)
            : base(EventType.KeyPressed, item)
        {
            KeyId = keyId;
            KeyState = keyState;
            Modifiers = modifiers;
        }

        #endregion

        #region Properties

        /// <summary>
        /// Key id as per Qt mappings: https://doc.qt.io/qt-5/qt.html#Key-enum 
        /// </summary>
        public int KeyId { get; }

        /// <summary>
        /// Is key pressed or released
        /// </summary>
        public KeyPressState KeyState { get; }

        /// <summary>
        /// Modifier bits as per Qt mappings: https://doc.qt.io/qt-5/qt.html#KeyboardModifier-enum 
        /// </summary>
        public int Modifiers { get; }

        #endregion
    }
}