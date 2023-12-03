from utils import diff_arrays


def find_all_congruences(vertexes, n):
    factor_arr = [[[0], [[[i] for i in vertexes]]]]
    #print("Тождественная конгруэнция: ", "\n", factor_arr)
    for i in range(1, n, 1):
        new_level = []
        prev_level = factor_arr[i - 1]
        if i == n - 1:
            factor_arr.append([[n-1], [[vertexes]]])
            break
        for j in range(0, len(prev_level[1]), 1):
            for k in range(0, len(prev_level[1][j]) - 1):
                for s in range(k + 1, len(prev_level[1][j])):
                    new_congruence = []
                    arr = sorted(prev_level[1][j][k] + prev_level[1][j][s])
                    new_congruence.append(arr)
                    diff_arr = diff_arrays(prev_level[1][j], arr)
                    for o in diff_arr:
                        if type(o) == list:
                            new_congruence.append(o)
                        else:
                            new_congruence.append([o])
                    new_congruence.sort()
                    if new_congruence not in new_level:
                        new_level.append(new_congruence)

        factor_arr.append([[i], new_level])
    #print("Все возможные потенциальные конгруэнции исходного турнира: ", "\n", factor_arr)
    return factor_arr
