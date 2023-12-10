import networkx as nx
from math import ceil
import time
import multiprocessing
from lattices.lattice import Lattice
from tournaments.congruences import find_all_congruences
from tournaments.tournaments import Tournaments
from tournaments.formatInput import FormatInput
import logging
# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def read_file_to_memory(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()


def fill_dict_with_int_values(dict, idx, value=None):
    increment = value if value else 1
    if not str(idx) in dict:
        dict[str(idx)] = increment
    else:
        dict[str(idx)] += increment


def fill_dict_with_list_values(dict, idx, value):
    if not idx in dict:
        dict[str(idx)] = value
    else:
        dict[str(idx)].extend(value)


def get_matrix_from_edges(g_sorted, n):
    matrix = [[0] * n for _ in range(n)]
    for edge in g_sorted:
        i, j = edge[0], edge[1]
        matrix[i][j] = 1
        matrix[j][i] = 1

    return matrix


def get_process_tuples(n):
    tuples_arr = []
    graphs_per_process = 2000
    batch_amount = ceil(n / graphs_per_process)
    for i in range(batch_amount):
        from_idx = i * graphs_per_process
        to_idx = min((i + 1) * graphs_per_process - 1, n - 1)
        tuples_arr.append((from_idx, to_idx))

    return tuples_arr


def fill_characteristics_tables(first, second, name_1, name_2, dicts, upper_matrix):
    key = f"{first}_{second}"
    counter_dict_key = f"{name_1}_{name_2}"
    list_dict_key = f"{counter_dict_key}_graphs"
    fill_dict_with_int_values(dicts[counter_dict_key], key)

    if key in dicts[list_dict_key]:
        if dicts[list_dict_key][key] is not None:
            dicts[list_dict_key][key].append(upper_matrix)
            if len(dicts[list_dict_key][key]) > 10:
                dicts[list_dict_key][key] = None
    else:
        dicts[list_dict_key][key] = [upper_matrix]


class Graphs:
    def __init__(self, v_n):
        # общие отдельные характеристики решеток
        self.order_dict = {}
        self.height_dict = {}
        self.width_dict = {}
        # таблицы для пересечения характеристик и списки графов < 10 штук
        self.height_width_dict = {}  # таблица высота-ширина
        self.height_width_graphs_list = {}
        self.width_order_dict = {}  # таблица ширина-кол-во
        self.width_order_graphs_list = {}
        self.order_height_dict = {}  # таблица кол-во-высота
        self.order_height_graphs_list = {}
        self.res_files_directory = 'out_files/'

        self.g_n = v_n
        # self.processes_parts = {
        #     3: get_process_tuples(2),
        #     4: get_process_tuples(4),
        #     5: get_process_tuples(12),
        #     6: get_process_tuples(56),
        #     7: get_process_tuples(456),
        #     8: get_process_tuples(6880),
        #     9: get_process_tuples(191536),
        #     #10: get_process_tuples(9733056),
        #     #11: get_process_tuples(903753248)
        # }
        #self.bytes_per_string = {3: 5, 4: 8, 5: 12, 6: 17, 7: 23, 8: 30, 9: 38, 10: 47, 11: 57}  # количество символов в строке + 2
        self.vertexes = list(range(self.g_n))
        #Все возможные потенциальные конгруэнции исходного турнира
        self.factor_arr = find_all_congruences(self.vertexes, self.g_n)

    def gen_by_parts(self, data_part):
        logging.info(f"Process {multiprocessing.current_process().name} started working")
        #string_bytes = self.bytes_per_string[self.g_n]
        dicts = {
            "height_width": {},
            "height_width_graphs": {},
            "width_order": {},
            "width_order_graphs": {},
            "order_height": {},
            "order_height_graphs": {},
            "order": {},
            "height": {},
            "width": {},
        }

        for line in data_part:
            graph = line.strip()
            # print('graph', graph, 'start', start, 'end', end, 'string_bytes', string_bytes, 'graphs_file.tell()', graphs_file.tell(), 'cond', graphs_file.tell() > string_bytes * (end + 1))
            if not graph:
                break

            upper_matrix_form = graph.strip()
            edges_list, adj_list = FormatInput(upper_matrix_form, self.g_n).upperTriangleToEdgeList()
            factor_arr = Tournaments(edges_list, adj_list, self.vertexes, self.g_n, upper_matrix_form).main_fun(self.factor_arr)
            lattice = Lattice(factor_arr)
            edges, width, height = lattice.main_fun()
            G = nx.Graph(edges)
            order = G.order()

            fill_dict_with_int_values(dicts["order"], order)
            fill_dict_with_int_values(dicts["height"], height)
            fill_dict_with_int_values(dicts["width"], width)

            fill_characteristics_tables(height, width, 'height', 'width', dicts, upper_matrix_form)
            fill_characteristics_tables(width, order, 'width', 'order', dicts, upper_matrix_form)
            fill_characteristics_tables(order, height, 'order', 'height', dicts, upper_matrix_form)

        #print('Done ', start, '-', end)
        logging.info(f"Process {multiprocessing.current_process().name} finished working")
        return list(dicts.values())

    def get_data_parts(self, data):
        num_processes = min(multiprocessing.cpu_count(), len(data))  # Не создавать больше процессов, чем данных
        part_size = max(1, len(data) // num_processes)
        parts = [data[i:i + part_size] for i in range(0, len(data), part_size)]
        return parts

    def find_all_characteristics(self):
        #multiprocessing.cpu_count()
        file_path = f"in_files/{self.g_n}in.txt"
        file_data = read_file_to_memory(file_path)

        # Разбиваем данные файла на части для каждого процесса
        data_parts = self.get_data_parts(file_data)

        pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
        res = pool.map(self.gen_by_parts, data_parts)

        for (height_width_dict, height_width_graphs_list, width_order_dict, width_order_graphs_list, order_height_dict,
             order_height_graphs_list, order_dict, height_dict, width_dict) in res:

            for key, value in order_dict.items():
                fill_dict_with_int_values(self.order_dict, key, value)

            for key, value in height_dict.items():
                fill_dict_with_int_values(self.height_dict, key, value)

            for key, value in width_dict.items():
                fill_dict_with_int_values(self.width_dict, key, value)

            for key, value in height_width_dict.items():
                fill_dict_with_int_values(self.height_width_dict, key, value)
            for graphs_key, graphs_value in height_width_graphs_list.items():
                if graphs_value is not None:
                    fill_dict_with_list_values(self.height_width_graphs_list, graphs_key, graphs_value)

            for key, value in width_order_dict.items():
                fill_dict_with_int_values(self.width_order_dict, key, value)
            for graphs_key, graphs_value in width_order_graphs_list.items():
                if graphs_value is not None:
                    fill_dict_with_list_values(self.width_order_graphs_list, graphs_key, graphs_value)

            for key, value in order_height_dict.items():
                fill_dict_with_int_values(self.order_height_dict, key, value)
            for graphs_key, graphs_value in order_height_graphs_list.items():
                if graphs_value is not None:
                    fill_dict_with_list_values(self.order_height_graphs_list, graphs_key, graphs_value)

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
        order_dict = {int(k): v for k, v in self.order_dict.items()}
        height_dict = {int(k): v for k, v in self.height_dict.items()}
        width_dict = {int(k): v for k, v in self.width_dict.items()}

        order_dict = dict(sorted(order_dict.items()))
        height_dict = dict(sorted(height_dict.items()))
        width_dict = dict(sorted(width_dict.items()))

        target = self.res_files_directory + str(self.g_n) + '_characteristics.txt'
        with open(target, encoding='UTF-8', mode='w') as fileCharacteristics:
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

    def save_sorted_int_table_to_file(self, dict_to_sort, filename):
        sorted_items = sorted(dict_to_sort.items(), key=lambda item: item[1])
        with open(self.res_files_directory + str(self.g_n) + filename, 'w') as file:
            for key, value in sorted_items:
                if value is not None and value:
                    print(f"{key}: {value}", file=file)

    def save_sorted_by_len_graph_dict_to_file(self, dict_to_sort, filename):
        sorted_items = sorted(dict_to_sort.items(), key=lambda item: len(item[1]) if item[1] else 0)
        with open(self.res_files_directory + str(self.g_n) + filename, 'w') as file:
            for key, value in sorted_items:
                if value is not None and len(value) > 0:
                    print(key + ": " + str(len(value)) + '\n' + '\n'.join(value), file=file, sep='\n')

    def main_fun(self):
        self.find_all_characteristics()

        self.save_sorted_int_table_to_file(self.height_width_dict, 'table_height_width.txt')
        self.save_sorted_int_table_to_file(self.width_order_dict, 'table_width_order.txt')
        self.save_sorted_int_table_to_file(self.order_height_dict, 'table_order_height.txt')

        self.save_sorted_by_len_graph_dict_to_file(self.height_width_graphs_list, 'height_width_graphs_list.txt')
        self.save_sorted_by_len_graph_dict_to_file(self.width_order_graphs_list, 'width_order_graphs_list.txt')
        self.save_sorted_by_len_graph_dict_to_file(self.order_height_graphs_list, 'order_height_graphs_list.txt')

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
