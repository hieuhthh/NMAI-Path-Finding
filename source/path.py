from visual import *

class Path():
    def __init__(self, mp):
        self.map = mp
        self.steps = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        self.block_len = 1
        self.tele_cost = 0
        
    def get_award(self, node):
        for ap in self.map.awarding_points:
            if ap[0] == node[0] and ap[1] == node[1]:
                return ap[-1]

        return 0

    def is_tele(self, node):
        return node in self.map.tele_mtr.keys()

    def trace_paths(self, traces):
        node = self.map.end_pos
        ans = 0
        paths = []

        while node in traces.keys() and node != self.map.start_pos:
            paths.append(node)
            ans += self.get_award(node) + self.block_len
            node = traces[node]

        paths.append(self.map.start_pos)
        
        paths.reverse()

        return paths, ans

    def find_paths(self):
        pass

    def execute(self, out_folder, print_full_cost=False):
        found, paths, closes, ans = self.find_paths()
        out_algo = os.path.join(out_folder, self.algo_name)
        os.mkdir(out_algo)
        save_path = os.path.join(out_algo, f"{self.algo_name}.mp4")
        window_name = f"{self.algo_name}_{self.map.filename} "
        self.map.show_video(paths, closes, save_path, window_name)
        with open(os.path.join(out_algo, f"{self.algo_name}.txt"), "w") as f:
            if found:
                f.write(str(ans))
            else:
                f.write('NO')
            
            if print_full_cost:
                f.write('\n' + str(len(closes)-1))


if __name__ == "__main__":
    filepath = 'maze.txt'
    mp = Map(filepath)
    fp = Path(mp)