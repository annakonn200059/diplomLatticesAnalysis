import networkx as nx
from math import ceil
import time
import multiprocessing
from lattices.lattice import Lattice
from tournaments.tournaments import Tournaments
from tournaments.formatInput import FormatInput


def fill_general_dict(dict, el, upper_matrix_form):
    # if not el in dict:
    #     dict[str(el)] = [upper_matrix_form]
    # else:
    #     dict[str(el)].append(upper_matrix_form)
    if not el in dict:
        dict[str(el)] = 1
    else:
        dict[str(el)] += 1


def get_matrix_from_edges(g_sorted, n):
    matrix = [[0] * n for _ in range(n)]
    for edge in g_sorted:
        i, j = edge[0], edge[1]
        matrix[i][j] = 1
        matrix[j][i] = 1

    return matrix


def get_process_tuples(n):
    tuples_arr = []
    graphs_per_process = 1
    batch_amount = ceil(n / graphs_per_process)
    for i in range(batch_amount):
        from_idx = i * graphs_per_process
        to_idx = min((i + 1) * graphs_per_process - 1, n - 1)
        tuples_arr.append((from_idx, to_idx))

    return tuples_arr


def fill_characteristics_tables(first_characteristic_name, second_characteristic_name, ch_dict, graph_list,
                                upper_matrix):
    key = str(first_characteristic_name) + '_' + str(second_characteristic_name)
    ch_dict[key] += 1

    if graph_list[key] is not None:
        graph_list[key].append(upper_matrix)
        if len(graph_list[key]) > 10:
            graph_list[key] = None


class Graphs:
    def __init__(self, v_n):
        # общие отдельные характеристики решеток
        self.order_dict = {}
        self.height_dict = {}
        self.width_dict = {}
        # таблицы для пересечения характеристик и списки графов < 10 штук
        self.height_width_dict = {}
        self.height_width_graphs_list = {}
        self.width_order_dict = {}
        self.width_order_graphs_list = {}
        self.order_height_dict = {}
        self.order_height_graphs_list = {}

        self.g_n = v_n
        self.processes_parts = {
            3: get_process_tuples(2),
            4: get_process_tuples(4),
            5: get_process_tuples(12),
            6: get_process_tuples(56),
            7: get_process_tuples(456),
            8: get_process_tuples(6880)
        }
        self.bytes_per_string = {3: 5, 4: 8, 5: 12, 6: 17, 7: 23, 8: 30}

    def gen_by_parts(self, args):
        string_bytes = self.bytes_per_string[self.g_n]
        height_width_dict = {}
        height_width_graphs_list = {}
        width_order_dict = {}
        width_order_graphs_list = {}
        order_height_dict = {}
        order_height_graphs_list = {}
        order_dict = {}
        height_dict = {}
        width_dict = {}

        # таблица высота-ширина
        for i in range(2, self.g_n + 1):
            for j in range(1, 200):
                height_width_dict[str(i) + '_' + str(j)] = 0
                height_width_graphs_list[str(i) + '_' + str(j)] = []

        # таблица ширина-кол-во
        for i in range(1, 200):
            for j in range(2, 2 ** (self.g_n - 1) + 1):
                width_order_dict[str(i) + '_' + str(j)] = 0
                width_order_graphs_list[str(i) + '_' + str(j)] = []

        # таблица кол-во-высота
        for i in range(2, 2 ** (self.g_n - 1) + 1):
            for j in range(2, self.g_n + 1):
                order_height_dict[str(i) + '_' + str(j)] = 0
                order_height_graphs_list[str(i) + '_' + str(j)] = []

        start = args[0]
        end = args[1]
        with open("in_files/" + str(self.g_n) + 'in.txt', 'r') as graphs_file:
            graphs_file.seek(string_bytes * start)
            while True:
                graph = graphs_file.readline().rstrip()
                #print('graph', graph, 'start', start, 'end', end, 'string_bytes', string_bytes, 'graphs_file.tell()', graphs_file.tell(), 'cond', graphs_file.tell() > string_bytes * (end + 1))
                if not graph:
                    break

                if graphs_file.tell() > string_bytes * (end + 1):
                    break

                upper_matrix_form = graph.strip()
                tournament_edges_list, adjacency_list, vertexes = FormatInput(upper_matrix_form, self.g_n).upperTriangleToEdgeList()
                factor_arr = Tournaments(tournament_edges_list, adjacency_list, vertexes, self.g_n, upper_matrix_form).main_fun()
                lattice = Lattice(factor_arr)
                lattice_edges, lattice_width, lattice_height = lattice.main_fun()
                G = nx.Graph(lattice_edges)
                lattice_order = G.order()
                fill_general_dict(order_dict, lattice_order, upper_matrix_form)
                fill_general_dict(height_dict, lattice_height, upper_matrix_form)
                fill_general_dict(width_dict, lattice_width, upper_matrix_form)

                fill_characteristics_tables(lattice_height, lattice_width, height_width_dict, height_width_graphs_list,
                                            upper_matrix_form)
                fill_characteristics_tables(lattice_width, lattice_order, width_order_dict, width_order_graphs_list,
                                            upper_matrix_form)
                fill_characteristics_tables(lattice_order, lattice_height, order_height_dict, order_height_graphs_list,
                                            upper_matrix_form)

        print('Done ', start, '-', end)
        return height_width_dict, height_width_graphs_list, width_order_dict, width_order_graphs_list, \
               order_height_dict, order_height_graphs_list, order_dict, height_dict, width_dict

    def find_all_characteristics(self):
        pool = multiprocessing.Pool(processes=6)
        res = pool.map(self.gen_by_parts, self.processes_parts[self.g_n])

        for (height_width_dict, height_width_graphs_list, width_order_dict, width_order_graphs_list, order_height_dict,
             order_height_graphs_list, order_dict, height_dict, width_dict) in res:
            for key, value in order_dict.items():
                self.order_dict[key] += value

            for key, value in height_dict.items():
                self.height_dict[key] += value

            for key, value in width_dict.items():
                self.width_dict[key] += value

            for key, value in height_width_dict.items():
                self.height_width_dict[key] += value
            for graphs_key, graphs_value in height_width_graphs_list.items():
                if graphs_value is not None:
                    self.height_width_graphs_list[graphs_key].extend(graphs_value)

            for key, value in width_order_dict.items():
                self.width_order_dict[key] += value
            for graphs_key, graphs_value in width_order_graphs_list.items():
                if graphs_value is not None:
                    self.width_order_graphs_list[graphs_key].extend(graphs_value)

            for key, value in order_height_dict.items():
                self.order_height_dict[key] += value
            for graphs_key, graphs_value in order_height_graphs_list.items():
                if graphs_value is not None:
                    self.order_height_graphs_list[graphs_key].extend(graphs_value)

        for key, val in self.height_width_graphs_list.items():
            if self.height_width_dict[key] > 10:
                self.height_width_graphs_list[key] = None

        for key, val in self.width_order_graphs_list.items():
            if self.width_order_dict[key] > 10:
                self.width_order_graphs_list[key] = None

        for key, val in self.order_height_graphs_list.items():
            if self.order_height_dict[key] > 10:
                self.order_height_graphs_list[key] = None

        return

    def saveGeneralCharachteristicsToFiles(self):
        order_dict = dict(sorted(self.order_dict.items()))
        height_dict = dict(sorted(self.height_dict.items()))
        width_dict = dict(sorted(self.width_dict.items()))

        target = str(self.g_n) + '_characteristics.txt'
        with open(target, encoding='UTF-8', mode='a') as fileCharacteristics:
            fileCharacteristics.write('Порядок:\n')
            for i in order_dict:
                if order_dict[i]:
                    fileCharacteristics.write(str(i) + ': ' + str(order_dict[i]) + '\n')

            fileCharacteristics.write('Ширина:\n')
            for i in width_dict:
                if width_dict[i]:
                    fileCharacteristics.write(str(i) + ': ' + str(width_dict[i]) + '\n')

            fileCharacteristics.write('Высота:\n')
            for i in height_dict:
                if height_dict[i]:
                    fileCharacteristics.write(str(i) + ': ' + str(height_dict[i]) + '\n')

    def main_fun(self):
        # таблица высота-ширина
        for i in range(2, self.g_n + 1):
            for j in range(1, 200):
                self.height_width_dict[str(i) + '_' + str(j)] = 0
                self.height_width_graphs_list[str(i) + '_' + str(j)] = []

        # таблица ширина-кол-во
        for i in range(1, 200):
            for j in range(2, 2 ** (self.g_n - 1) + 1):
                self.width_order_dict[str(i) + '_' + str(j)] = 0
                self.width_order_graphs_list[str(i) + '_' + str(j)] = []

        # таблица кол-во-высота
        for i in range(2, 2 ** (self.g_n - 1) + 1):
            for j in range(2, self.g_n + 1):
                self.order_height_dict[str(i) + '_' + str(j)] = 0
                self.order_height_graphs_list[str(i) + '_' + str(j)] = []

        for i in range(2, self.g_n + 1):
            self.height_dict[str(i)] = 0

        for i in range(1, 200):
            self.width_dict[str(i)] = 0

        for i in range(2, 2 ** (self.g_n - 1) + 1):
            self.order_dict[str(i)] = 0

        self.find_all_characteristics()

        with open(str(self.g_n) + 'table_height_width.txt', 'w') as table_file:
            new_graph = [list(self.height_width_dict.values())[i:i + self.g_n - 1] for i in
                         range(0, len(list(self.height_width_dict.values())), self.g_n - 1)]
            for line in new_graph:
                print("\t".join(map(str, line)), file=table_file, sep='\n')

        with open(str(self.g_n) + 'table_width_order.txt', 'w') as table_file:
            new_graph = [list(self.width_order_dict.values())[i:i + self.g_n - 1] for i in
                         range(0, len(list(self.width_order_dict.values())), self.g_n - 1)]
            for line in new_graph:
                print("\t".join(map(str, line)), file=table_file, sep='\n')

        with open(str(self.g_n) + 'table_order_height.txt', 'w') as table_file:
            new_graph = [list(self.order_height_dict.values())[i:i + self.g_n - 1] for i in
                         range(0, len(list(self.order_height_dict.values())), self.g_n - 1)]
            for line in new_graph:
                print("\t".join(map(str, line)), file=table_file, sep='\n')

        with open(str(self.g_n) + 'height_width_graphs_list.txt', 'w') as graphs_list_file:
            for key, value in self.height_width_graphs_list.items():
                if value is not None and len(value) > 0:
                    print(key + ": " + str(len(value)) + str(value), file=graphs_list_file, sep='\n')

        with open(str(self.g_n) + 'width_order_graphs_list.txt', 'w') as graphs_list_file:
            for key, value in self.width_order_graphs_list.items():
                if value is not None and len(value) > 0:
                    print(key + ": " + str(len(value)) + str(value), file=graphs_list_file, sep='\n')

        with open(str(self.g_n) + 'order_height_graphs_list.txt', 'w') as graphs_list_file:
            for key, value in self.order_height_graphs_list.items():
                if value is not None and len(value) > 0:
                    print(key + ": " + str(len(value)) + str(value), file=graphs_list_file, sep='\n')

        self.saveGeneralCharachteristicsToFiles()

        return


if __name__ == "__main__":
    n = int(input('Введите количество вершин в графах: '))

    if n > 11:
        print('Нельзя больше 11 вершин')
        exit(0)

    cls = Graphs(n)
    t12 = time.perf_counter()
    cls.main_fun()
    t22 = time.perf_counter()
    print(f'Скорость работы: {(t22 - t12) * 1000} мс')

