import torch
import os
from torch.utils import data
import csv
from PIL import Image
import numpy as np

# only return the side images
class nutrition5k_sides(data.Dataset):
    # angles: overhead, camera_A, camera_B, camera_C, camera_D
    def _init__(self, split='train', angles='camera_A'):
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
        #img_list = [os.path.join(imagery_path, 'realsense_overhead'), os.path.join(imagery_path, 'side_angles')]
        label_list = [os.path.join(label_path, 'dish_metadata_cafe1.csv'), os.path.join(label_path, 'dish_metadata_cafe2.csv')]
       #
        with open(paths, mode='r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            img_list = []
            for row in reader:
                if 'dish' not in row:
                    continue
                #
                #img_overhead = os.path.join(img_list[0], row)
                #if os.path.exists(img_overhead):
                #    img_list.append(img_overhead)
                img_upper_path = os.path.join(imagery_path, 'side_angles')
                img_sides = os.path.join(img_upper_path, row)    
                #
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
        cameras = ["camera_A_frame_", "camera_B_frame_", "camera_C_frame_", "camera_D_frame_"]
        if angels != '':
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
    def __getitem__(self, index, num_choice = 5):
        transform = self.get_transform()
        index = index % len(self.image_path.keys())
        key = list(self.image_path.keys())[index]
        ##########
        imgs = []
        # 
        sides_path = self.image_path[key]
        sides_path = os.path.join(sides_path, 'frames')
        #
        for e in self.camera:
            img_list = []
            # from 30 different sides choice 1 random
            for c in range(num_choice):
                indexs = random.choice(30)
                cam_path = os.path.join(sides_path, e) + '0' + indexs + '.jpeg'
                side_img = Image.open(cam_path).convert('RGB')
                img_list.append(np.array(transform(e)))
            img = np.stack(arr_list, axis=0)
            imgs.append(img)
        # 
        label = np.asarray(self.label_dict[key].astype('float32'))
        # now we have a list [cam A, cam B, cam C, cam D] or [cam A, cam B, cam C, cam D] 
        # then we can concat them together    
        return imgs, label
        
##################
#
# img output sequence :  tensor : [[camera_A, camera_B, camera_C, camera_D]], N x [cam A, ..., cam D]
#
##################


# only return the overhead images and their sides angles
class nutrition5k_overhead(data.Dataset):
    # angles: overhead
    def _init__(self, split='train'): 
        train_path = '/data/rpu2/nutrition5k/nutrition5k_dataset/dish_ids/splits/rgb_train_ids.txt'
        test_path = '/data/rpu2/nutrition5k/nutrition5k_dataset/dish_ids/splits/rgb_test_ids.txt'
        if split == 'train':
            paths = train_path
        if split == 'test':
            paths = test_path
        overhead_path = os.path.join(imagery_path, 'realsense_overhead')
        angles_path = os.path.join(imagery, 'side_angles')
        imagery_path = '/data/rpu2/nutrition5k/nutrition5k_dataset/imagery'
        label_list = [os.path.join(label_path, 'dish_metadata_cafe1.csv'), os.path.join(label_path, 'dish_metadata_cafe2.csv')]
        with open(paths, mode='r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            img_list = []
            for row in reader:
                if 'dish' not in row:
                    continue
                #
                img_overhead = os.path.join(overhead_path, row)
                img_side_angles = os.path.join(side_angles, row)
                if os.path.exists(img_overhead) and os.path.exists(img_side_angles):
                    self.image_path[row] = [img_overhead, img_side_angles]
                else:
                    continue

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
        self.cameras = ["camera_A_frame_", "camera_B_frame_", "camera_C_frame_", "camera_D_frame_"]
        
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
    def __getitem__(self, index, num_choice = 5):
        transform = self.get_transform()
        index = index % len(self.image_path.keys())
        key = list(self.image_path.keys())[index]
        ##########
        imgs = []
        # check the first item is the overhead path, the next item is sides path
        # length 1, only sides, length 2, both overhead and sides
        #if len(self.image_path[key]) == 2:
        overhead_path = self.image_path[key][0] + '/rgb.png'
        overhead_img = Image.open(overhead_path).convert('RGB')
        overhead_img = np.array(transform(overhead_img))
        #
        imgs.append(overhead_img)
        #
        sides_path = os.path.join(self.image_path[key][1], 'frames')
        #
        for a in self.camera:
            indexs = random.choice(30)
            sides_img = os.path.join(sides_path, a) + '0' + indexes + '.jpeg'
            sides_img = Image.open(sides_img).convert('RGB')
            sides_img = np.array(transform(side_img))
            imgs.append(sides_img)
        #imgs.append(np.expand_dims(img, axis=0))
        label = np.asarray(self.label_dict[key].astype('float32'))
        # now we have a list [cam A, cam B, cam C, cam D] or [cam A, cam B, cam C, cam D] 
        # then we can concat them together    
        return imgs, label



