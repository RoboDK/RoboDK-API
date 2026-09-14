package com.robodk.api.exception;

/**
 * Thrown when an invalid operation is attempted on a {@link com.robodk.api.Mat}, such as
 * building a pose from an array of the wrong size or inverting a non-homogeneous matrix.
 */
public class MatException extends RuntimeException {

    private static final long serialVersionUID = 1L;

    public MatException(String message) {
        super(message);
    }

    public MatException(String message, Throwable cause) {
        super(message, cause);
    }
}
