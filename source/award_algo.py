import operator
import random
from pygame import init
from path import *
from heuristic import *
from queue import PriorityQueue

class Award_Algo(Path):
    def __init__(self, mp, heuristic_func):
        super().__init__(mp)
        self.heuristic_func = heuristic_func
        self.algo_name = 'algo1'

    def award_heuristic_func(self, a, b, closes):
        """
        a: start point
        b: end point
        closes: list of reached point
        """
        h1 = self.heuristic_func(a, b)
        h2 = None
        
        for ap in self.map.awarding_points:
            if ap not in closes:
                temp = self.heuristic_func(a, ap[:2]) + ap[-1] + self.heuristic_func(ap[:2], b)
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
            closes.append(node)

            if (node == self.map.end_pos):
                found = True
                break

            for step in self.steps:
                next = (node[0] + step[0], node[1] + step[1])

                if self.map.is_movable(next) and next not in closes:
                    temp = actual[node] + self.block_len + self.get_award(next)

                    if next not in actual.keys() or temp < actual[next]:
                        actual[next] = temp
                        traces[next] = node

                    value = actual[next] + self.award_heuristic_func(next, self.map.end_pos, closes)

                    if next not in costs.keys() or value < costs[next]:
                        costs[next] = value
                        opens.put((value, next))
                        
        paths, ans = self.trace_paths(traces)

        return found, paths, closes, ans

class Must_Pass_Algo(Path):
    def __init__(self, mp):
        super().__init__(mp)
        self.algo_name = 'algo2'
        
        self.n_cells = self.map.row * self.map.col
        self.previous_cells = [[None for j in range(self.n_cells)] for i in range(self.n_cells)]
        inf = self.n_cells ** 2
        self.cost_matrix = [[inf if (i != j) else 0 for j in range(self.n_cells)] for i in range(self.n_cells)]
        self.generations_cost = ""

    def find_local_paths_ucs(self, start):
        if (self.map.is_movable(start) == False):
            return

        traces = {start : None}
        cost = {}
        frontier = PriorityQueue()
        explored = []

        frontier.put((0, start))

        while not frontier.empty():
            dist, node = frontier.get()
            frontier.task_done()
            if node in explored:
                continue
            explored.append(node)
            cost[node] = dist
            
            #if node not in explored:
            for step in self.steps:
                next = (node[0] + step[0], node[1] + step[1])

                if self.map.is_movable(next) and next not in explored:
                    frontier.put((dist + self.block_len, next))
                    traces[next] = node

        start_id = start[0] * self.map.col + start[1]
        for node in traces.keys():
            node_id = node[0] * self.map.col + node[1]
            self.cost_matrix[start_id][node_id] = cost[node]
            self.previous_cells[start_id][node_id] = traces[node]

        return

    def create_route(self):
        route = [self.map.start_pos]
        route.extend(random.sample(self.map.must_pass_points, len(self.map.must_pass_points)))
        route.append(self.map.end_pos)
        return route
        
    def init_population(self, population_size):
        population = []

        for i in range(0, population_size):
            population.append(self.create_route())
        
        return population

    def calculate_id(self, coord):
        return coord[0] * self.map.col + coord[1]

    def calculate_route_dist(self, route):
        start = None
        total_dist = 0

        start = route[0]

        for cur_node in route:
            total_dist += self.cost_matrix[self.calculate_id(start)][self.calculate_id(cur_node)]
            
            start = cur_node

        return total_dist

    def rank_population(self, population):
        ranking = {}
        for i in range(0, len(population)):
            ranking[i] = self.calculate_route_dist(population[i])

        return sorted (ranking.items(), key = operator.itemgetter(1))
        
    def select_population(self, ranked_population, size_for_best):
        selection = []
        
        if (size_for_best > len(ranked_population)):
            size_for_best = len(ranked_population)

        for i in range(0, size_for_best):
            selection.append(ranked_population[i][0])
        
        saved_size = ((len(ranked_population) - size_for_best) * random.randrange(1, 20) //  100)

        for individual in random.sample(ranked_population[size_for_best:], saved_size):
            selection.append(individual[0])

        return selection

    def create_mating_list(self, population, selected_id_list):
        mating_list = []

        for i in range(len(selected_id_list)):
            id = selected_id_list[i]
            mating_list.append(population[id])

        return mating_list

    def cross_over(self, parent1, parent2):
        child = [None] * len(parent1)
        existed_gen = []
        
        #assert len(parent1) > 2, len(parent1)
        st_gen = random.randrange(1, len(parent1) - 1)
        en_gen = random.randrange(1, len(parent1) - 1)

        if st_gen > en_gen:
            temp = st_gen
            st_gen = en_gen
            en_gen = temp
        elif st_gen == en_gen:
            en_gen += 1

        for i in range(st_gen, en_gen):
            existed_gen.append(parent1[i])
            child[i] = parent1[i]

        ptr = 0
        for gene in parent2:
            if gene not in existed_gen:
                while ptr < len(parent1) and child[ptr] != None:
                    ptr += 1
                
                child[ptr] = gene
                ptr += 1
        return child        

    def get_next_gen_by_mating(self, mating_list, size_for_best):
        next_gen = []
        
        #n_new_born = len(mating_list) - size_for_best

        for i in range(size_for_best):
            next_gen.append(mating_list[i])

        mating_list = random.sample(mating_list, len(mating_list))

        for i in range(len(mating_list)):
            next_gen.append(self.cross_over(mating_list[i], mating_list[len(mating_list) - i - 1]))

        return next_gen

    def mutate(self, individual, mutation_rate):
        #assert len(individual) > 2
        new_individual = individual.copy()
        for cur_gen in range(1, len(individual) - 1):
            if (random.random() < mutation_rate):
                
                to_swap_gen = random.randrange(1, len(individual) - 1)

                temp = new_individual[cur_gen]
                new_individual[cur_gen] = new_individual[to_swap_gen]
                new_individual[to_swap_gen] = temp

        return new_individual

    def get_next_gen_by_mutating(self, population, mutation_rate):
        next_gen = []

        for i in range(len(population)):
            new_ver = self.mutate(population[i], mutation_rate)
            next_gen.append(new_ver)

            if (self.calculate_route_dist(population[i]) < self.calculate_route_dist(new_ver)):
                next_gen.append(population[i])

        return next_gen

    def get_next_gen(self, population, size_for_best, mutation_rate, print_debug):
        ranked_population = self.rank_population(population)
        if (print_debug):
            cur_cost = self.calculate_route_dist(population[ranked_population[0][0]])
            print("Cost: ", cur_cost)
            self.generations_cost += str(cur_cost) + "\n"
        selected_id_list = self.select_population(ranked_population, size_for_best)
        
        #print(selected_id_list)

        mating_list = self.create_mating_list(population, selected_id_list)

        # for t in mating_list:
        #     print(self.calculate_route_dist(t), t)
        # print('*******************************')

        next_gen = self.get_next_gen_by_mating(mating_list, size_for_best)
        next_gen = self.get_next_gen_by_mutating(next_gen, mutation_rate)

        # Delete repeative individuals
        temp = []
        for i in range(0, len(next_gen)):
            fl = True
            for j in range(i + 1, len(next_gen)):
                if (next_gen[i] == next_gen[j]):
                    fl = False
                    break
            if fl:
                temp.append(next_gen[i])
                
        if (len(next_gen) < size_for_best):
            next_gen = next_gen * ((size_for_best // len(next_gen)) + 1)
            
        # for ind in next_gen:
        #     start_coord = self.map.start_pos
        #     end_coord = self.map.end_pos
        #     assert ind[0] == start_coord, "Not at beginning"
        #     assert ind[len(ind) - 1] == end_coord, "Not at ending"

        return next_gen

    def evolve(self, initial_size, size_for_best, mutation_rate, n_generations):
        population = self.init_population(initial_size)

        # print("Gen first:")
        # for ind in population:
        #     print(self.calculate_route_dist(ind), ind)
        # print('----------------------')


        for i in range(n_generations + 1):
            if (i % 1000 == 0):
                print("Gen",i)
                self.generations_cost = self.generations_cost + "Best cost in generation " + str(i) + ": "
            population = self.get_next_gen(population, size_for_best, mutation_rate, (i % 1000 == 0))

        # print("Gen final:")
        # for ind in population:
        #     print(self.calculate_route_dist(ind), ind)

        best_id = self.rank_population(population)[0][0]
        best = population[best_id]

        return best


    def find_paths(self):
        self.find_local_paths_ucs(self.map.start_pos)
        
        for cell in self.map.must_pass_points:
            self.find_local_paths_ucs(cell)
            pass

        n_tsp_points = len(self.map.must_pass_points)

        tsp_path = self.evolve(initial_size= 20 , size_for_best=10,
        mutation_rate=0.3, n_generations= 20000)

        ans = self.calculate_route_dist(tsp_path)
        self.generations_cost = str(ans) + "\n" + self.generations_cost
        found = (False if ans >= self.n_cells ** 2 else True)
        tsp_path.reverse()

        paths =[]
        if found:
            for i in range(len(tsp_path)):
                if i == len(tsp_path) - 1:
                    continue

                cur_node = tsp_path[i]
                cur_node_id = self.calculate_id(tsp_path[i])
                pre_node_id = self.calculate_id(tsp_path[i + 1])

                while (cur_node != None and cur_node_id != pre_node_id):
                    paths.append(cur_node)
                    cur_node = self.previous_cells[pre_node_id][cur_node_id]

                    cur_node_id = self.calculate_id(cur_node)
                pass
        paths.append(self.map.start_pos)
        paths.reverse()
        
        finding_process = [] # no finding process

        return found, paths, finding_process, self.generations_cost
        

if __name__ == "__main__":
    filepath = './input/level_3/input2.txt'
    mp = Map(filepath)

    algo = Must_Pass_Algo(mp)
    #print(algo.map.must_pass_points)
    
    found, paths, closes, ans = algo.find_paths()
    
    print(found)
    print(paths)
    print(len(paths))
    print(closes)
    print("Cost: ",ans)
    
  