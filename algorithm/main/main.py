

import time
import threading
from navigation import NavigationSystem
from vision import VisionSystem
from arm_control import ArmController
from motor_control import MotorController
from sensors import SensorHub
from utils import logger


class SmartAgriRobot:
    def __init__(self):
        # 初始化各子系统
        self.nav_system = NavigationSystem()
        self.vision_system = VisionSystem()
        self.arm_controller = ArmController()
        self.motor_controller = MotorController()
        self.sensor_hub = SensorHub()

        # 机器人状态
        self.state = "IDLE"
        self.current_task = None
        self.battery_level = 100
        self.operation_mode = "AUTO"  # AUTO or MANUAL

        # 线程控制
        self.running = True
        self.main_thread = threading.Thread(target=self.run)
        self.monitor_thread = threading.Thread(target=self.monitor_system)

    def start(self):
        """启动机器人系统"""
        logger.info("启动智能巡检采摘机器人系统...")
        self.nav_system.initialize()
        self.vision_system.initialize()
        self.arm_controller.initialize()
        self.motor_controller.initialize()
        self.sensor_hub.initialize()

        self.main_thread.start()
        self.monitor_thread.start()
        logger.info("系统启动完成，进入运行状态")

    def run(self):
        """主运行循环"""
        while self.running:
            try:
                # 检查电池状态
                if self.battery_level < 20:
                    logger.warning("电量低于20%，返回充电站")
                    self.return_to_charge()
                    continue

                # 执行当前任务
                if self.state == "IDLE":
                    time.sleep(1)
                    continue

                if self.state == "NAVIGATING":
                    self.execute_navigation()

                elif self.state == "INSPECTING":
                    self.execute_inspection()

                elif self.state == "HARVESTING":
                    self.execute_harvesting()

                elif self.state == "RETURNING":
                    self.execute_return()

                time.sleep(0.1)

            except Exception as e:
                logger.error(f"主循环发生错误: {str(e)}")
                self.emergency_stop()

    def monitor_system(self):
        """系统监控线程"""
        while self.running:
            # 更新传感器数据
            self.update_sensor_data()

            # 检查系统状态
            if self.sensor_hub.check_emergency():
                self.emergency_stop()

            # 更新电池状态
            self.battery_level -= 0.01  # 模拟电量消耗
            if self.battery_level < 10:
                logger.critical("电量严重不足！")
                self.return_to_charge()

            time.sleep(1)

    def update_sensor_data(self):
        """更新传感器数据"""
        # 获取所有传感器数据
        ultrasonic_data = self.sensor_hub.get_ultrasonic_data()
        imu_data = self.sensor_hub.get_imu_data()
        camera_data = self.sensor_hub.get_camera_data()
        motor_status = self.motor_controller.get_status()
        arm_status = self.arm_controller.get_status()

        # 更新导航系统
        self.nav_system.update_sensor_data(
            ultrasonic=ultrasonic_data,
            imu=imu_data,
            camera=camera_data
        )

    def set_task(self, task_type, target=None):
        """设置机器人任务"""
        if task_type == "NAVIGATE":
            if not target:
                logger.error("导航任务需要目标位置")
                return False
            self.current_task = {
                "type": "NAVIGATE",
                "target": target,
                "status": "PENDING"
            }
            self.state = "NAVIGATING"
            return True

        elif task_type == "INSPECT":
            self.current_task = {
                "type": "INSPECT",
                "status": "PENDING"
            }
            self.state = "INSPECTING"
            return True

        elif task_type == "HARVEST":
            if not target:
                logger.error("采摘任务需要目标果实")
                return False
            self.current_task = {
                "type": "HARVEST",
                "target": target,
                "status": "PENDING"
            }
            self.state = "HARVESTING"
            return True

        elif task_type == "RETURN":
            self.current_task = {
                "type": "RETURN",
                "status": "PENDING"
            }
            self.state = "RETURNING"
            return True

        else:
            logger.error(f"未知任务类型: {task_type}")
            return False

    def execute_navigation(self):
        """执行导航任务"""
        target = self.current_task["target"]
        logger.info(f"开始导航到目标位置: {target}")

        # 规划路径
        path = self.nav_system.plan_path(target)
        if not path:
            logger.error("无法规划到目标位置的路径")
            self.state = "IDLE"
            return

        # 沿路径移动
        for point in path:
            if not self.running:
                break

            # 检查前方障碍物
            if self.sensor_hub.detect_obstacle():
                logger.info("检测到障碍物，重新规划路径")
                path = self.nav_system.replan_path(target)
                if not path:
                    logger.error("无法避开障碍物，停止导航")
                    self.state = "IDLE"
                    return
                continue

            # 移动到下一个点
            self.motor_controller.move_to(point)

            # 更新位置
            self.nav_system.update_position()

        logger.info("到达目标位置")
        self.state = "IDLE"
        self.current_task["status"] = "COMPLETED"

    def execute_inspection(self):
        """执行巡检任务"""
        logger.info("开始作物巡检...")

        # 启动视觉系统
        self.vision_system.start_inspection()

        # 移动到第一个巡检点
        self.set_task("NAVIGATE", target=(0, 0))
        while self.state != "IDLE":
            time.sleep(1)

        # 扫描区域
        inspection_points = [(x, y) for x in range(0, 5) for y in range(0, 5)]

        for point in inspection_points:
            if not self.running:
                break

            # 导航到巡检点
            self.set_task("NAVIGATE", target=point)
            while self.state != "IDLE":
                time.sleep(0.5)

            # 采集数据
            crop_data = self.vision_system.capture_crop_data()
            health_status = self.vision_system.analyze_health(crop_data)

            logger.info(f"巡检点 {point}: 作物健康状况 - {health_status}")

            # 检测果实
            fruits = self.vision_system.detect_fruits()
            if fruits:
                logger.info(f"检测到 {len(fruits)} 个成熟果实")

        logger.info("巡检任务完成")
        self.state = "IDLE"
        self.current_task["status"] = "COMPLETED"

    def execute_harvesting(self):
        """执行采摘任务"""
        target_fruit = self.current_task["target"]
        logger.info(f"开始采摘果实: {target_fruit}")

        # 定位果实
        fruit_position = self.vision_system.locate_fruit(target_fruit)
        if not fruit_position:
            logger.error("无法定位目标果实")
            self.state = "IDLE"
            return

        # 计算机械臂运动轨迹
        arm_trajectory = self.arm_controller.calculate_trajectory(fruit_position)

        # 移动机械臂到采摘位置
        self.arm_controller.execute_trajectory(arm_trajectory)

        # 执行采摘动作
        success = self.arm_controller.harvest_fruit()

        if success:
            logger.info("果实采摘成功")
            # 将果实放入货舱
            self.arm_controller.store_fruit()
        else:
            logger.warning("果实采摘失败")

        self.state = "IDLE"
        self.current_task["status"] = "COMPLETED" if success else "FAILED"

    def execute_return(self):
        """执行返回任务"""
        logger.info("返回充电站...")
        self.set_task("NAVIGATE", target="CHARGING_STATION")
        while self.state != "IDLE":
            time.sleep(1)

        # 对接充电站
        self.motor_controller.dock_to_charger()
        logger.info("已连接充电站，开始充电")

        # 充电过程
        while self.battery_level < 95 and self.running:
            self.battery_level += 1
            time.sleep(0.5)

        logger.info("充电完成")
        self.state = "IDLE"
        self.current_task["status"] = "COMPLETED"

    def return_to_charge(self):
        """返回充电站"""
        logger.info("电量不足，返回充电站")
        self.set_task("RETURN")

    def emergency_stop(self):
        """紧急停止"""
        logger.critical("执行紧急停止！")
        self.running = False
        self.motor_controller.stop()
        self.arm_controller.stop()
        self.state = "EMERGENCY"

    def shutdown(self):
        """关闭系统"""
        logger.info("关闭系统...")
        self.running = False
        self.main_thread.join()
        self.monitor_thread.join()

        self.nav_system.shutdown()
        self.vision_system.shutdown()
        self.arm_controller.shutdown()
        self.motor_controller.shutdown()
        self.sensor_hub.shutdown()
        logger.info("系统已关闭")














