package com.robodk.api;

/**
 * Type of a station tree {@link Item} (robot, object, target, reference frame, program, ...).
 * <p>
 * The numeric values match the RoboDK API wire protocol and the values used by the reference
 * RoboDK C# and Python APIs, so they must not be changed.
 */
public enum ItemType {

    /** Any item type, used as a wildcard filter when requesting items from the station. */
    ANY(-1),
    STATION(1),
    ROBOT(2),
    FRAME(3),
    TOOL(4),
    OBJECT(5),
    TARGET(6),
    CURVE(7),
    PROGRAM(8),
    INSTRUCTION(9),
    PROGRAM_PYTHON(10),
    MACHINING(11),
    BALLBAR_VALIDATION(12),
    CALIB_PROJECT(13),
    VALID_ISO9283(14),
    FOLDER(17),
    ROBOT_ARM(18),
    CAMERA(19),
    GENERIC(20),
    ROBOT_AXES(21),
    NOTES(22);

    private final int value;

    ItemType(int value) {
        this.value = value;
    }

    /**
     * Returns the integer value used by the RoboDK API wire protocol for this item type.
     */
    public int getValue() {
        return value;
    }

    /**
     * Resolves an {@link ItemType} from its RoboDK API wire protocol integer value.
     *
     * @param value the wire protocol value, as returned by RoboDK
     * @return the matching item type, or {@link #ANY} if the value is unknown
     */
    public static ItemType fromValue(int value) {
        for (ItemType itemType : values()) {
            if (itemType.value == value) {
                return itemType;
            }
        }
        return ANY;
    }
}
