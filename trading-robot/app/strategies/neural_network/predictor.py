import __main__
import os
from typing import List

import numpy as np
import torch
from torch import nn

from strategies.neural_network.models import Signal


class ConvNet(nn.Module):
    def __init__(self):
        super(ConvNet, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, stride=1)
        self.act1 = nn.ReLU()
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1)
        self.act2 = nn.ReLU()
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=1)
        self.drop_out = nn.Dropout(p=0.5)
        self.fc1 = nn.Linear(26 * 26 * 64, 200)
        self.act3 = nn.Tanh()
        self.fc2 = nn.Linear(200, 200)
        self.act4 = nn.Tanh()
        self.fc3 = nn.Linear(200, 3)
        self.soft = nn.Softmax(dim=1)

    def forward(self, x):
        out = self.act1(self.conv1(x))
        out = self.pool1(out)
        out = self.act2(self.conv2(out))
        out = self.pool2(out)
        out = out.reshape(out.size(0), -1)
        out = self.drop_out(out)
        out = self.act3(self.fc1(out))
        out = self.act4(self.fc2(out))
        out = self.soft(self.fc3(out))
        return out


def create_image(history: List[float]) -> np.ndarray:
    size = len(history)
    min_ts, max_ts = np.min(history), np.max(history)
    diff = max_ts - min_ts
    if diff == 0:
        return np.zeros((1, size, size), float)

    rescaled_ts = (history - min_ts) / diff
    image = np.zeros((1, size, size), float)
    sin_ts = np.sqrt(np.clip(1 - rescaled_ts ** 2, 0, 1))

    image[0] = np.outer(rescaled_ts, rescaled_ts) - np.outer(sin_ts, sin_ts)

    return image


class Predictor:
    def __init__(self, device, model_path):
        self.device = torch.device(device)
        self.model = torch.load(model_path, map_location=self.device)
        self.model = self.model.eval()

    def predict(self, history: List[float]) -> tuple[Signal, float]:
        image = create_image(history)
        tensor = torch.FloatTensor(image)
        predict = self.model(np.reshape(tensor, (1, 1, 32, 32)))
        probability, signal = torch.max(predict[0].data, 0)
        return Signal(int(signal)), round(float(probability) * 100, 4)


DEVICE = 'cpu'
MODEL_NAME = 'GAN_USDRUB_32x32.zip'
MODEL_PATH = os.path.abspath(os.path.join(__file__, f'../{MODEL_NAME}'))

setattr(__main__, "ConvNet", ConvNet)
predictor = Predictor(DEVICE, MODEL_PATH)
