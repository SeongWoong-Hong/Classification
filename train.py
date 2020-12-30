## Header
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from Models import ANNModel, CNNModel, RNNModel
from matplotlib import pyplot as plt
import csv
import numpy as np


## Data Preprocessing

traindata = csv.reader(open("train.txt"), delimiter='\t')
trainlabel = csv.reader(open("train_label.txt"), delimiter='\t')
testdata = csv.reader(open("test.txt"), delimiter='\t')
testlabel = csv.reader(open("test_label.txt"), delimiter='\t')

train_label = []
train_data = []
test_label = []
test_data = []

for line in trainlabel:
    train_label.append(int(float(line[0])))

for line in traindata:
    train_data.append([float(i) for i in line[0:-1]])

for line in testlabel:
    test_label.append(int(float(line[0])))

for line in testdata:
    test_data.append([float(i) for i in line[0:-1]])

##
LEARNING_RATE = 1e-4
BATCH_SIZE = 128
CRITERION = nn.CrossEntropyLoss()

##
train_data = np.array(train_data, dtype=np.float32)
train_image = train_data.reshape([len(train_label), 1, -1, 6])
img_size = train_image.shape[1]*train_image.shape[2]*train_image.shape[3]
label_data = np.array(train_label, dtype=np.int)
inp = train_data.shape[1]

tensor_train_data = torch.from_numpy(train_data)
tensor_train_image = torch.from_numpy(train_image)
tensor_label_data = torch.from_numpy(label_data)

train_dataset = list(zip(tensor_train_data, tensor_label_data))
train_imgset = list(zip(tensor_train_image, tensor_label_data))

test_data = np.array(test_data, dtype=np.float32)
test_image = test_data.reshape([len(test_label), 1, -1, 6])
label_data = np.array(test_label, dtype=np.int)

tensor_test_data = torch.from_numpy(test_data)
tensor_test_image = torch.from_numpy(test_image)
tensor_label_data = torch.from_numpy(label_data)

test_dataset = list(zip(tensor_test_data, tensor_label_data))
test_imgset = list(zip(tensor_test_image, tensor_label_data))


##
def fit(model, train_loader):
    model.train()
    device = next(model.parameters()).device.index
    optimizer = torch.optim.SGD(model.parameters(), lr=LEARNING_RATE, momentum=0.9)
    # optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    losses = []
    for i, data in enumerate(train_loader):
        image = data[0].type(torch.FloatTensor).cuda(device)
        label = data[1].type(torch.LongTensor).cuda(device)

        pred_label = model(image)
        loss = CRITERION(pred_label, label)
        losses.append(loss.item())

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    avg_loss = sum(losses)/len(losses)
    return avg_loss

##
def eval(model, test_loader):
    model.eval()
    device = next(model.parameters()).device.index
    pred_labels = []
    real_labels = []
    for i, data in enumerate(test_loader):
        image = data[0].type(torch.FloatTensor).cuda(device)
        label = data[1].type(torch.LongTensor).cuda(device)
        real_labels += list(label.cpu().detach().numpy())

        pred_label = model(image)
        pred_label = list(pred_label.cpu().detach().numpy())
        pred_labels += pred_label

    real_labels = np.array(real_labels)
    pred_labels = np.array(pred_labels)
    pred_labels = pred_labels.argmax(axis=1)
    acc = sum(real_labels == pred_labels) / len(real_labels) * 100
    return acc, pred_labels, real_labels

train_data_loader = DataLoader(dataset=train_dataset, batch_size=BATCH_SIZE, shuffle=True)
train_img_loader = DataLoader(dataset=train_imgset, batch_size=BATCH_SIZE, shuffle=True)
test_data_loader = DataLoader(dataset=test_dataset, batch_size=BATCH_SIZE, shuffle=False)
test_img_loader = DataLoader(dataset=test_imgset, batch_size=BATCH_SIZE, shuffle=False)

ANNet = ANNModel(inp, 4).cuda()
CNNet = CNNModel(img_size, 4).cuda()
# RNNet = RNNModel(inp, 128, 4).cuda()
EpochLoss = []
Acc = []
for epoch in range(200):
    CurrentEpochLoss = fit(ANNet, train_data_loader)
    CurrentAcc, _, _ = eval(ANNet, test_data_loader)
    print("ANN {}th Epoch. Average Loss is {:.5f}. Test Acc is {:.2f}".format(epoch+1, CurrentEpochLoss, CurrentAcc))
    EpochLoss.append(CurrentEpochLoss)
    Acc.append(CurrentAcc)
for epoch in range(200):
    CurrentEpochLoss = fit(CNNet, train_img_loader)
    CurrentAcc, _, _ = eval(CNNet, test_img_loader)
    print("CNN {}th Epoch. Average Loss is {:.5f}. Test Acc is {:.2f}".format(epoch+1, CurrentEpochLoss, CurrentAcc))
    EpochLoss.append(CurrentEpochLoss)
    Acc.append(CurrentAcc)
# for epoch in range(200):
#     CurrentEpochLoss = fit(RNNet, train_loader)
#     CurrentAcc, _, _ = eval(RNNet, test_loader)
#     print("RNN {}th Epoch. Average Loss is {:.5f}. Test Acc is {:.2f}".format(epoch+1, CurrentEpochLoss, CurrentAcc))
#     EpochLoss.append(CurrentEpochLoss)
#     Acc.append(CurrentAcc)

torch.save(ANNet.state_dict(), "ANN.pt")
torch.save(CNNet.state_dict(), "CNN.pt")
# torch.save(RNNet, "RNN")
##


# Acc, pred_labels, real_labels = eval(ANNet, test_loader)
# plt.plot(real_labels)
# plt.show()
# plt.plot(pred_labels)
# plt.show()
# print("{}, {:.2f}".format(len(real_labels), Acc))

