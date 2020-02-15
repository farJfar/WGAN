# -*- coding: utf-8 -*-
"""WGAN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FE3SM0ov6C43_9mbpiqaiNH26-C6DID1
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms

# MNIST Dataset
original_train_dataset = datasets.MNIST(root='./mnist_data/', train=True, transform=transforms.ToTensor(), download=True)
original_test_dataset = datasets.MNIST(root='./mnist_data/', train=False, transform=transforms.ToTensor(), download=True)

# Device configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Set Hyper-parameters 
BATCH_SIZE = 128
LEARNING_RATE_D = 5e-5
LEARNING_RATE_G = 5e-5
N_EPOCH = 100

# Define Train loader
train_tensors = original_train_dataset.data.float() / 255
test_tensors = original_test_dataset.data.float() / 255

train_dataset = torch.utils.data.TensorDataset(train_tensors, original_train_dataset.targets)
test_dataset = torch.utils.data.TensorDataset(test_tensors, original_test_dataset.targets)

train_loader = torch.utils.data.DataLoader(dataset=train_dataset, batch_size=BATCH_SIZE, shuffle=True)
test_loader = torch.utils.data.DataLoader(dataset=test_dataset, batch_size=BATCH_SIZE, shuffle=False)

discriminator = nn.Sequential(
    nn.Conv2d(1, 32, 4, 2, 1), 
    nn.BatchNorm2d(32),
    nn.LeakyReLU(0.2, inplace=True),
    nn.Conv2d(32, 64, 4, 2, 1), 
    nn.BatchNorm2d(64),
    nn.LeakyReLU(0.2, inplace=True),
    nn.Conv2d(64, 128, 4, 2, 1),  
    nn.BatchNorm2d(128),
    nn.LeakyReLU(0.2, inplace=True),
    nn.Conv2d(128, 1, 4, 2, 1),  
)

generator = nn.Sequential(
    nn.ConvTranspose2d(128, 256, 4, 2, 1), 
    nn.BatchNorm2d(256),
    nn.LeakyReLU(0.2, inplace=True),
    nn.ConvTranspose2d(256, 128, 4, 2, 0), 
    nn.BatchNorm2d(128),
    nn.LeakyReLU(0.2, inplace=True),
    nn.ConvTranspose2d(128, 64, 4, 2, 0), 
    nn.BatchNorm2d(64),
    nn.LeakyReLU(0.2, inplace=True),
    nn.ConvTranspose2d(64, 1, 2, 2, 0), 
    nn.Sigmoid()
)

def weights_init(m):
    classname = m.__class__.__name__
    if classname.find('Conv') != -1:
        m.weight.data.normal_(0.0, 0.02)
    elif classname.find('BatchNorm') != -1:
        m.weight.data.normal_(1.0, 0.02)
        m.bias.data.fill_(0)

# Device setting
discriminator = discriminator.to(device)
discriminator.apply(weights_init)

# Device setting
generator= generator.to(device)
generator.apply(weights_init)

# Create two optimizer for discriminator and generator 
opt_D = optim.RMSprop(discriminator.parameters(), lr=LEARNING_RATE_D)
opt_G = optim.RMSprop(generator.parameters(), lr=LEARNING_RATE_G)

# Commented out IPython magic to ensure Python compatibility.
import matplotlib.pyplot as plt
# %matplotlib inline
plt.rcParams['figure.figsize'] = (10, 3)

for epoch in range(N_EPOCH):
  
    for i, (img, label) in enumerate(train_loader):
        for _ in range(5):
          img = img.reshape(-1, 1, 28, 28)
          real_img = img.to(device)

          fake_labels = torch.zeros(img.shape[0], 1, 1, 1).to(device)
          real_labels = torch.ones(img.shape[0], 1, 1, 1).to(device)
          discriminator.zero_grad()
          outputs_real=discriminator(real_img)       
          z = torch.randn(img.shape[0], 128)
          z=z.view(-1, 128, 1, 1)
          z=z.to(device)
          fake_img = generator(z)
          outputs_fake=discriminator(fake_img)
          loss_d =  -(torch.mean(outputs_real) - torch.mean(outputs_fake))
          loss_d.backward()
          opt_D.step()
          for p in discriminator.parameters():
            p.data.clamp_(-0.01, 0.01)
            
        generator.zero_grad()
        z = torch.randn(img.shape[0], 128)
        z=z.view(-1, 128, 1, 1)
        z=z.to(device)
        fake_img = generator(z)
        outputs_fake= discriminator(fake_img)
        loss_g = -torch.mean(outputs_fake)
        loss_g.backward()
        opt_G.step()

    
    print("epoch: {} \t last batch loss D: {} \t last batch loss G: {}".format(epoch + 1, 
                                                                               loss_d.item(), 
                                                                               loss_g.item()))

    for i in range(3):
        for j in range(10):
            plt.subplot(3, 10, i * 10 + j + 1)
            plt.imshow(fake_img[i * 10 + j].detach().cpu().view(28, 28).numpy())
    plt.show()