import torch
import os
from torch.utils import data
import csv
from PIL import Image
import numpy as np


class nutrition5k(data.Dataset):
    # angles: overhead, camera_A, camera_B, camera_C, camera_D
    def _init__(self, split='train', angles='overhead'):
        train_path = '/data/rpu2/nutrition5k/nutrition5k_dataset/dish_ids/splits/rgb_train_ids.txt'
        test_path = '/data/rpu2/nutrition5k/nutrition5k_dataset/dish_ids/splits/rgb_test_ids.txt'
        #
        imagery_path = '/data/rpu2/nutrition5k/nutrition5k_dataset/imagery'
        # dish_id, total_calories, total_mass, total_fat, total_carb, total_protein, num_ingrs
        label_path = '/data/rpu2/nutrition5k/nutrition5k_dataset/metadata'
        if split == 'train':
            paths = train_path
        if split == 'test':
            paths = test_path
        #
        self.removal_angle = angles
        self.image_path, self.label_dict = [], {}
        #
        img_list = [os.path.join(imagery_path, 'realsense_overhead'), os.path.join(imagery_path, 'side_angles')]
        label_list = [os.path.join(label_path, 'dish_metadata_cafe1.csv'), os.path.join(label_path, 'dish_metadata_cafe2.csv')]
        #
        #if angles == 'overhead':
        #    position = '/realsense_overhead'
        #else:
        #    position = '/side_angles'
        # process the image directory
        with open(paths, mode='r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            img_list = []
            for row in reader:
                if 'dish' not in row:
                    continue
                #
                img_overhead = os.path.join(img_list[0], row)
                img_sides = os.path.join(img_list[1], row)    
                #
                if os.path.exists(img_overhead):
                    img_list.append(img_overhead)
                if os.path.exists(img_sides):
                    img_list.append(img_sides)
                    # this path is the upper directory of the dish_id, not 
                self.image_path[row] = img_list
        print(f'The length of this set is {len(self.image_path)}')
        # process the label directory
        for e in label_list:
            with open(e, mode='r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    dish = row.split(',')
                    dish_id, dish_calo = dish[0], dish[1]
                    self.label_dict[dish_id] = dish_calo
        #
        if sl
        cameras = ["camera_A_frame_", "camera_B_frame_", "camera_C_frame_", "camera_D_frame_"]
        self.camera = cameras.remove(f'{self.removal_angle}_frame_')

    #
    def __len__(self):
        return len(self.image_path.keys())


    #
    def get_transform(self):
        if self.split == 'train':
            transform = transforms.Compose([
                transforms.Resize((self.img_size, self.img_size)),
                transforms.RandomCrop(self.img_size, padding=16),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                transforms.Normalize([.5, .5, .5], [.5, .5, .5]),
            ])
        else:
            transform = transforms.Compose([
                transforms.Resize((self.img_size, self.img_size)),
                transforms.ToTensor(),
                transforms.Normalize([.5, .5, .5], [.5, .5, .5]),
            ])
        return transform

    # num_choice : how many image you want to chosse from each angle (sides)
    def __getitem__(self, index, num_choice = 1):
        index = index % len(self.image_path.keys())
        key = list(self.image_path.keys())[index]
        ##########
        img_path_list, img = [], []
        # check the first item is the overhead path, the next item is sides path
        # length 1, only sides, length 2, both overhead and sides
        if len(self.image_path[key]) == 2:
            overhead_path = self.image_path[0]
            overhead_img = Image.open(self.image_path[key]).convert('RGB')
            img_path_list.append(overhead_img)
        #if len(self.image_path[key]) == 1:
        sides_path = self.image_path[-1]
        sides_path = os.path.join(sides_path, 'frames')
        # 
        for e in self.cameras:
            # from 30 different sides choice 1 random
            for c in range(num_choice):
                indexs = random.choice(30)
                cam_path = os.path.join(sides_path, e)
                cam_path = os.path.join(cam_path, indexs)
                side_img = Image.open(self.image_path[key]).convert('RGB')
                img_path_list.append(side_img)
        # 
        transform = self.get_transform()
        for e in img_path_list:
            transformed_img = np.array(transform(e))
            img.append(transformed_img)
        label = np.asarray(self.label_dict[key].astype('float32'))
        # now we have a list [overhead, cam A, cam B, cam C, cam D] or [cam A, cam B, cam C, cam D] 
        # then we can concat them together
        img = np.concatenate(img, axis=0)
        return img, label
        
##################
#
# img output sequence : overhead, camera_A, camera_B, camera_C, camera_D
#
##################



    

