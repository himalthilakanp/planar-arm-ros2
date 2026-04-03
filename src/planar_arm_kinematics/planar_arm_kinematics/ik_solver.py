import rclpy
from rclpy.node import Node
from planar_arm_interfaces.srv import ComputeIK
import math


class IKSolver(Node):

    def __init__(self):
        super().__init__('ik_solver')

        # Create service
        self.srv = self.create_service(ComputeIK, '/compute_ik', self.compute_ik_callback)

        # Link lengths
        self.L1 = 0.4
        self.L2 = 0.3

        self.get_logger().info("IK Solver Service Ready")

    def compute_ik_callback(self, request, response):

        x = request.target_x
        y = request.target_y

        # Distance to target
        dist_sq = x**2 + y**2
        max_reach = (self.L1 + self.L2)**2

        # ❌ Unreachable case
        if dist_sq > max_reach:
            response.success = False
            response.message = "Target out of reach"
            response.theta1 = 0.0
            response.theta2 = 0.0
            response.theta3 = 0.0
            return response

        try:
            # ✅ Compute theta2
            cos_theta2 = (dist_sq - self.L1**2 - self.L2**2) / (2 * self.L1 * self.L2)

            # Clamp for safety (avoid acos crash)
            cos_theta2 = max(-1.0, min(1.0, cos_theta2))

            theta2 = math.acos(cos_theta2)

            # ✅ Compute theta1
            if abs(x) < 1e-6 and abs(y) < 1e-6:
                # Edge case: origin
                theta1 = 0.0
            else:
                k1 = self.L1 + self.L2 * math.cos(theta2)
                k2 = self.L2 * math.sin(theta2)

                theta1 = math.atan2(y, x) - math.atan2(k2, k1)

            # θ3 fixed
            theta3 = 0.0

            # ✅ Success
            response.success = True
            response.message = "IK solution found"
            response.theta1 = theta1
            response.theta2 = theta2
            response.theta3 = theta3

            self.get_logger().info(
                f"IK -> ({x:.2f},{y:.2f}) → [{theta1:.2f}, {theta2:.2f}]"
            )

        except Exception as e:
            response.success = False
            response.message = f"IK computation error: {str(e)}"
            response.theta1 = 0.0
            response.theta2 = 0.0
            response.theta3 = 0.0

        return response


def main(args=None):
    rclpy.init(args=args)
    node = IKSolver()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
