import random
from utils import logger


class SensorHub:
    def __init__(self):
        self.ultrasonic_data = [0.0] * 4  # 四个方向的超声波数据
        self.imu_data = {"ax": 0, "ay": 0, "az": 0, "gx": 0, "gy": 0, "gz": 0}
        self.camera_data = None
        self.limit_switches = [False] * 3
        self.photo_sensors = [False] * 2

    def initialize(self):
        """初始化传感器"""
        logger.info("初始化传感器系统...")
        # 在实际系统中会初始化各个传感器
        logger.info("传感器系统初始化完成")

    def update_all_sensors(self):
        """更新所有传感器数据"""
        self.get_ultrasonic_data()
        self.get_imu_data()
        self.get_camera_data()
        self.get_limit_switch_status()
        self.get_photo_sensor_status()

    def get_ultrasonic_data(self):
        """获取超声波传感器数据"""
        # 模拟超声波数据 (距离单位: 米)
        self.ultrasonic_data = [
            random.uniform(0.1, 2.0),
            random.uniform(0.1, 2.0),
            random.uniform(0.1, 2.0),
            random.uniform(0.1, 2.0)
        ]
        return self.ultrasonic_data

    def get_imu_data(self):
        """获取IMU数据"""
        # 模拟IMU数据
        self.imu_data = {
            "ax": random.uniform(-1.0, 1.0),
            "ay": random.uniform(-1.0, 1.0),
            "az": random.uniform(9.7, 9.9),  # 重力加速度
            "gx": random.uniform(-0.1, 0.1),
            "gy": random.uniform(-0.1, 0.1),
            "gz": random.uniform(-0.1, 0.1)
        }
        return self.imu_data

    def get_camera_data(self):
        """获取相机数据"""
        # 在实际系统中会获取相机帧
        # 这里返回模拟数据
        self.camera_data = {"frame": "simulated_frame", "timestamp": time.time()}
        return self.camera_data

    def get_limit_switch_status(self):
        """获取限位开关状态"""
        # 模拟限位开关状态
        self.limit_switches = [random.random() > 0.9 for _ in range(3)]
        return self.limit_switches

    def get_photo_sensor_status(self):
        """获取光电传感器状态"""
        # 模拟光电传感器状态
        self.photo_sensors = [random.random() > 0.8 for _ in range(2)]
        return self.photo_sensors

    def detect_obstacle(self, threshold=0.5):
        """检测障碍物"""
        # 如果有任何超声波检测到障碍物距离小于阈值
        return any(dist < threshold for dist in self.ultrasonic_data)

    def check_emergency(self):
        """检查紧急停止条件"""
        # 模拟紧急情况
        return random.random() > 0.99  # 1%的概率触发紧急停止

    def shutdown(self):
        """关闭传感器系统"""
        logger.info("关闭传感器系统")
