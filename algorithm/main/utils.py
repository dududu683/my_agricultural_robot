# 文件: utils.py
"""
工具函数和类
"""
import logging
import time

# 配置日志系统
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SmartAgriRobot")


class SimulatedCamera:
    """模拟相机类"""

    def __init__(self):
        self.width = 640
        self.height = 480

    def capture(self):
        """捕获图像"""
        # 返回模拟图像
        return np.zeros((self.height, self.width, 3), dtype=np.uint8)

    def release(self):
        """释放相机资源"""
        pass


class SimulatedYOLOModel:
    """模拟YOLO模型"""

    def __init__(self):
        self.classes = ['apple', 'orange', 'tomato', 'leaf', 'stem']

    def detect(self, image):
        """目标检测"""
        # 返回模拟检测结果
        detections = []
        num_detections = random.randint(0, 5)

        for i in range(num_detections):
            cls = random.choice(self.classes)
            # 仅果实有深度信息
            depth = random.uniform(0.3, 1.0) if cls in ['apple', 'orange', 'tomato'] else None

            detections.append({
                'id': i,
                'class': cls,
                'confidence': random.uniform(0.7, 0.99),
                'x': random.randint(0, image.shape[1]),
                'y': random.randint(0, image.shape[0]),
                'width': random.randint(30, 100),
                'height': random.randint(30, 100),
                'depth': depth
            })

        return detections
