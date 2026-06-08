import torch
from ultralytics import YOLO
from ultralytics.data.augment import Compose, RandomRotate, AddNoise
from ultralytics.nn.modules import Conv, C3
import os


# -----------------------------
# 1. BiFPN模块实现
# -----------------------------
class BiFPN(torch.nn.Module):
    def __init__(self, in_channels, out_channels, num_levels=3):
        super(BiFPN, self).__init__()
        self.num_levels = num_levels
        self.lateral_convs = torch.nn.ModuleList([
            Conv(in_channels[i], out_channels, 1) for i in range(num_levels)
        ])
        self.fpn_convs = torch.nn.ModuleList([
            Conv(out_channels, out_channels, 3, p=1) for _ in range(num_levels)
        ])
        self.downsample_convs = torch.nn.ModuleList([
            Conv(out_channels, out_channels, 3, s=2, p=1) for _ in range(num_levels - 1)
        ])

    def forward(self, inputs):
        laterals = [self.lateral_convs[i](inputs[i]) for i in range(self.num_levels)]

        # Top-down pathway
        for i in range(self.num_levels - 1, 0, -1):
            laterals[i - 1] += torch.nn.functional.interpolate(
                laterals[i], scale_factor=2, mode='nearest'
            )
            laterals[i - 1] = self.fpn_convs[i - 1](laterals[i - 1])

        # Bottom-up pathway
        for i in range(self.num_levels - 1):
            laterals[i + 1] += self.downsample_convs[i](laterals[i])
            laterals[i + 1] = self.fpn_convs[i + 1](laterals[i + 1])

        return laterals


# -----------------------------
# 2. 改进的YOLOv8模型
# -----------------------------
class ImprovedYOLOv8(YOLO):
    def __init__(self, model="yolov8n.pt", num_classes=80, bi_fpn_out_channels=256):
        super(ImprovedYOLOv8, self).__init__(model)
        self.model = self._build_model(num_classes, bi_fpn_out_channels)

    def _build_model(self, num_classes, bi_fpn_out_channels):
        model = YOLO("yolov8n.pt").model
        model.nc = num_classes

        # 提取YOLOv8-Tiny的P3/P4/P5特征图
        feature_maps = [
            model.model[6].cv2,  # P3
            model.model[14].cv2,  # P4
            model.model[22].cv2  # P5
        ]

        # 添加BiFPN模块
        self.bifpn = BiFPN(
            in_channels=[f.out_channels for f in feature_maps],
            out_channels=bi_fpn_out_channels,
            num_levels=3
        )

        # 替换检测头
        model.model[-1] = torch.nn.Sequential(
            C3(bi_fpn_out_channels, bi_fpn_out_channels, n=1),
            torch.nn.Conv2d(bi_fpn_out_channels, num_classes + 4, 1)
        )

        return model

    def forward(self, x):
        features = []
        for i, layer in enumerate(self.model.model):
            x = layer(x)
            if i in [6, 14, 22]:  # P3, P4, P5
                features.append(x)

        fused_features = self.bifpn(features)
        output = self.model.model[-1](fused_features[-1])
        return output


# -----------------------------
# 3. 数据增强策略
# -----------------------------
def get_augmentations():
    return Compose([
        RandomRotate(limit=30),  # 旋转增强
        AddNoise(mode="gaussian"),  # 高斯噪声
        AddNoise(mode="salt_pepper"),  # 椒盐噪声
    ])


# -----------------------------
# 4. 训练与评估
# -----------------------------
def train_and_evaluate(model, data_yaml, epochs=100, batch_size=16, imgsz=640, project="improved_yolov8", name="bifpn"):
    print("🚀 开始训练模型...")
    model.train(
        data=data_yaml,
        epochs=epochs,
        batch=batch_size,
        imgsz=imgsz,
        augment=get_augmentations(),
        pretrained=True,
        project=project,
        name=name,
        device="0" if torch.cuda.is_available() else "cpu"
    )

    print("✅ 训练完成，开始评估模型...")
    metrics = model.val(data=data_yaml)
    print(f"📊 mAP@0.5: {metrics.box.map:.4f}")
    print(f"📊 mAP@0.5:0.95: {metrics.box.map50_95:.4f}")


# -----------------------------
# 5. 模型导出（ONNX）
# -----------------------------
def export_onnx(model, output_path="improved_yolov8.onnx"):
    print(f"📦 导出ONNX模型到: {output_path}")
    model.export(format="onnx", dynamic=True, simplify=True)


# -----------------------------
# 6. 主程序入口
# -----------------------------
if __name__ == "__main__":
    # ✅ 修改为你的数据集路径
    DATA_YAML_PATH = "path/to/your_dataset.yaml"

    # 初始化模型（假设检测3种作物）
    model = ImprovedYOLOv8(model="yolov8n.pt", num_classes=3, bi_fpn_out_channels=256)

    # 训练与评估
    train_and_evaluate(model, data_yaml=DATA_YAML_PATH, epochs=100, batch_size=16, imgsz=640)

    # 导出ONNX模型
    export_onnx(model, output_path="improved_yolov8.onnx")