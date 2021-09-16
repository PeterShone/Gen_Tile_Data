from util.debugger import MyDebugger
# from interfaces.qt_plot import Plotter
from graph_networks.networks.TilinGNN import TilinGNN
import os
from inputs import config
from solver.ml_solver.trainer import Trainer
import torch
from solver.ml_solver.ml_solver import ML_Solver
import numpy as np
from solver.ml_solver.data_util import GraphDataset

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

if __name__ == "__main__":
    print(device)
    MyDebugger.pre_fix = os.path.join(MyDebugger.pre_fix, "debug")
    debugger = MyDebugger(f"gen_data_{config.env_name}-ring{config.complete_graph_size}-{config.number_of_data}",
                          fix_rand_seed = config.rand_seed, save_print_to_file=False)
    # plotter = Plotter()
    data_env = config.environment
    data_env.load_complete_graph(config.complete_graph_size)

    trainer = Trainer(debugger, None, device, None, data_path=config.dataset_path)

    trainer.create_data(data_env.complete_graph,
                        low            = config.shape_size_lower_bound,
                        high           = config.shape_size_upper_bound,
                        max_vertices   = config.max_vertices,
                        testing_ratio  = config.validation_data_proportion,
                        number_of_data = config.number_of_data)

    # data_path = config.dataset_path
    # training_path = os.path.join(data_path, 'train')
    # testing_path = os.path.join(data_path, 'test')

    # dataset_train = GraphDataset(root=training_path)
    # dataset_train.process()
    
    # dataset_test = GraphDataset(root=testing_path)
    # dataset_test.process()
