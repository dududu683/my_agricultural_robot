import numpy as np
from utils import logger


class ArmController:
    def __init__(self):
        self.current_position = (0, 0, 0)  # 末端执行器位置
        self.joint_angles = [0, 0, 0, 0, 0, 0]  # 六个关节的角度
        self.ik_solver = InverseKinematicsSolver()

    def initialize(self):
        """初始化机械臂"""
        logger.info("初始化机械臂控制系统...")
        self.calibrate()
        logger.info("机械臂初始化完成")

    def calibrate(self):
        """校准机械臂"""
        logger.info("执行机械臂校准...")
        # 移动到初始位置
        self.move_to_home_position()
        logger.info("校准完成")

    def move_to_home_position(self):
        """移动到初始位置"""
        logger.info("移动机械臂到初始位置")
        self.joint_angles = [0, -np.pi / 4, np.pi / 2, 0, np.pi / 4, 0]
        self.current_position = (0.5, 0, 0.5)

    def calculate_trajectory(self, target_position):
        """计算到目标位置的轨迹"""
        logger.info(f"计算到目标位置 {target_position} 的轨迹")

        # 使用逆运动学求解关节角度
        target_angles = self.ik_solver.solve(target_position)

        if target_angles:
            # 生成轨迹 (在实际系统中会更复杂)
            trajectory = [self.joint_angles, target_angles]
            return trajectory
        else:
            logger.error("无法计算轨迹")
            return None

    def execute_trajectory(self, trajectory):
        """执行轨迹"""
        logger.info(f"执行轨迹，包含 {len(trajectory)} 个路径点")

        for angles in trajectory:
            self.set_joint_angles(angles)
            time.sleep(0.1)  # 模拟运动时间

        logger.info("轨迹执行完成")

    def set_joint_angles(self, angles):
        """设置关节角度"""
        if len(angles) != 6:
            logger.error("需要6个关节角度")
            return False

        self.joint_angles = angles
        # 更新末端执行器位置
        self.current_position = self.forward_kinematics(angles)
        logger.debug(f"设置关节角度: {angles}, 末端位置: {self.current_position}")
        return True

    def forward_kinematics(self, angles):
        """正运动学计算"""
        # 简化的正运动学计算
        x = 0.3 * np.cos(angles[0]) + 0.25 * np.cos(angles[0] + angles[1]) + 0.2 * np.cos(
            angles[0] + angles[1] + angles[2])
        y = 0.3 * np.sin(angles[0]) + 0.25 * np.sin(angles[0] + angles[1]) + 0.2 * np.sin(
            angles[0] + angles[1] + angles[2])
        z = 0.1 + 0.2 * np.sin(angles[3]) + 0.15 * np.sin(angles[4])
        return (x, y, z)

    def harvest_fruit(self):
        """执行采摘动作"""
        logger.info("执行采摘动作...")
        # 在实际系统中会控制末端执行器
        # 模拟采摘动作
        time.sleep(1)

        # 模拟采摘成功或失败
        success = np.random.random() > 0.2  # 80%成功率
        if success:
            logger.info("采摘成功")
        else:
            logger.warning("采摘失败")

        return success

    def store_fruit(self):
        """存储果实到货舱"""
        logger.info("存储果实到货舱")
        # 移动到存储位置
        store_position = (0.2, -0.3, 0.1)
        trajectory = self.calculate_trajectory(store_position)
        if trajectory:
            self.execute_trajectory(trajectory)
            # 释放果实
            logger.info("果实已存储")
            return True
        return False

    def get_status(self):
        """获取机械臂状态"""
        return {
            "position": self.current_position,
            "joint_angles": self.joint_angles
        }

    def stop(self):
        """停止机械臂运动"""
        logger.info("机械臂停止")

    def shutdown(self):
        """关闭机械臂系统"""
        logger.info("关闭机械臂控制系统")
        self.move_to_home_position()
