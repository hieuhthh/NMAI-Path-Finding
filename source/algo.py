from path import *
from heuristic import *
from queue import PriorityQueue

class DFS(Path):
    def __init__(self, mp):
        super().__init__(mp)
        self.algo_name = 'dfs'

    def find_paths(self):
        traces = {self.map.start_pos : None}
        opens = [self.map.start_pos]
        closes = []
        found = False

        while opens:
            node = opens.pop()
            closes.append(node)

            if (node == self.map.end_pos):
                found = True
                break

            for step in self.steps:
                next = (node[0] + step[0], node[1] + step[1])

                if self.map.is_movable(next) and next not in closes:
                    opens.append(next)
                    traces[next] = node

        paths, ans = self.trace_paths(traces)

        return found, paths, closes, ans

class BFS(Path):
    def __init__(self, mp):
        super().__init__(mp)
        self.algo_name = 'bfs'

    def find_paths(self):
        traces = {self.map.start_pos : None}
        opens = [self.map.start_pos]
        closes = [self.map.start_pos]
        found = False

        while opens:
            node = opens.pop(0)

            if (node == self.map.end_pos):
                found = True
                break

            for step in self.steps:
                next = (node[0] + step[0], node[1] + step[1])

                if self.map.is_movable(next) and next not in closes:
                    opens.append(next)
                    closes.append(next)
                    traces[next] = node

        paths, ans = self.trace_paths(traces)

        return found, paths, closes, ans

class UCS(Path):
    def __init__(self, mp):
        super().__init__(mp)
        self.algo_name = 'ucs'

    def find_paths(self):
        traces = {self.map.start_pos : None}
        frontier = PriorityQueue()
        explored = []
        found = False

        frontier.put((0, self.map.start_pos))

        while not frontier.empty():
            dist, node = frontier.get()
            frontier.task_done()
            if node in explored:
                continue
            explored.append(node)

            if (node == self.map.end_pos):
                found = True
                break
            
            #if node not in explored:
            for step in self.steps:
                next = (node[0] + step[0], node[1] + step[1])

                if self.map.is_movable(next) and next not in explored:
                    frontier.put((dist + 1, next))
                    traces[next] = node

        paths, ans = self.trace_paths(traces)

        return found, paths, explored, ans

class Gready_BFS(Path):
    """
    f(x) = h(x)
    """
    def __init__(self, mp, heuristic_func):
        super().__init__(mp)
        self.heuristic_func = heuristic_func
        self.algo_name = 'gready_bfs'

    def find_paths(self):
        traces = {self.map.start_pos : None}
        opens = PriorityQueue()
        closes = []
        found = False

        opens.put((0, self.map.start_pos))

        while not opens.empty():
            node = opens.get()
            opens.task_done()
            node = node[1]
            if node in closes: # If not already in closes, no need to proceed
                continue
            
            closes.append(node)

            if (node == self.map.end_pos):
                found = True
                break

            for step in self.steps:
                next = (node[0] + step[0], node[1] + step[1])

                if self.map.is_movable(next) and next not in closes:
                    value = self.heuristic_func(next, self.map.end_pos)
                    opens.put((value, next))
                    traces[next] = node

        paths, ans = self.trace_paths(traces)

        return found, paths, closes, ans

class AStar(Path):
    """
    f(x) = g(x) + h(x)
    """
    def __init__(self, mp, heuristic_func):
        super().__init__(mp)
        self.heuristic_func = heuristic_func
        self.algo_name = 'astar'

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
            closes.append(node)

            if (node == self.map.end_pos):
                found = True
                break

            for step in self.steps:
                next = (node[0] + step[0], node[1] + step[1])

                if self.map.is_movable(next) and next not in closes:
                    if next not in actual.keys() or actual[node] + self.block_len < actual[next]:
                        actual[next] = actual[node] + self.block_len
                        traces[next] = node

                    value = actual[next] + self.heuristic_func(next, self.map.end_pos)

                    if next not in costs.keys() or value < costs[next]:
                        costs[next] = value
                        opens.put((value, next))
                        
        paths, ans = self.trace_paths(traces)

        return found, paths, closes, ans

if __name__ == "__main__":
    filepath = './input/level_1/input4.txt'
    mp = Map(filepath)

    algo = DFS(mp)
    found, paths, closes, ans = algo.find_paths()
    print(found)
    print(paths)
    print(len(paths))
    save_path = "DFS.mp4"
    mp.show_video(paths, closes, save_path)

    algo = BFS(mp)
    found, paths, closes, ans = algo.find_paths()
    print(found)
    print(paths)
    print(len(paths))
    save_path = "BFS.mp4"
    mp.show_video(paths, closes, save_path)

    algo = UCS(mp)
    found, paths, closes, ans = algo.find_paths()
    print(found)
    print(paths)
    print(len(paths))
    save_path = "UCS.mp4"
    mp.show_video(paths, closes, save_path)

    #heuristic_func = euclidean_distance
    heuristic_func = manhattan_distance
    #heuristic_func = chebyshev_distance
    algo = Gready_BFS(mp, heuristic_func)
    found, paths, closes, ans = algo.find_paths()
    print(found)
    print(paths)
    print(len(paths))
    save_path = "Gready_BFS.mp4"
    mp.show_video(paths, closes, save_path)

    heuristic_func = euclidean_distance
    # heuristic_func = manhattan_distance
    # heuristic_func = chebyshev_distance
    algo = AStar(mp, heuristic_func)
    found, paths, closes, ans = algo.find_paths()
    print(found)
    print(paths)
    print(len(paths))
    save_path = "AStar.mp4"
    mp.show_video(paths, closes, save_path)

    