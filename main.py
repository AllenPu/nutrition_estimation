import torch
from torch.utils.data import DataLoader
#
from network import Regression





if __name__ == "__main__":
    #build up model
    model = Regression()
    #set up dataset
    train_dataset = nutrition5k_overhead()
    train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True,num_workers=8, pin_memory=True, drop_last=False)
    test_dataset = nutrition5k_overhead(split='test')
    test_loader = DataLoader(test_dataset, batch_size=128, shuffle=True,num_workers=8, pin_memory=True, drop_last=False)
    #
    
        # shape of N, camA, camB, camC, camD