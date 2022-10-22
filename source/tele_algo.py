from matplotlib.pyplot import close
from path import *
from heuristic import *
from queue import PriorityQueue

class Tele_Algo(Path):
    def __init__(self, mp, heuristic_func):
        super().__init__(mp)
        self.heuristic_func = heuristic_func
        self.algo_name = 'algo3'

    def tele_heuristic_func(self, a, b, closes):
        """
        a: start point
        b: end point
        closes: list of reached point
        """
        h1 = self.heuristic_func(a, b)
        h2 = None
        
        for tl in self.map.tele_mtr.keys():
            if tl not in closes:
                temp = self.heuristic_func(a, tl) + self.tele_cost + self.heuristic_func(self.map.tele_mtr[tl], b)
                if h2 is None:
                    h2 = temp
                else:
                    h2 = min(h2, temp)

        if h2 is None:
            return h1

        return min(h1, h2)

    def find_paths(self):
        traces = {self.map.start_pos : None}
        actual = {self.map.start_pos : 0} # actual cost from start to this
        costs = {} # cost from start to end
        opens = PriorityQueue()
        closes = []
        found = False

        opens.put((0, self.map.start_pos))

        while not opens.empty():
            node = opens.get()
            opens.task_done()
            node = node[1]
            
            if self.is_tele(node):
                closes.append(self.map.tele_mtr[node])
                closes.append(node)
            else:
                closes.append(node)

            if (node == self.map.end_pos):
                found = True
                break

            for step in self.steps:
                next = (node[0] + step[0], node[1] + step[1])
                if self.map.is_movable(next) and next not in closes:
                    
                    if self.is_tele(next):
                        next_tele = self.map.tele_mtr[next]

                        if next not in actual.keys() or actual[node] + self.block_len < actual[next]:
                            actual[next] = actual[node] + self.block_len
                            traces[next] = node

                        if next_tele not in actual.keys() or actual[next] + self.tele_cost < actual[next_tele]:
                            actual[next_tele] = actual[next] + self.tele_cost
                            traces[next_tele] = next

                        value = actual[next_tele] + self.tele_heuristic_func(next_tele, self.map.end_pos, closes)

                        if next_tele not in costs.keys() or value < costs[next_tele]:
                            costs[next_tele] = value
                            opens.put((value, next_tele))
                    else:
                        if next not in actual.keys() or actual[node] + self.block_len < actual[next]:
                            actual[next] = actual[node] + self.block_len
                            traces[next] = node

                        value = actual[next] + self.tele_heuristic_func(next, self.map.end_pos, closes)

                        if next not in costs.keys() or value < costs[next]:
                            costs[next] = value
                            opens.put((value, next))
                        
        paths, ans = self.trace_paths(traces)

        return found, paths, closes, ans

if __name__ == "__main__":
    filepath = '.\\input\\advance\\input3.txt'
    out_folder = '.\\'
    mp = Map(filepath)
    heuristic_func = euclidean_distance
    # heuristic_func = manhattan_distance
    # heuristic_func = chebyshev_distance
    algo = Tele_Algo(mp, heuristic_func)
    try:
        shutil.rmtree(algo.algo_name)
    except:
        pass
    algo.execute(out_folder)
    found, paths, closes, ans = algo.find_paths()
    print(found)
    print(paths)
    print(len(paths))
    print(ans)
    print(mp.get_tele_points())