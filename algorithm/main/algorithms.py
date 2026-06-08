
import numpy as np
import math
from utils import logger


class RRTPlanner:
    def __init__(self, max_iter=1000, step_size=0.5):
        self.max_iter = max_iter
        self.step_size = step_size

    def plan(self, start, goal, obstacles):
        """RRT*路径规划算法"""
        logger.info(f"使用RRT*规划从 {start} 到 {goal} 的路径")

        # 在实际系统中会有完整的RRT*实现
        # 这里返回模拟路径

        # 简单直线路径
        path = [start]

        # 添加中间点
        if abs(start[0] - goal[0]) > 1 or abs(start[1] - goal[1]) > 1:
            mid_point = ((start[0] + goal[0]) / 2, (start[1] + goal[1]) / 2)
            path.append(mid_point)

        path.append(goal)

        return path

    def distance(self, p1, p2):
        """计算两点间距离"""
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def steer(self, from_point, to_point, step_size):
        """生成从起点到终点的步进点"""
        d = self.distance(from_point, to_point)
        if d < step_size:
            return to_point

        theta = math.atan2(to_point[1] - from_point[1], to_point[0] - from_point[0])
        return (
            from_point[0] + step_size * math.cos(theta),
            from_point[1] + step_size * math.sin(theta)
        )


class InverseKinematicsSolver:
    def __init__(self):
        # 机械臂参数
        self.link_lengths = [0.3, 0.25, 0.2, 0.15, 0.1]

    def solve(self, target_position):
        """逆运动学求解"""
        logger.info(f"求解逆运动学: 目标位置 {target_position}")

        x, y, z = target_position

        # 简化的逆运动学计算
        # 计算基座旋转角度
        theta1 = math.atan2(y, x)

        # 计算第二个关节角度
        d = math.sqrt(x ** 2 + y ** 2) - self.link_lengths[3]
        h = z - self.link_lengths[0]
        L = math.sqrt(d ** 2 + h ** 2)

        # 检查是否可达
        if L > (self.link_lengths[1] + self.link_lengths[2]):
            logger.warning("目标位置超出工作空间")
            return None

        # 计算角度
        alpha = math.atan2(h, d)
        beta = math.acos(
            (self.link_lengths[1] ** 2 + L ** 2 - self.link_lengths[2] ** 2) /
            (2 * self.link_lengths[1] * L)
        )
        theta2 = alpha + beta

        gamma = math.acos(
            (self.link_lengths[1] ** 2 + self.link_lengths[2] ** 2 - L ** 2) /
            (2 * self.link_lengths[1] * self.link_lengths[2])
        )
        theta3 = gamma - math.pi

        # 简化末端执行器角度
        theta4 = 0
        theta5 = math.pi / 2
        theta6 = 0

        angles = [theta1, theta2, theta3, theta4, theta5, theta6]
        logger.info(f"逆运动学解: {angles}")
        return angles

