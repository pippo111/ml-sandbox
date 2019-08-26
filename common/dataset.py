import os
import numpy as np
import glob
from sklearn.model_selection import train_test_split

from common import data_sequence
from common import utils

class MyDataset():
    def __init__(
            self,
            scans = [],
            labels = [255.0],
            collection_name = 'mindboggle',
            input_label_niftii = 'aseg-in-t1weighted_2std.nii.gz',
            input_image_niftii = 't1weighted_2std.nii.gz',
            scan_shape = (192, 256, 256),
            input_shape = (48, 64, 64),
            batch_size = 32,
            limit = None
        ):
        self.scans = scans
        self.labels = labels
        self.collection_name = collection_name
        self.input_label_niftii = input_label_niftii
        self.input_image_niftii = input_image_niftii
        self.batch_size = batch_size

        self.scan_shape = scan_shape
        self.input_shape = input_shape

        self.limit = limit

        self.in_dataset_dir = './input/niftii'
        self.out_dataset_dir = './input/datasets'

    def save_3d(self, data, name, types):
        data_full_path = os.path.join(self.out_dataset_dir, self.collection_name, types)
        data_full_name = os.path.join(data_full_path, name)

        if not os.path.exists(data_full_path):
            os.makedirs(data_full_path)

        print(f'Saving {types} as {data_full_name}.npy')

        norm_data = utils.norm_to_uint8(data)

        # save normalized to uint (0 - 255)
        np.save(data_full_name, norm_data)
        print('Done.')

    def create_3d(self, scan_name, path):
        print(f'Loading from {path}/{self.input_label_niftii}')
        label_data = utils.load_image_data(self.input_label_niftii, path)
        prepared_labels = utils.convert_to_binary_3d(label_data, self.labels)
        prepared_labels = utils.resize_3d(prepared_labels, self.scan_shape)

        print(f'Loading from {path}/{self.input_image_niftii}...')
        image_data = utils.load_image_data(self.input_image_niftii, path)
        prepared_images = utils.resize_3d(image_data, self.scan_shape)

        if self.scan_shape != self.input_shape:
            sliced_images = utils.slice_3d(prepared_images, self.input_shape)
            sliced_labels = utils.slice_3d(prepared_labels, self.input_shape)

            for i, labels in enumerate(sliced_labels):
                if labels.max() > 0.0:
                    self.save_3d(labels, f'{scan_name}_{i}', 'labels')
                    self.save_3d(sliced_images[i], f'{scan_name}_{i}', 'images')

        else:
            self.save_3d(prepared_labels, scan_name, 'labels')
            self.save_3d(prepared_images, scan_name, 'images')


    # Public api
    def create_dataset_3d(self):
        for scan_name in self.scans:
            full_path = os.path.join(self.in_dataset_dir, scan_name)
            self.create_3d(scan_name, full_path)

    def create_train_valid_test_gen(self, test_size=1):
        X_files = sorted(
            glob.glob(
                os.path.join(self.out_dataset_dir, self.collection_name, 'images', '*.npy')
            )[:self.limit]
        )
        y_files = sorted(
            glob.glob(
                os.path.join(self.out_dataset_dir, self.collection_name, 'labels', '*.npy')
            )[:self.limit]
        )

        X_train, X_valid, y_train, y_valid = train_test_split(X_files, y_files, test_size=0.2, random_state=1)

        train_generator = data_sequence.DataSequence3d(X_train, y_train, self.batch_size, augmentation=True)
        valid_generator = data_sequence.DataSequence3d(X_valid, y_valid, self.batch_size, shuffle=False, augmentation=False)

        self.train_generator = train_generator
        self.valid_generator = valid_generator
        self.test_generator = valid_generator

        return train_generator, valid_generator, valid_generator

    def get_count(self):
        X_files = glob.glob(os.path.join(self.out_dataset_dir, self.collection_name, 'images', '*.npy'))[:self.limit]
        return len(X_files)