import torch
import os
from torch.utils import data
import csv
from PIL import Image


class nutrition5k(data.Dataset):
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
        img_list = []
        # check the first item is the overhead path, the next item is sides path
        # length 1, only sides, length 2, both overhead and sides
        if len(self.image_path[key]) == 2:
            overhead_path = self.image_path[0]
            overhead_img = Image.open(self.image_path[key]).convert('RGB')
        # 
        img = Image.open(self.image_path[key]).convert('RGB')
        transform = self.get_transform()
        img = transform(img)
        label = float(self.label_dict[key])
        return img, label
        
##################
#
# img output sequence : overhead, camera_A, camera_B, camera_C, camera_D
#
##################



    

