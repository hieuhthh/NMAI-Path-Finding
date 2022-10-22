try:
    from visual.cell import *
except:
    from cell import *

from importlib.resources import path
import matplotlib.pyplot as plt
import sys
import os
import shutil
import moviepy.video.io.ImageSequenceClip
import time
from util import *

class Map:
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(self.filepath)
        self.must_pass_points, self.awarding_points, self.matrix = self.read_file(self.filepath)
        self.row = len(self.matrix)
        self.col = len(self.matrix[0])
        self.start_pos = self.get_start_pos()
        self.end_pos = self.get_end_pos()
        self.tele_mtr = self.get_tele_points()

        # Visualization properties
        self.screen_res = self.screen_width, self.screen_height = 340, 340
        self.tile_size = min(self.screen_height // self.row, self.screen_width // self.col)
        self.tile_padding = 20 * self.tile_size // 170

        self.screen_height = self.tile_size * self.row # update to fit map
        self.screen_width = self.tile_size * self.col # update to fit map
        self.screen_res = self.screen_width, self.screen_height # update to fit map

        self.screen_fps = 20
        self.jump = 5
        self.video_fps = 20

        self.search_print_speed = 15 # miliseconds
        self.path_print_speed = 15 # miliseconds

        self.auto_close = False

    def read_file(self, file_name):
        with open(file_name, 'r') as f:
            n_awarding_cells = int(next(f)[:-1])
            awarding_points = []
            must_pass_points = []

            for i in range(n_awarding_cells):
                x, y, reward = map(int, next(f)[:-1].split(' '))
                if reward == 0:
                    must_pass_points.append((x, y))
                else:
                    awarding_points.append((x, y, reward))

            raw_matrix = f.read()
            matrix = [list(i) for i in raw_matrix.splitlines()]
        
        return must_pass_points, awarding_points, matrix

    def get_tele_points(self):
        tele_dic = {}
        tele_mtr = {}
        for p in self.awarding_points:
            if p[-1] > 0:
                try:
                    tele_dic[p[-1]].append(p[:2])
                except:
                    tele_dic[p[-1]] = [p[:2]]

        for l in tele_dic.values():
            tele_mtr[(l[0])] = l[1]
            tele_mtr[(l[1])] = l[0]

        return tele_mtr

    def get_level(self):
        if len(self.awarding_points) == 0:
            return 'level_1'

        for p in self.awarding_points:
            if p[-1] > 0:
                return 'advance'

            if p[-1] == 0:
                return 'level_3'

        return 'level_2'

    def get_start_pos(self):
        for i in range(self.row):
            for j in range(self.col):
                if self.matrix[i][j] == 'S':
                    return (i, j)
            
        return None

    def is_edge(self, point):
        if point[0] == 0 or point[0] == self.row - 1 or  point[1] == 0 or point[1] == self.col - 1:
            return True
        
        return False

    def get_end_pos(self):
        for i in range(self.row):
            for j in range(self.col):
                if self.matrix[i][j] == ' ' and self.is_edge((i, j)):
                    return (i, j)
            
        return None

    def is_inside(self, point):
        if point[0] >= 0 and point[0] < self.row and \
           point[1] >= 0 and point[1] < self.col:
            return True
        
        return False

    def is_movable(self, point):
        if self.is_inside(point) and self.matrix[point[0]][point[1]] != 'x':
            return True
        
        return False

    def get_walls(self):
        walls = []

        for i in range(self.row):
            for j in range(self.col):
                if self.matrix[i][j] == 'x':
                    walls.append((i, j))
            
        return walls

    def convert_video(self, from_folder, to_file, final_img=True):
        filenames = os.listdir(from_folder)
        filenames = sorted(filenames, key=lambda x : int(x.split('_')[-1][:-4]))
        filepaths = [from_folder + '/' + x for x in filenames]
        clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(filepaths, fps=self.video_fps)
        clip.write_videofile(to_file)

        if final_img:
            shutil.copy(filepaths[-1], to_file[:-3] + 'jpg')

        try:
            shutil.rmtree(from_folder)
        except:
            pass

    def show_video(self, paths=None, searchs=None, save_path=None, window_name="My search game"):
        grid_cells = self.generate_map()

        if save_path is not None:
            cnt = -1
            from_folder = os.path.join('source','temp')
            try_make_dir(from_folder)

        pygame.init()
        surface = pygame.Surface(self.screen_res)
        surface = pygame.display.set_mode((self.screen_width,self.screen_height))
        pygame.display.set_caption(window_name)

        clock = pygame.time.Clock()
        
        background = pygame.Rect((0, 0), (self.screen_width,self.screen_height))

        print_search = pygame.USEREVENT + 0
        print_search_complete = False

        print_path = pygame.USEREVENT + 1
        print_path_complete = False

        cur_node = 0
        cur_node_search = 0
        pygame.time.set_timer(print_search, self.search_print_speed)

        start_time = None

        while True: 
            if print_search_complete and print_path_complete and self.auto_close > 0:
                if start_time is None:
                    start_time = time.time()
                else:
                    dura = time.time() - start_time
                    if dura >= self.auto_close:
                        if save_path is not None:
                            cnt += 1
                            save_im_path = os.path.join(from_folder, f"screenshot_{cnt}.jpg")
                            pygame.image.save(surface, save_im_path)
                            self.convert_video(from_folder, save_path)
                        pygame.quit()
                        return

            for event in pygame.event.get():
                if print_search_complete and not print_path_complete:
                    pygame.event.post(pygame.event.Event(print_path))

                if event.type == pygame.QUIT:
                    print('QUIT')
                    if save_path is not None:
                        cnt += 1
                        save_im_path = os.path.join(from_folder, f"screenshot_{cnt}.jpg")
                        pygame.image.save(surface, save_im_path)
                        self.convert_video(from_folder, save_path)

                    pygame.quit()
                    return

                elif event.type == print_search:
                    if (searchs is None or print_search_complete):
                        pygame.time.set_timer(print_search, 0) # Stop events
                    else:
                        if (cur_node_search >= len(searchs)):
                            print_search_complete = True
                        else:
                            x = searchs[cur_node_search][0]
                            y = searchs[cur_node_search][1]

                            id = x * self.col + y
                            grid_cells[id].set_in_search(True)
                            # print(cur_node, id, grid_cells[id].type, grid_cells[id].inPath)
                            cur_node_search += 1

                elif event.type == print_path:
                    if (paths is None or print_path_complete):
                        pygame.time.set_timer(print_path, 0) # Stop events
                    else:
                        if (cur_node >= len(paths)):
                            print_path_complete = True
                        else:
                            x = paths[cur_node][0]
                            y = paths[cur_node][1]

                            id = x * self.col + y
                            grid_cells[id].set_in_path(True)
                            # print(cur_node, id, grid_cells[id].type, grid_cells[id].inPath)
                            cur_node += 1

            pygame.draw.rect(surface, pygame.Color('white'), background)
            [cell.draw_border(surface) for cell in grid_cells]
            [cell.draw(surface) for cell in grid_cells]
    
            # debug
            # for i, cell in enumerate(grid_cells):
            #     try:
            #         cell.draw(surface)
            #     except:
            #         print(i)

            pygame.display.flip()
            clock.tick(self.screen_fps)

            if save_path is not None:
                if (paths != None and not print_path_complete):
                    cnt += 1
                    if cnt % self.jump == 0:
                        save_im_path = os.path.join(from_folder, f"screenshot_{cnt}.jpg")
                        pygame.image.save(surface, save_im_path)

            # secs = 0.001
            # time.sleep(secs)

            print('drawing')


    # Generate cells in map to visualize
    # Input: maze read in txt
    # Output: array of cells
    def generate_map(self):
        grid_cells = [Cell(col, row, self.matrix[row][col], self.tile_size, self.tile_padding) for row in range(self.row) for col in range(self.col)]

        return grid_cells

if __name__ == "__main__":
    filepath = '../maze.txt'
    mp = Map(filepath)
    print(mp.awarding_points)
    print(mp.__dict__)
    
