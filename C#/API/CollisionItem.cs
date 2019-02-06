namespace RoboDk.API
{
    public class CollisionItem
    {
        public CollisionItem(IItem item, int robotLinkId = 0)
        {
            Item = item;
            RobotLinkId = robotLinkId;
        }

        public IItem Item { get; }

        public int RobotLinkId { get; }
    }
}