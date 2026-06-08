import torch
import torch.nn as nn
import torch.nn.functional as F
from ultralytics.nn.modules import Conv, C3


class BiFPN(nn.Module):
    def __init__(self, in_channels, out_channels, num_levels=3):
        super(BiFPN, self).__init__()
        self.num_levels = num_levels
        self.lateral_convs = nn.ModuleList([
            Conv(in_channels[i], out_channels, 1) for i in range(num_levels)
        ])
        self.fpn_convs = nn.ModuleList([
            Conv(out_channels, out_channels, 3, p=1) for _ in range(num_levels)
        ])
        self.downsample_convs = nn.ModuleList([
            Conv(out_channels, out_channels, 3, s=2, p=1) for _ in range(num_levels - 1)
        ])

    def forward(self, inputs):
        # Lateral connections
        laterals = [self.lateral_convs[i](inputs[i]) for i in range(self.num_levels)]

        # Top-down pathway
        for i in range(self.num_levels - 1, 0, -1):
            laterals[i - 1] += F.interpolate(laterals[i], scale_factor=2, mode='nearest')
            laterals[i - 1] = self.fpn_convs[i - 1](laterals[i - 1])

        # Bottom-up pathway
        for i in range(self.num_levels - 1):
            laterals[i + 1] += self.downsample_convs[i](laterals[i])
            laterals[i + 1] = self.fpn_convs[i + 1](laterals[i + 1])

        return laterals