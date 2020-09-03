"""
data loader for a  'corrupted' (c for corrupted) version of the STL-10 data set. based on the
the stl-10 data loader shipped with pytorch.
this by-passes downloading, integrity checking etc.
"""

from __future__ import print_function
import torch.utils.data as data
from PIL import Image
import os
import os.path
import errno
import numpy as np
import sys
from torchvision.datasets.cifar import CIFAR10


class STL10_C(CIFAR10):
    """`STL10 <https://cs.stanford.edu/~acoates/stl10/>`_ Dataset.
    Args:
        root (string): Root directory of dataset where directory
            ``stl10_binary`` exists.
        split (string): One of {'train', 'test', 'unlabeled', 'train+unlabeled'}.
            Accordingly dataset is selected.
        transform (callable, optional): A function/transform that  takes in an PIL image
            and returns a transformed version. E.g, ``transforms.RandomCrop``
        target_transform (callable, optional): A function/transform that takes in the
            target and transforms it.
        
    """
    base_folder = 'stl10_binary'
    class_names_file = 'class_names.txt'
    train_list = [
        #['train_X_modified.bin', '918c2871b30a85fa023e0c44e0bee87f'],
        ['train_X.bin', '918c2871b30a85fa023e0c44e0bee87f'],
        #['train_X_smudged_all.bin', '918c2871b30a85fa023e0c44e0bee87f'],
        #['train_y_modified.bin', '5a34089d4802c674881badbb80307741'],
        ['train_y.bin', '5a34089d4802c674881badbb80307741']
        #['unlabeled_X.bin', '5242ba1fed5e4be9e1e742405eb56ca4']
        #['unlabeled_X_smudged_all.bin', '5242ba1fed5e4be9e1e742405eb56ca4']
        #['tiny-imagenet-5k-96x96x3-stl10-format-smudged-all.bin' ,'5242ba1fed5e4be9e1e742405eb56ca4']
        #['tiny-imagenet-5k-96x96x3-stl10-format.bin' ,'5242ba1fed5e4be9e1e742405eb56ca4']
    ]

    test_list = [
        #['test_X_modified.bin', '7f263ba9f9e0b06b93213547f721ac82'],
        ['test_X.bin', '7f263ba9f9e0b06b93213547f721ac82'],
        #['test_X_smudged_all.bin', '7f263ba9f9e0b06b93213547f721ac82'],
        ['test_y.bin', '36f9794fa4beb8a2c72628de14fa638e']
    ]
    splits = ('train', 'train+unlabeled', 'unlabeled', 'test')

    def __init__(self, root, split='train',
                 transform=None, target_transform=None, train_list=None,test_list=None):
        if split not in self.splits:
            raise ValueError('Split "{}" not found. Valid splits are: {}'.format(
                split, ', '.join(self.splits),
            ))
        self.root = os.path.expanduser(root)
        self.transform = transform
        self.target_transform = target_transform
        self.split = split  # train/test/unlabeled set

        if not train_list is None:
            for i in [0,1]:
                for j in [0,1]:
                    self.train_list[i][j] = train_list[i][j] or self.train_list[i][j]
   
        if not test_list is None:
            for i in [0,1]:
                for j in [0,1]:
                    self.test_list[i][j] = test_list[i][j] or self.test_list[i][j]
            

        # if download:
        #     self.download()

        # if not self._check_integrity():
        #     raise RuntimeError(
        #         'Dataset not found or corrupted. '
        #         'You can use download=True to download it')

        # now load the picked numpy arrays
        if self.split == 'train':
            self.data, self.labels = self.__loadfile(
                self.train_list[0][0], self.train_list[1][0])
            self.train_labels = self.labels
        # elif self.split == 'train+unlabeled':
        #     self.data, self.labels = self.__loadfile(
        #         self.train_list[0][0], self.train_list[1][0])
        #     unlabeled_data, _ = self.__loadfile(self.train_list[2][0])
        #     self.data = np.concatenate((self.data, unlabeled_data))
        #     self.labels = np.concatenate(
        #         (self.labels, np.asarray([-1] * unlabeled_data.shape[0])))

        elif self.split == 'unlabeled':
            self.data, _ = self.__loadfile(self.train_list[2][0])
            self.labels = np.asarray([-1] * self.data.shape[0])
        else:  # self.split == 'test':
            self.data, self.labels = self.__loadfile(
                self.test_list[0][0], self.test_list[1][0])

        class_file = os.path.join(
            self.root, self.base_folder, self.class_names_file)
        if os.path.isfile(class_file):
            with open(class_file) as f:
                self.classes = f.read().splitlines()

    def __getitem__(self, index):
        """
        Args:
            index (int): Index
        Returns:
            tuple: (image, target) where target is index of the target class.
        """
        if self.labels is not None:
            img, target = self.data[index], int(self.labels[index])
        else:
            img, target = self.data[index], None

        # doing this so that it is consistent with all other datasets
        # to return a PIL Image
        img = Image.fromarray(np.transpose(img, (1, 2, 0)))

        if self.transform is not None:
            img = self.transform(img)

        if self.target_transform is not None:
            target = self.target_transform(target)

        return img, target

    def __len__(self):
        return self.data.shape[0]

    def __loadfile(self, data_file, labels_file=None):
        labels = None
        if labels_file:
            path_to_labels = os.path.join(
                self.root, self.base_folder, labels_file)
            print("label file is",path_to_labels)
            with open(path_to_labels, 'rb') as f:
                #labels = np.fromfile(f, dtype=np.uint8) - 1  # 0-based
                labels = np.fromfile(f, dtype=np.uint8) # 0-based

        path_to_data = os.path.join(self.root, self.base_folder, data_file)
        print("data file is",path_to_data)

        with open(path_to_data, 'rb') as f:
            # read whole file in uint8 chunks
            everything = np.fromfile(f, dtype=np.uint8)
            images = np.reshape(everything, (-1, 3, 96, 96))
            images = np.transpose(images, (0, 1, 3, 2))

        return images, labels

    def __repr__(self):
        fmt_str = 'Dataset ' + self.__class__.__name__ + '\n'
        fmt_str += '    Number of datapoints: {}\n'.format(self.__len__())
        fmt_str += '    Split: {}\n'.format(self.split)
        fmt_str += '    Root Location: {}\n'.format(self.root)
        tmp = '    Transforms (if any): '
        fmt_str += '{0}{1}\n'.format(tmp, self.transform.__repr__().replace('\n', '\n' + ' ' * len(tmp)))
        tmp = '    Target Transforms (if any): '
        fmt_str += '{0}{1}'.format(tmp, self.target_transform.__repr__().replace('\n', '\n' + ' ' * len(tmp)))
        return fmt_str