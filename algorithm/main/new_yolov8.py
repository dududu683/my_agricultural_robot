from ultralytics import YOLO

class ImprovedYOLOv8(YOLO):
    def __init__(self, model="yolov8n.pt", num_classes=80, bi_fpn_out_channels=256):
        super(ImprovedYOLOv8, self).__init__(model)
        self.model = self._build_model(num_classes, bi_fpn_out_channels)

    def _build_model(self, num_classes, bi_fpn_out_channels):
        # 加载预训练YOLOv8模型
        model = YOLO("yolov8n.pt").model
        model.nc = num_classes

        # 提取P3, P4, P5特征图
        feature_maps = [
            model.model[6].cv2,  # P3
            model.model[14].cv2, # P4
            model.model[22].cv2  # P5
        ]

        # 添加BiFPN模块
        self.bifpn = BiFPN(
            in_channels=[f.out_channels for f in feature_maps],
            out_channels=bi_fpn_out_channels,
            num_levels=3
        )

        # 替换检测头
        model.model[-1] = nn.Sequential(
            C3(bi_fpn_out_channels, bi_fpn_out_channels, n=1),
            nn.Conv2d(bi_fpn_out_channels, num_classes + 4, 1)
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