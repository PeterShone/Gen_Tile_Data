import logging
import os
from util.debugger import MyDebugger
from tiling.tile_graph import TileGraph, find_candidate_tile_locations, get_all_tiles
import tiling.tile_factory as factory
from inputs import config
from tiling.brick_layout import BrickLayout
import time
import multiprocessing as mp
from interfaces.qt_plot import Plotter
import shapely


def scan(last_layer_tile):
    result = []
    for align_tile in data_env.proto_tiles:
        neighbour_tiles, _ = get_all_tiles(last_layer_tile, align_tile, integer_align = True)
        for elem in neighbour_tiles:
            if elem not in result:
                result.append(elem)
    return result
        

if __name__ == '__main__':
    print(shapely.__version__)
    # Driver code
    MyDebugger.pre_fix = os.path.join(MyDebugger.pre_fix, "debug")
    debugger = MyDebugger(f"gen_tile_graph_{config.env_name}", fix_rand_seed=0, save_print_to_file=False)
    data_env = config.environment

    total_ring_num = 20
    least_graph_ring_num = 1

    print('start!')
    begin_time = time.time()
    ring_time = begin_time

    # the resulting tiles
    result_tiles = [data_env.proto_tiles[0]]
    # the tiles in the last ring
    last_ring = [data_env.proto_tiles[0]]

    # keep generating until ring20
    for i in range(0, total_ring_num):
        print(f"computing ring_{i}")
        last_ring_num = len(last_ring)
        print(f"last_ring_num: {last_ring_num}")
        
        # multiprocessing
        workers = 8
        pool = mp.Pool(workers)
        rl = pool.map(scan, last_ring)
        pool.close()
        pool.join()

        last_ring = []
        for last_ring_idx in range(last_ring_num):
            for elem in rl[last_ring_idx]:
                if elem not in result_tiles:
                    result_tiles.append(elem)
                    last_ring.append(elem)

        print(f"Ring {i} Time used: %s" % (time.time() - ring_time))
        print()
        ring_time = time.time()
        
        # original
        # for last_ring_idx in range(last_ring_num):
        #     print(f"last ring_{last_ring_idx}")
        #     last_layer_tile = last_ring.pop(0)
        #     # plotter.draw_contours(debugger.file_path("last_layer_tile_{}.png".format(i)), [tile.get_plot_attribute("blue_trans") for tile in [last_layer_tile]])
        #     for align_tile in data_env.proto_tiles:
        #         neighbour_tiles, _ = get_all_tiles(last_layer_tile, align_tile, integer_align = True)
        #         for elem in neighbour_tiles:
        #             if elem not in result_tiles:
        #                 result_tiles.append(elem)
        #                 last_ring.append(elem)
        # print(f'final last ring: {len(last_ring)}')
        # print(f"Tile num: {len(result_tiles)}")
        # print(f"Ring {i} Time used: %s" % (time.time() - ring_time))
        # ring_time = time.time()
        
        # generate complete graph from ring10
        if(i >= (least_graph_ring_num - 1)):
            tiles = result_tiles
            print(f"Form complete_graph_ring{i+1}...")
            print(f"Total {len(tiles)}  tiles created!")
            print("Total creating Time used: %s" % (time.time() - begin_time))
            file_name = "complete_graph_ring{}.pkl".format(i+1)
            
            # record strat time
            start_time = time.time()
            graph = TileGraph(data_env.tile_count, tiles = tiles, one_hot = True, proto_tiles= data_env.proto_tiles)
            print("Forming Graph time used: %s" % (time.time() - start_time))

            if not os.path.isdir(data_env.base_path):
                os.mkdir(data_env.base_path)
            graph.save_current_state(os.path.join(data_env.base_path, file_name))

            # load complete brick_layouts
            graph = TileGraph(data_env.tile_count)
            graph.load_graph_state(os.path.join(data_env.base_path, file_name))

            # graph.show_complete_super_graph(plotter, debugger, f"super_graph_{num_rings}.png")

            # logging...
            print(f"done_{i}")
            num_of_nodes, num_of_adj_edges, num_of_collide_edges = graph._get_graph_statistics()
            print(f"num_of_nodes : {num_of_nodes}")
            print(f"num_of_adj_edges : {num_of_adj_edges}")
            print(f"num_of_collide_edges : {num_of_collide_edges}")
            print()
