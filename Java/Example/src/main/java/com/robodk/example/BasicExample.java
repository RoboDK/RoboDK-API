package com.robodk.example;

import com.robodk.api.Item;
import com.robodk.api.ItemType;
import com.robodk.api.Mat;
import com.robodk.api.RoboDK;
import com.robodk.api.exception.RdkException;

import java.util.Arrays;
import java.util.List;

/**
 * Small runnable demonstration of the RoboDK API for Java (the {@code API} module).
 * <p>
 * This is a plain {@code main} method rather than a test: it opens a real TCP connection to a
 * running RoboDK station, so it is meant to be run (and stepped through in a debugger) with
 * RoboDK open on the same machine, not executed as part of a build.
 * <p>
 * To run it:
 * <ol>
 *     <li>Start RoboDK.</li>
 *     <li>Run this class's {@code main} method (from IntelliJ IDEA, or with
 *         {@code mvn -pl Example -am exec:java}).</li>
 * </ol>
 */
public final class BasicExample {

    private BasicExample() {
    }

    public static void main(String[] args) {
        try (RoboDK robodk = new RoboDK()) {
            if (!robodk.connect()) {
                System.err.println("Could not connect to RoboDK. Is it running?");
                return;
            }

            System.out.println("Connected to RoboDK " + robodk.version()
                    + " (API version " + robodk.getApiVersion() + ", build " + robodk.getRoboDKBuild() + ")");

            List<String> robotNames = robodk.getItemListNames(ItemType.ROBOT);
            System.out.println("Robots in the station: " + robotNames);

            Item robot = robodk.getItemByName("", ItemType.ROBOT);
            if (!robot.isValid()) {
                System.out.println("No robot found in the open station. Add one and re-run this example.");
                return;
            }

            System.out.println("First robot found: " + robot.getName());
            System.out.println("Current joints: " + Arrays.toString(robot.getJoints()));
            System.out.println("Current pose:\n" + robot.getPose());

            // A quick tour of Mat: build a pose 100 mm above the robot's current pose,
            // rotated 90 degrees around Z, and print it out (this does not move the robot).
            Mat currentPose = robot.getPose();
            Mat offsetPose = Mat.offset(currentPose, 0, 0, 100, 0, 0, 90);
            System.out.println("Offset pose (100 mm up, 90 deg around Z):\n" + offsetPose);

        } catch (RdkException e) {
            System.err.println("RoboDK API error: " + e.getMessage());
        }
    }
}
