#region Namespaces

using RoboDk.API.Model;

#endregion

namespace RoboDk.API
{
    public interface IRoboDKEventSource
    {
        #region Public Methods

        bool Connected { get; }

        /// <summary>
        /// Wait for a new RoboDK event. This function blocks until a new RoboDK event occurs.
        /// </summary>
        /// <param name="timeout"></param>
        /// <returns></returns>
        EventResult WaitForEvent(int timeout = 1000);

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

        public ObjectSelectionType ObjectSelectionType { get; }

        public int ShapeId { get; }

        public Mat ClickedOffset { get; }
    }

    public class KeyPressedEventResult : EventResult
    {
        public enum KeyPressState
        {
            Released = 0,
            Pressed = 1
        }

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
    }
}