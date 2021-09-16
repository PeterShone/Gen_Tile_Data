import logging
import os
from util.debugger import MyDebugger
from tiling.tile_graph import TileGraph, find_candidate_tile_locations, get_all_tiles
import tiling.tile_factory as factory
from inputs import config
from tiling.brick_layout import BrickLayout


if __name__ == '__main__':
    # Driver code
    MyDebugger.pre_fix = os.path.join(MyDebugger.pre_fix, "debug")
    debugger = MyDebugger(f"gen_tile_graph_{config.env_name}", fix_rand_seed=0, save_print_to_file=False)
    data_env = config.environment
    print('start!')
    logging.error('start')

    # the resulting tiles
    result_tiles = [data_env.proto_tiles[0]]
    # the tiles in the last ring
    last_ring = [data_env.proto_tiles[0]]
    
    # for num_rings in range(20, 21):
        

        # generate complete brick_layouts
        # tiles = find_candidate_tile_locations(num_rings=num_rings, base_tile=data_env.proto_tiles[0], align_tiles=data_env.proto_tiles)

    for i in range(0, 21):
        print(f"computing ring_{i}")
        logging.error(f"computing ring_{i}")
        last_ring_num = len(last_ring)
        for last_ring_idx in range(last_ring_num):
            print(f"last ring_{last_ring_idx}")
            logging.error(f"last ring_{last_ring_idx}")
            last_layer_tile = last_ring.pop(0)
            for align_tile in data_env.proto_tiles:
                neighbour_tiles, _ = get_all_tiles(last_layer_tile, align_tile, integer_align = True)
                for elem in neighbour_tiles:
                    if elem not in result_tiles:
                        result_tiles.append(elem)
                        last_ring.append(elem)
        
        if(i >= 10):
            tiles = result_tiles
            print(f"{len(tiles)}  tiles created!")
            logging.error(f"{len(tiles)}  tiles created!")
            file_name = "complete_graph_ring{}.pkl".format(i+1)
            graph = TileGraph(data_env.tile_count, tiles = tiles, one_hot = True, proto_tiles= data_env.proto_tiles)

            if not os.path.isdir(data_env.base_path):
                os.mkdir(data_env.base_path)
            graph.save_current_state(os.path.join(data_env.base_path, file_name))

            # load complete brick_layouts
            graph = TileGraph(data_env.tile_count)
            graph.load_graph_state(os.path.join(data_env.base_path, file_name))

            # graph.show_complete_super_graph(plotter, debugger, f"super_graph_{num_rings}.png")

            print(f"done_{i}")
            logging.error(f"done_{i}")

            num_of_nodes, num_of_adj_edges, num_of_collide_edges = graph._get_graph_statistics()
            print(f"num_of_nodes : {num_of_nodes}")
            logging.error(f"num_of_nodes : {num_of_nodes}")
            print(f"num_of_adj_edges : {num_of_adj_edges}")
            logging.error(f"num_of_adj_edges : {num_of_adj_edges}")
            print(f"num_of_collide_edges : {num_of_collide_edges}")
            logging.error(f"num_of_collide_edges : {num_of_collide_edges}")
            print()
            logging.error("------")

        
        


        
