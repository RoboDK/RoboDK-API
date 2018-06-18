#region Namespaces

using RoboDk.API.Model;

#endregion

namespace RoboDk.API
{
    public interface IRoboDKEventSource
    {
        #region Public Methods

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

        private EventResult(bool hasEvent, EventType eventType, IItem item)
        {
            HasEvent = hasEvent;
            EventType = eventType;
            Item = item;
        }

        #endregion

        #region Properties

        public static EventResult None { get; } = new EventResult(false, EventType.NoEvent, null);

        public bool HasEvent { get; }

        public EventType EventType { get; }

        public IItem Item { get; }

        #endregion

        #region Public Methods

        public static EventResult Create(EventType eventType, IItem item)
        {
            return new EventResult(true, eventType, item);
        }

        #endregion
    }
}