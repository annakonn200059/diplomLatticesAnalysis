def make_dict_factor_vertexes(factor_graph, vertexes):
    max_vertex = max(vertexes) + 1
    dict_factor_vertexes = {}
    for v in factor_graph:
        if len(v) == 1:
            dict_factor_vertexes[v[0]] = v
        else:
            dict_factor_vertexes[max_vertex] = v
            max_vertex += 1
    return dict_factor_vertexes


def find_vertex_edges(v1, v2, i, j, edges_of_factor, adjacency_list):
    loop = False
    edge = False
    edges_arr = []
    for k in v1:
        if k in adjacency_list.keys():
            for c in adjacency_list[k]:
                '''
                if c in v1:
                    if not loop:
                        loop = True
                        if [i, i] not in edges_of_factor:
                            edges_arr.append([i, i])
                            '''
                if c in v2:
                    if not edge:
                        edge = True
                        if [i, j] not in edges_of_factor:
                            edges_arr.append([i, j])
    return edges_arr


def make_factor_graph_from_factor_arr(factor_graph, adjacency_list, vertexes):
    edges_of_factor = []
    dict_factor_vertexes = make_dict_factor_vertexes(factor_graph, vertexes)
    for i in dict_factor_vertexes:
        for j in dict_factor_vertexes:
            if i != j:
                v1 = dict_factor_vertexes[i]
                v2 = dict_factor_vertexes[j]
                v1_edges = find_vertex_edges(v1, v2, i, j, edges_of_factor, adjacency_list)
                edges_of_factor.extend(v1_edges)
                v2_edges = find_vertex_edges(v2, v1, j, i, edges_of_factor, adjacency_list)
                edges_of_factor.extend(v2_edges)
    return [edges_of_factor, dict_factor_vertexes]
