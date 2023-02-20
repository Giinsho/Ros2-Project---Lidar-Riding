from pathlib import Path
import rclpy
from rclpy.time import Time
from rclpy.action import ActionServer
from rclpy.node import Node
from action_bot.action import Move
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path
import os


class MoveActionServer(Node):
    status = False

    def __init__(self):
        super().__init__('server_bot')
        self._publisher = self.create_publisher(PoseStamped, '/goal_pose', 10)
        self._action_server = ActionServer(
            self,
            Move,
            'move',
            self.execute_callback)
        self.get_logger().info("Server is running")

    def goToThePoint(self, type, goal_handle):
        # x_dol , x_gora, Y_lewo , y _ prawo
        #pokoje = ['kanciapa': [20.0, 6.0, -8.0, -4.0], 'sypialnia': [20.0, 6.0, 8.0, 4.0], 'kuchnia': [-10.0, -8.0, -8.0, -4.0], 'korytarz': [2.0, -2.0, -2.0, 2.0], 'goscinny': [-9.0, -12.0, -1.0, 4.0], 'przedsionek': [5.0, -2.0, 11.0, 13.0], 'wyjscie': [4.5, 1.0, 16.0, 18.0]]
        status = False
        if type.startswith("kanciapa"):
            status = self.move(goal_handle, 10.0, -6.0, 0.0)
        elif type.startswith("sypialnia"):
            status = self.move(goal_handle, 10.0, 6.0, 0.0)
        elif type.startswith("kuchnia"):
            status = self.move(goal_handle, -5.0, -6.0, 0.0)
        elif type.startswith("korytarz"):
            status = self.move(goal_handle, 0.0, 0.0, 0.0)
        elif type.startswith("goscinny"):
            status = self.move(goal_handle, -10.0, 5.0, 0.0)
        elif type.startswith("przedsionek"):
            status = self.move(goal_handle, 3.0, 12.0, 0.0)
        elif type.startswith("wyjscie"):
            status = self.move(goal_handle, 4.0, 16.0, 0.0)
        elif type[0].startswith('x'):
            variables = type.split(" ")
            x = variables[0].split(":")
            val_x = x[1]
            print(x)
            y = variables[1].split(":")
            val_y = y[1]
            print(y)
            status = self.move(goal_handle, float(val_x), float(val_y), 0.0)
        return status

    def execute_callback(self, goal_handle):
        status = False
        type = goal_handle.request.request

        status = self.goToThePoint(type, goal_handle)

        goal_handle.succeed()
        result = Move.Result()
        result.finish = status
        return result

    def move(self, goal_handle, x, y, z):
        msg = PoseStamped()
        msg.header.frame_id = "map"
        msg.pose.position.x = x
        msg.pose.position.y = y
        msg.pose.position.z = z
        msg.pose.orientation.x = 0.0
        msg.pose.orientation.y = 0.0
        msg.pose.orientation.z = 0.0
        msg.pose.orientation.w = 1.0

        self._publisher.publish(msg)
        return True


def main(args=None):
    rclpy.init(args=args)
    server_bot = MoveActionServer()
    rclpy.spin(server_bot)


if __name__ == '__main__':
    main()
