from algo import *
from award_algo import *
from tele_algo import *
from util import *
import os
import shutil
import gc
import argparse

def parse_opt(known=False):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-folder', type=str, default='input', help='path to input folder')
    parser.add_argument('--output-folder', type=str, default='output', help='path to output folder')
    parser.add_argument('--print-search-cost', action='store_true', default=False, help='if print search cost in file output txt')
    parser.add_argument('--dont-show-video', action='store_true', default=False, help='if show video on screen')
    parser.add_argument('--auto-close', type=float, default=0.1, help='wait x (sec) until auto close between each map / algorithm, set 0 if you want to close it by yourself')
    parser.add_argument('--level', nargs='+', type=int, default=[1, 2, 3, 4], help='do which level (1, 2, 3, 4 = advance)')
    parser.add_argument('--path', type=str, default='', help='path to specific input.txt, wont care input folder')

    return parser.parse_known_args()[0] if known else parser.parse_args()

def excute_level(map, level, opt, out_folder):
    if level == 'level_1' and 1 in opt.level:
        for ALGO in [DFS, BFS, UCS]:
            algo = ALGO(map)
            algo.execute(out_folder, opt.print_search_cost)

        for ALGO in [Gready_BFS, AStar]:
            for ih, H_FUNC in enumerate([euclidean_distance, manhattan_distance, chebyshev_distance]):
                algo = ALGO(map, H_FUNC)
                algo.algo_name = algo.algo_name + f'_heuristic_{ih+1}'
                algo.execute(out_folder, opt.print_search_cost)

    elif level == 'level_2' and 2 in opt.level:
        for ih, H_FUNC in enumerate([euclidean_distance, manhattan_distance, chebyshev_distance]):
            algo = Award_Algo(map, H_FUNC)
            algo.algo_name = algo.algo_name + f'_heuristic_{ih+1}'
            algo.execute(out_folder, opt.print_search_cost)

    elif level == 'level_3' and 3 in opt.level:
        algo = Must_Pass_Algo(map)
        algo.execute(out_folder, opt.print_search_cost)

    elif level == 'advance' and 4 in opt.level:
        for ih, H_FUNC in enumerate([euclidean_distance, manhattan_distance, chebyshev_distance]):
            algo = Tele_Algo(map, H_FUNC)
            algo.algo_name = algo.algo_name + f'_heuristic_{ih+1}'
            algo.execute(out_folder, opt.print_search_cost)
    
    gc.collect()

def main(opt):
    print('First, run: pip install -r requirements.txt')
    print('The program sometimes may suddenly end due to the inconsistent when converting video, just need to re-run: python main.py')
    print('Watching screen may reduce the times program interrupt')
    print('You could try: python main.py --dont-show-video to run it silently, more stable!')
    print('Or run: python main.py --path path-to-txt-file')
    print('For more information run: python main.py -h')

    in_route = opt.input_folder
    out_route = opt.output_folder

    try_make_dir(out_route)

    if opt.dont_show_video:
        os.environ["SDL_VIDEODRIVER"] = "dummy"

    if opt.path != '':
        map = Map(opt.path)
        map.auto_close = opt.auto_close # sec
        level = map.get_level()
        excute_level(map, level, opt, out_route)
        return

    for level in ['level_1', 'level_2', 'level_3', 'advance']:
        in_level = os.path.join(in_route, level)
        out_level = os.path.join(out_route, level)
        os.mkdir(out_level)

        for filepath in os.listdir(in_level):
            in_path = os.path.join(in_level, filepath)
            out_folder = os.path.join(out_level, filepath[:-4])
            os.mkdir(out_folder)

            map = Map(in_path)
            map.auto_close = opt.auto_close # sec

            excute_level(map, level, opt, out_folder)
            
if __name__ == "__main__":
    opt = parse_opt()
    main(opt)



