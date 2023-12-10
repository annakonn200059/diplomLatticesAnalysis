
class FormatInput:
    def __init__(self, upper_matrix_form, n):
        self.n = n
        self.edges_list = []
        self.upper_matrix_form = upper_matrix_form
        self.adjacency_list = {}

    def add_to_adj_list(self, node1, node2):
        temp = []
        if node1 not in self.adjacency_list:
            temp.append(node2)
            self.adjacency_list[node1] = temp

        elif node1 in self.adjacency_list:
            temp.extend(self.adjacency_list[node1])
            temp.append(node2)
            self.adjacency_list[node1] = temp

    def digraph6_to_directed_edges(self):
        # Извлечение количества вершин из второго символа
        num_vertices = ord(self.upper_matrix_form[1]) - 63

        # Конвертация строки code[2]...code[P-1] в бинарную строку
        binary_string = ''.join(format(ord(char) - 63, '06b') for char in self.upper_matrix_form[2:])

        # Извлекаем первые n^2 бит для матрицы смежности
        binary_string = binary_string[:num_vertices ** 2]

        # Генерация матрицы смежности из бинарной строки
        adjacency_matrix = [list(map(int, binary_string[i:i + num_vertices]))
                            for i in range(0, len(binary_string), num_vertices)]

        # Генерация списка дуг из матрицы смежности
        edges = [(i, j) for i in range(num_vertices) for j in range(num_vertices)
                 if adjacency_matrix[i][j] == 1]

        # Генерация списка смежности из матрицы смежности
        adjacency_list = {}
        for i in range(num_vertices):
            # Добавляем в список смежности только те вершины, которые имеют исходящие рёбра
            adjacent_vertices = [j for j in range(num_vertices) if adjacency_matrix[i][j] == 1]
            if adjacent_vertices:
                adjacency_list[i] = adjacent_vertices

        # Генерация списка вершин
        nodes_list = list(range(num_vertices))

        # Генерация верхней матричной формы графа (все элементы над главной диагональю)
        upper_matrix_form = [adjacency_matrix[i][j] for i in range(num_vertices) for j in range(i + 1, num_vertices)]

        return edges, adjacency_list, nodes_list, upper_matrix_form

    def upperTriangleToEdgeList(self):
        #print(self.upper_matrix_form)
        # количество элементов над главной диагональю матрицы смежности
        upper_form_len = (self.n * (self.n - 1)) // 2
        if not upper_form_len == len(self.upper_matrix_form):
            print("Матричная форма не соответствует количеству вершин")
            return

        cur = 0
        stop = self.n - 1
        for i in range(0, self.n - 1):
            column = i + 1
            for j in range(cur, stop):
                if j >= len(self.upper_matrix_form):
                    print("Количество вершин не соответствует введенному турниру")
                if self.upper_matrix_form[j] == '1':
                    self.edges_list.append([i, column])
                    self.add_to_adj_list(i, column)
                else:
                    self.edges_list.append([column, i])
                    self.add_to_adj_list(column, i)
                column += 1
            copy_cur = cur
            cur = stop
            stop += stop - copy_cur - 1
        
        return self.edges_list, self.adjacency_list

    def upper_matrix_to_full_matrix(self):
        """
        Converts the upper matrix form of an oriented graph to its full adjacency matrix.
        :return: 2D list representing the full adjacency matrix of the graph.
        """
        full_matrix = [['0'] * self.n for _ in range(self.n)]
        index = 0
        for i in range(self.n):
            for j in range(self.n):
                if i < j:  # Элементы над главной диагональю
                    full_matrix[i][j] = self.upper_matrix_form[index]
                    # Инвертируется бит для элементов под главной диагональю
                    full_matrix[j][i] = '1' if self.upper_matrix_form[index] == '0' else '0'
                    index += 1

        return full_matrix

    def to_digraph6(self):
        # Построение полной матрицы смежности из верхней матричной формы
        full_matrix = self.upper_matrix_to_full_matrix()

        # Преобразование полной матрицы смежности в бинарную строку
        binary_string = ''.join(''.join(row) for row in full_matrix)

        # Дополнение бинарной строки нулями до кратности 6 для формата digraph6
        while len(binary_string) % 6 != 0:
            binary_string += '0'

        # Преобразование бинарной строки в строку формата digraph6
        g6_str = '&'
        g6_str += chr(self.n + 63)  # Добавление символа для количества вершин

        for i in range(0, len(binary_string), 6):
            # Конвертация каждой 6-битной группы в соответствующий символ digraph6
            char_code = int(binary_string[i:i+6], 2) + 63
            g6_str += chr(char_code)

        return g6_str

