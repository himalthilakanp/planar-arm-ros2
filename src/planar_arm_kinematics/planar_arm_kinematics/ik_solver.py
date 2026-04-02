import rclpy
from rclpy.node import Node
from planar_arm_interfaces.srv import ComputeIK
import math


class IKSolver(Node):

    def __init__(self):
        super().__init__('ik_solver')

        self.srv = self.create_service(
            ComputeIK,
            'compute_ik',
            self.compute_ik_callback)

        self.L1 = 0.4
        self.L2 = 0.3

    def compute_ik_callback(self, request, response):

        x = request.target_x
        y = request.target_y

        r = math.sqrt(x**2 + y**2)

        # Reachability check
        if r > (self.L1 + self.L2):
            response.success = False
            response.message = "Target unreachable"
            return response

        # Compute theta2
        cos_theta2 = (x**2 + y**2 - self.L1**2 - self.L2**2) / (2 * self.L1 * self.L2)

        theta2 = math.acos(cos_theta2)

        # Compute theta1
        theta1 = math.atan2(y, x) - math.atan2(
            self.L2 * math.sin(theta2),
            self.L1 + self.L2 * math.cos(theta2)
        )

        response.success = True
        response.message = "IK solution found"
        response.theta1 = theta1
        response.theta2 = theta2
        response.theta3 = 0.0

        self.get_logger().info(f"IK -> ({x},{y}) → [{theta1:.2f}, {theta2:.2f}]")

        return response


def main(args=None):
    rclpy.init(args=args)
    node = IKSolver()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
