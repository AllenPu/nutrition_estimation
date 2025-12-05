import torch
import torch.nn as nn
from torchvision.models import resnet18


class Regression(nn.Module):
    def __init__(self, args=None):
        super(Regression, self).__init__()
        self.args = args
        self.model = torchvision.models.resnet18(pretrained=False)
        #
        fc_inputs = self.model.fc.in_features
        #
        self.model_extractor = nn.Sequential(*list(self.model.children())[:-1])
        #
        self.model_linear =  nn.Sequential(nn.Flatten(start_dim=1), nn.Linear(fc_inputs, outpu1_dim))
        

    def forward(self, x):
        #"output of model dim is 2G"
        z = self.model_extractor(x)
        #
        z = self.Flatten(z)
        #
        y_hat = self.model_linear(z)
        #
        return y_hat, z