package com.robodk.api.exception;

/**
 * Thrown when the RoboDK API reports an error (invalid item, invalid license, target not
 * reachable, communication problem with RoboDK, ...) or when the client cannot communicate
 * with a RoboDK station.
 */
public class RdkException extends RuntimeException {

    private static final long serialVersionUID = 1L;

    public RdkException(String message) {
        super(message);
    }

    public RdkException(String message, Throwable cause) {
        super(message, cause);
    }
}
