def diff_arrays(arr1, arr2) -> list:
    list_difference = []
    for element in arr1:
        if len(element) == 1 and element[0] not in arr2:
            list_difference.append(element[0])
        else:
            flag = True
            for j in element:
                if j in arr2:
                    flag = False
                    break
            if flag:
                list_difference.append(element)

    return list_difference


def fill_dict(dict, el, upper_matrix_form):
    if not el in dict:
        dict[el] = [upper_matrix_form]
    else:
        dict[el].append(upper_matrix_form)


def get_node_with_positions(nodes, level_arr):
    x_spacing = 100  # Расстояние по горизонтали между вершинами
    y_spacing = 100  # Расстояние по вертикали между уровнями

    ans = []
    #номер уровня из массива level_arr
    level_idx = level_arr[0][0]
    #номер уровня по порядку 0,1,2...
    cur_level_idx = 0
    #номер элемента в текущем уровне (по горизонтали)
    level_el_idx = -1

    # Считаем количество элементов на каждом уровне
    level_counts = {}
    for level in level_arr:
        if level[0] in level_counts:
            level_counts[level[0]] += 1
        else:
            level_counts[level[0]] = 1

    for node_id in range(0, len(nodes)):
        node = str(nodes[node_id])

        if not level_idx == level_arr[node_id][0]:
            level_idx = level_arr[node_id][0]
            cur_level_idx += 1
            level_el_idx = 0
        else:
            level_el_idx += 1

        # Вычисляем начальное смещение x так, чтобы узлы были центрированы
        x_offset = -(level_counts[level_idx] - 1) * x_spacing / 2

        ans.append({'data': {'id': node, 'label': node},
                    'position': {'x':  x_offset + level_el_idx * x_spacing, 'y': cur_level_idx * y_spacing}})

    return ans


def edges_to_cytoscape_format(edges, level_arr=None):
    # Создаем множество нод
    nodes = set()
    for edge in edges:
        nodes.add(edge[0])
        nodes.add(edge[1])

    # Преобразуем ноды в формат для Cytoscape
    if level_arr:
        node_elements = get_node_with_positions(list(nodes), level_arr)
    else:
        node_elements = [{'data': {'id': str(node_idx), 'label': str(node_idx)}}
                         for node_idx in nodes]

    # Преобразуем дуги в формат для Cytoscape
    edge_elements = [{'data': {'source': str(edge[0]), 'target': str(edge[1])}} for edge in edges]

    # Объединяем узлы и дуги
    return node_elements + edge_elements
