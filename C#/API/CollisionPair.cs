namespace RoboDk.API
{
    public class CollisionPair
    {
        public CollisionPair(IItem item1, int robotLinkId1, IItem item2, int robotLinkId2)
        {
            CollisionItem1 = new CollisionItem(item1, robotLinkId1);
            CollisionItem2 = new CollisionItem(item2, robotLinkId2);
        }

        public CollisionPair(IItem item1, IItem item2)
        {
            CollisionItem1 = new CollisionItem(item1);
            CollisionItem2 = new CollisionItem(item2);
        }

        public CollisionItem CollisionItem1 { get; }
        public CollisionItem CollisionItem2 { get; }

        public IItem Item1 => CollisionItem1.Item;

        public IItem Item2 => CollisionItem2.Item;

        public int RobotLinkId1 => CollisionItem1.RobotLinkId;

        public int RobotLinkId2 => CollisionItem2.RobotLinkId;
    }
}
