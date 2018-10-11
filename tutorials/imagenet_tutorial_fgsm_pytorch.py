# Copyright 2017 - 2018 Baidu Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
FGSM tutorial on mnist using advbox tool.
FGSM method is non-targeted attack while FGSMT is targeted attack.
"""

import logging
logging.basicConfig(level=logging.INFO,format="%(filename)s[line:%(lineno)d] %(levelname)s %(message)s")
logger=logging.getLogger(__name__)



import sys
sys.path.append("..")

import torch
import torchvision
from torchvision import datasets, transforms
from torch.autograd import Variable
import torch.utils.data.dataloader as Data
import torch.nn as nn
from torchvision import models


from advbox.adversary import Adversary
from advbox.attacks.gradient_method import FGSMT
from advbox.attacks.gradient_method import FGSM
from advbox.models.pytorch import PytorchModel


import numpy as np
import cv2


def main(image_path):

    # Define what device we are using
    logging.info("CUDA Available: {}".format(torch.cuda.is_available()))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")



    orig = cv2.imread(image_path)[..., ::-1]
    orig = cv2.resize(orig, (224, 224))
    img = orig.copy().astype(np.float32)

    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]
    img /= 255.0
    img = (img - mean) / std
    img = img.transpose(2, 0, 1)

    img = Variable(torch.from_numpy(img).to(device).float().unsqueeze(0)).numpy()


    # Initialize the network
    model = models.resnet18(pretrained=True).to(device).eval()

    loss_func=nn.CrossEntropyLoss()

    # advbox demo
    m = PytorchModel(
        model, loss_func,(-1, 1),
        channel_axis=1)
    #attack = FGSMT(m)
    attack = FGSM(m)

    attack_config = {"epsilons": 0.3}

    inputs=img
    labels=np.array([388])

    print(inputs.shape)

    adversary = Adversary(inputs, labels)
    #adversary = Adversary(inputs, 388)

    #tlabel = np.array([489])
    #adversary.set_target(is_targeted_attack=True, target_label=tlabel)

    # FGSM non-targeted attack
    adversary = attack(adversary, **attack_config)


    if adversary.is_successful():
        print(
            'attack success, adversarial_label=%d'
            % (adversary.adversarial_label))

        adv=adversary.adversarial_example[0]
        adv = adv.transpose(1, 2, 0)
        adv = (adv * std) + mean
        adv = adv * 255.0
        adv = adv[..., ::-1]  # RGB to BGR
        adv = np.clip(adv, 0, 255).astype(np.uint8)
        cv2.imwrite('img_adv.png', adv)

    else:
        print('attack failed')


    print("fgsm attack done")


if __name__ == '__main__':
    main("cropped_panda.jpg")
