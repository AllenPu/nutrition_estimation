import torch
from network import Regression




if __name__ == "__main__":
    #build up model
    model = Regression()
    #set up dataset
    train_data = nutrition5k()
