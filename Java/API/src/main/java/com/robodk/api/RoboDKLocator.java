package com.robodk.api;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Locates the RoboDK executable on the current machine, without any third-party dependency.
 * <p>
 * This mirrors {@code getPathRoboDK()} from the reference RoboDK Python API
 * ({@code robolink.py}), which is the only reference implementation that supports more than
 * Windows: the C# API only looks up the Windows registry
 * ({@code RoboDK.RoboDKInstallPath()}, backed by {@code Microsoft.Win32.Registry}).
 */
final class RoboDKLocator {

    private static final Pattern REG_INSTDIR_PATTERN =
            Pattern.compile("INSTDIR\\s+REG_SZ\\s+(.+)", Pattern.CASE_INSENSITIVE);

    private RoboDKLocator() {
    }

    /** The operating system families this locator knows how to handle. */
    enum OperatingSystem {
        WINDOWS,
        LINUX,
        MACOS,
        OTHER
    }

    /** Detects the operating system family this JVM is running on. */
    static OperatingSystem currentOperatingSystem() {
        String name = System.getProperty("os.name", "").toLowerCase(Locale.ROOT);
        if (name.contains("win")) {
            return OperatingSystem.WINDOWS;
        }
        if (name.contains("mac") || name.contains("darwin")) {
            return OperatingSystem.MACOS;
        }
        if (name.contains("nux") || name.contains("nix")) {
            return OperatingSystem.LINUX;
        }
        return OperatingSystem.OTHER;
    }

    /**
     * Attempts to find the RoboDK executable for the current operating system.
     *
     * @return the absolute path to the RoboDK executable, or {@code null} if none was found
     */
    static String findExecutable() {
        switch (currentOperatingSystem()) {
            case WINDOWS:
                return findOnWindows();
            case LINUX:
                return findOnLinux();
            case MACOS:
                return findOnMacOs();
            default:
                return null;
        }
    }

    // ------------------------------------------------------------------------------------
    // Windows: HKLM\SOFTWARE\RoboDK\INSTDIR, falling back to C:\RoboDK\bin\RoboDK.exe
    // ------------------------------------------------------------------------------------

    private static String findOnWindows() {
        String installDir = readWindowsInstallDirFromRegistry();
        if (installDir != null) {
            File exe = new File(installDir, "bin\\RoboDK.exe");
            if (exe.isFile()) {
                return exe.getPath();
            }
        }

        File defaultExe = new File("C:\\RoboDK\\bin\\RoboDK.exe");
        return defaultExe.isFile() ? defaultExe.getPath() : null;
    }

    /**
     * Reads {@code HKLM\SOFTWARE\RoboDK\INSTDIR} using the {@code reg.exe} command that ships
     * with every Windows install. This is the same registry value the RoboDK installer writes
     * and that the C# and Python reference APIs read, just via the OS's own command-line tool
     * instead of an in-process registry binding (the JDK has none, and adding one would mean a
     * third-party dependency).
     */
    private static String readWindowsInstallDirFromRegistry() {
        try {
            Process process = new ProcessBuilder(
                    "reg", "query", "HKLM\\SOFTWARE\\RoboDK", "/v", "INSTDIR")
                    .redirectErrorStream(true)
                    .start();
            String output = readAll(process);
            waitForQuietly(process);

            Matcher matcher = REG_INSTDIR_PATTERN.matcher(output);
            if (matcher.find()) {
                return matcher.group(1).trim();
            }
            return null;
        } catch (IOException e) {
            // reg.exe not on PATH, or the key does not exist: fall back to the default path.
            return null;
        }
    }

    // ------------------------------------------------------------------------------------
    // Linux: ~/RoboDK/bin/RoboDK
    // ------------------------------------------------------------------------------------

    private static String findOnLinux() {
        File exe = new File(userHome(), "RoboDK/bin/RoboDK");
        return exe.isFile() ? exe.getPath() : null;
    }

    // ------------------------------------------------------------------------------------
    // macOS: ~/Applications/RoboDK.app/..., falling back to ~/RoboDK/RoboDK.app/...
    // ------------------------------------------------------------------------------------

    private static String findOnMacOs() {
        File userApplications = new File(userHome(), "Applications/RoboDK.app/Contents/MacOS/RoboDK");
        if (userApplications.isFile()) {
            return userApplications.getPath();
        }

        File defaultInstall = new File(userHome(), "RoboDK/RoboDK.app/Contents/MacOS/RoboDK");
        return defaultInstall.isFile() ? defaultInstall.getPath() : null;
    }

    // ------------------------------------------------------------------------------------
    // Helpers
    // ------------------------------------------------------------------------------------

    private static String userHome() {
        return System.getProperty("user.home", "");
    }

    private static String readAll(Process process) throws IOException {
        StringBuilder output = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8))) {
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append('\n');
            }
        }
        return output.toString();
    }

    private static void waitForQuietly(Process process) {
        try {
            process.waitFor();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
