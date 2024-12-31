import unittest

from robodk import robomath
import random


def q_norm(q):
    """Returns the norm of a qaternion"""
    return robomath.sqrt(q[0] * q[0] + q[1] * q[1] + q[2] * q[2] + q[3] * q[3])


SIN45 = robomath.sin(robomath.pi / 4.)
Q_NOISE = 1e-9  # Quaternion noise
Q_NORM_TOLERANCE = max(1e-10, Q_NOISE * 10)  # Norm cant be more precise than the noise..
M_SIMILAR_TOLERANCE = 1e-5  # deg+mm
M_NOISE_ERR_MM = 1e-10
M_NOISE_ERR_RAD = 1e-3


class TestQuaternion(unittest.TestCase):

    def setUp(self):
        H = []
        H.append(robomath.eye(4))  # z with z
        H.append(robomath.rotx(robomath.pi))  # Z with z inversed
        H.append(robomath.roty(-robomath.pi / 2))  # x with z
        H.append(robomath.roty(robomath.pi / 2))  # x with z inversed
        H.append(robomath.rotx(robomath.pi / 2))  # y with z
        H.append(robomath.rotx(-robomath.pi / 2))  # y with z inversed

        H.append(robomath.KUKA_2_Pose([0, 0, 0, 180, 0, 90]))
        H.append(robomath.KUKA_2_Pose([0, 0, 0, 0, 45, 180]))
        H.append(robomath.KUKA_2_Pose([0, 0, 0, -180, 45, 0]))
        H.append(robomath.KUKA_2_Pose([0, 0, 0, -180, -45, 0]))

        H.append(robomath.TxyzRxyz_2_Pose([0, 0, 0, -robomath.pi, -robomath.pi / 4, 0]))
        H.append(robomath.TxyzRxyz_2_Pose([0, 0, 0, -robomath.pi, robomath.pi / 4, 0]))

        h = robomath.eye(4)
        h.setVX([SIN45, 0, -SIN45])
        h.setVY([0, -1, 0])
        h.setVZ([-SIN45, 0, -SIN45])
        H.append(h)

        h = robomath.eye(4)
        h.setVX([SIN45, 0, SIN45])
        h.setVY([0, -1, 0])
        h.setVZ([SIN45, 0, -SIN45])
        H.append(h)

        for h in list(H):
            H.append(h * robomath.rotz(robomath.pi / 2))
            H.append(h * robomath.rotz(robomath.pi / 4))
            H.append(h * robomath.rotz(robomath.pi / 6))

        for h in list(H):
            H.append(h * robomath.rotx(random.uniform(0, 1)) * robomath.roty(random.uniform(0, 1)) * robomath.rotz(random.uniform(0, 1)))

        self.H = H

        return super().setUp()

    def test_matrix_identity(self):
        h0 = robomath.eye(4)
        self.assertTrue(h0.isHomogeneous())
        q = robomath.pose_2_quaternion(h0)
        h1 = robomath.quaternion_2_pose(q)
        self.assertEqual(h0, h1)

    def test_quaterion_identity(self):
        q0 = [1, 0, 0, 0]
        h = robomath.quaternion_2_pose(q0)
        self.assertTrue(h.isHomogeneous())
        q1 = robomath.pose_2_quaternion(h)
        self.assertEqual(q0, q1)

    def test_quaternion(self):

        Q_NOISE1 = [Q_NOISE for n in range(4)]
        Q_NOISE2 = [-Q_NOISE for n in range(4)]
        Q_NOISE3 = [[-1, 1][random.randrange(2)] * Q_NOISE for n in range(4)]

        for i, h in enumerate(self.H):
            self.assertTrue(h.isHomogeneous())

            # Pose -> Q
            q = robomath.pose_2_quaternion(h)
            q_norm_err = abs(q_norm(q) - 1)
            self.assertLess(q_norm_err, Q_NORM_TOLERANCE)

            # Pose -> Q -> Pose
            hq = robomath.quaternion_2_pose(q)
            self.assertTrue(hq.isHomogeneous())
            self.assertTrue(robomath.pose_is_similar(h, hq, M_SIMILAR_TOLERANCE), "pose_is_similar greater than " + str(M_SIMILAR_TOLERANCE))
            self.assertTrue(h == hq)

            # Inject numerical error in the quaternions
            for noise in [Q_NOISE1, Q_NOISE2, Q_NOISE3]:

                # Pose -> Q -> Q+Noise
                q_noise = [a + b for a, b in zip(q, noise)]
                q_norm_err = abs(q_norm(q_noise) - 1)
                self.assertLess(q_norm_err, Q_NORM_TOLERANCE)

                # Pose -> Q -> Q+Noise -> Pose+Noise
                h_noise = robomath.quaternion_2_pose(q_noise)
                self.assertTrue(h_noise.isHomogeneous())

                # Compare with original Pose
                h2_err = h.inv() * h_noise
                self.assertTrue(h2_err.isHomogeneous())
                mm_err = robomath.norm(h2_err.Pos())
                ang_err = robomath.pose_angle(h2_err)
                self.assertLess(mm_err, M_NOISE_ERR_MM)
                self.assertLess(ang_err, M_NOISE_ERR_RAD)


if __name__ == '__main__':
    import unittest
    unittest.main()
