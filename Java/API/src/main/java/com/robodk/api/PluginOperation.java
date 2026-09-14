package com.robodk.api;

/**
 * Operation requested from {@link RoboDK#pluginLoad(String, PluginOperation)}.
 * <p>
 * Unlike most other enums in this package, these values are never sent over the wire as a raw
 * integer: the reference C# and Python implementations use this selector purely locally, to pick
 * which of the {@code "PluginLoad"}/{@code "PluginUnload"} string commands to send (reload is
 * simply an unload followed by a load). It is therefore safe to model as a plain enum without a
 * verified numeric value.
 */
public enum PluginOperation {
    LOAD,
    UNLOAD,
    RELOAD
}
