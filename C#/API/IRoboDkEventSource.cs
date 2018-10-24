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
}