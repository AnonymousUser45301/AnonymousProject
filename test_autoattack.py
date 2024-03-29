import sys
import os
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.autograd import Variable
import torchvision.datasets as dset
import torchvision.transforms as transforms
from torchvision.utils import save_image
from torch.utils.data import DataLoader

import shutil
import setproctitle
import numpy as np
import random

import models, wideresnet
from autoattack import AutoAttack


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--batchSz', type=int, default=250)
    parser.add_argument('--data', type=str, default='cifar10', choices=('cifar10', 'cifar100'))
    parser.add_argument('--num_samples', type=int, default=10000)

    parser.add_argument('--attack', type=str, default='L2', choices=('Linf', 'L2'))
    parser.add_argument('--eps', type=float, default=128.0)
    parser.add_argument('--model_path', type=str)

    parser.add_argument('--seed', type=int, default=1)

    args = parser.parse_args()

    args.eps = args.eps / 255


    torch.manual_seed(args.seed)
    torch.cuda.manual_seed(args.seed)
    np.random.seed(args.seed)
    random.seed(args.seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    os.environ["PYTHONHASHSEED"] = str(args.seed)


    orig_stdout = sys.stdout
    f = open(os.path.join('model_pth', args.model_path, 'test_autoattack_output.log'), 'w')
    #sys.stdout = f


    transform = transforms.Compose([transforms.ToTensor()])
    if args.data == 'cifar10':
        trainDataset = dset.CIFAR10(root='cifar10', train=True, download=True, transform=transform)
        testDataset = dset.CIFAR10(root='cifar10', train=False, download=True, transform=transform)
    elif args.data == 'cifar100':
        trainDataset = dset.CIFAR100(root='cifar100', train=True, download=True, transform=transform)
        testDataset = dset.CIFAR100(root='cifar100', train=False, download=True, transform=transform)

    kwargs = {'num_workers': 0} 
    trainLoader = DataLoader(trainDataset, batch_size=args.batchSz, shuffle=False, **kwargs)
    testLoader = DataLoader(testDataset, batch_size=args.batchSz, shuffle=False, **kwargs)
   

    net = torch.load(os.path.join('model_pth', args.model_path, 'latest.pth'), map_location=torch.device('cuda'))

    adversary = AutoAttack(net, norm=args.attack, eps=args.eps, seed=args.seed,  version='standard')

    print('\n\n')
    print('*'*40)
    print('Train error against auto attack: ')
    print('*'*40)
    aa_test(args, net, trainLoader, adversary)

    print('\n\n')
    print('*'*40)
    print('Test error against auto attack: ')
    print('*'*40)
    aa_test(args, net, testLoader, adversary)

    sys.stdout = orig_stdout
    f.close()



def aa_test(args, net, testLoader, attacker):
    net.eval()
    image = None
    labels = None
    
    for data, target in testLoader:
        data, target = data.cuda(), target.cuda()

        if image == None:
            image = data
            labels = target
        else:
            image = torch.cat((image, data), 0)
            labels = torch.cat((labels, target), 0)

    attacker.run_standard_evaluation(image[:args.num_samples], labels[:args.num_samples], bs=args.batchSz)




if __name__=='__main__':
    main()
