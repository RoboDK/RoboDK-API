using System;


namespace RoboDk.API.Model
{
    /// <summary>
    /// 
    /// </summary>
    [Flags]
    public enum DisplayRefType
    {
        /// <summary>
        /// Set the default behavior
        /// </summary>
        DEFAULT = -1,

        /// <summary>
        /// No axis to display
        /// </summary>
        NONE = 0,

        /// <summary>
        /// Display all reference frames
        /// </summary>
        ALL = 0x1FF, /*0b111111111,*/
        
        /// <summary>
        /// Display the translation/rotation along the XY plane (holds Z axis the same)
        /// </summary>
        TXY_RZ = 0x63, /*0b001100011,*/

        /// <summary>
        /// Display the translation X axis
        /// </summary>
        TX = 0x1, /*0b001,*/

        /// <summary>
        /// Display the translation Y axis
        /// </summary>
        TY = 0x2, /*0b010,*/

        /// <summary>
        /// Display the translation Z axis
        /// </summary>
        TZ = 0x4, /*0b100,*/

        /// <summary>
        /// Display the rotation X axis
        /// </summary>
        RX = 0x8, /*0b001000,*/

        /// <summary>
        /// Display the rotation Y axis
        /// </summary>
        RY = 0x10, /*0b010000,*/

        /// <summary>
        /// Display the rotation Z axis
        /// </summary>
        RZ = 0x20, /*0b100000,*/

        /// <summary>
        /// Display the plane translation along XY plane
        /// </summary>
        PXY = 0x40, /*0b001000000,*/

        /// <summary>
        /// Display the plane translation along XZ plane
        /// </summary>
        PXZ = 0x80, /*0b010000000,*/

        /// <summary>
        /// Display the plane translation along YZ plane
        /// </summary>
        PYZ = 0x100, /*0b100000000*/

    }
}
