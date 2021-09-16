from tiling.brick_layout import BrickLayout
import os
import torch
import numpy as np
from solver.ml_solver.data_util import GraphDataset
from util.data_util import write_brick_layout_data, load_brick_layout_data
from util.algo_util import append_text_to_file
import tiling.tile_factory as factory
from torch_geometric.data import DataLoader
import time
import glob
import asyncio, concurrent.futures
import multiprocessing as mp
import inputs.config as config
import traceback
from util.shape_processor import load_polygons
from solver.ml_solver.losses import Losses

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)

class Trainer():
    def __init__(self, debugger, plotter, device, network, data_path):
        self.debugger = debugger
        self.plotter = plotter
        self.device = device
        self.model_save_path = self.debugger.file_path(self.debugger.file_path("model"))
        self.data_path = data_path
        self.raw_path = os.path.join(data_path, 'raw')
        self.training_path = os.path.join(self.raw_path, 'train')
        self.testing_path = os.path.join(self.raw_path, 'test')
        self.network = network

        # creation of directory for result
        os.mkdir(self.debugger.file_path('model'))
        os.mkdir(self.debugger.file_path('result'))



    def create_data(self, complete_graph, low=0.4, high=0.8, max_vertices=10, testing_ratio=0.2, number_of_data=20000):
        
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
        if not os.path.exists(self.raw_path):
            os.makedirs(self.raw_path)
        if not os.path.exists(self.training_path):
            os.makedirs(self.training_path)
        if not os.path.exists(self.testing_path):
            os.makedirs(self.testing_path)
        # create training data
        self._create_data(self.plotter, complete_graph, self.training_path, number_of_data, low, high, max_vertices)
        # create testing data
        self._create_data(self.plotter, complete_graph, self.testing_path, int(number_of_data * testing_ratio), low, high, max_vertices)


    def _create_data(self, plotter, graph, data_path, number_of_data, low, high, max_vertices,
                     workers = 16):
        start_time = time.time()
        print(f"generating data to {data_path}")
        if not os.path.isdir(os.path.join(data_path, 'raw')):
            os.mkdir(os.path.join(data_path, 'raw'))

        loop = asyncio.get_event_loop()

        # put poisitonal args in order of _create_one_data

        pool = mp.Pool(workers)
        pool.map(Trainer._create_one_data, [ (graph, data_path, low, high, max_vertices, i) for i in range(number_of_data) ])

        print("Time used: %s" % (time.time() - start_time))

    @staticmethod
    def _create_one_data(data):
        graph, data_path, low, high, max_vertices, index = data
        single_data_path = os.path.join(data_path, 'raw/data_{}.pkl'.format(index))
        if not os.path.exists(single_data_path):
            node_feature, collide_edge_index, collide_edge_features, align_edge_index, align_edge_features,\
            re_index = factory.generate_random_inputs(graph, max_vertices, low=low, high=high)
            # write the file to a pkl file
            assert len(collide_edge_index) > 0
            assert len(align_edge_index) > 0

            write_brick_layout_data(save_path='data_{}.pkl'.format(index),
                                    node_features=node_feature,
                                    collide_edge_index=collide_edge_index,
                                    collide_edge_features=collide_edge_features,
                                    align_edge_index=align_edge_index,
                                    align_edge_features=align_edge_features,
                                    re_index=re_index,
                                    prefix=data_path,
                                    predict=None,
                                    predict_order=None,
                                    predict_probs=None
                                    )

            if index % 5 == 0:
                print(f"{index} data generated")
