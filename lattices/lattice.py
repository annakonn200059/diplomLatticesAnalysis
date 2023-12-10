from utils import diff_arrays


class Lattice:
    def __init__(self, factor_arr):
        self.n = 0
        self.m = 0
        self.edges_list = []
        self.factor_arr = factor_arr
        self.flatten_arr = factor_arr

    '''
    arr1-элемент предыдущего уровня
    arr2-элемент текущего уровня
    '''
    def compare_arr(self, dict1, dict2):
        res = False
        values_arr1 = list(dict1.values())
        #values_arr2 = list(dict2.values())
        current_arr1 = []
        for k in range(0, len(values_arr1) - 1):
            for s in range(k + 1, len(values_arr1)):
                new_congruence = []
                arr = sorted(values_arr1[k] + values_arr1[s])
                new_congruence.append(arr)
                diff_arr = diff_arrays(values_arr1, arr)
                for o in diff_arr:
                    if type(o) == list:
                        new_congruence.append(o)
                    else:
                        new_congruence.append([o])
                new_congruence.sort()
                #print(values_arr1, arr, new_congruence)
                current_arr1.append(new_congruence)
                if new_congruence == current_arr1[len(current_arr1) - 1]:
                    return True
        print('\n')
        return res

    def findIndex(self, el):
        for i in range(len(self.flatten_arr)):
            if self.flatten_arr[i] == el:
                return i

    def make_level_arr(self):
        temp_arr, ans = [], []
        for i in range(0, len(self.factor_arr)):
            if i == 0:
                continue
            next_factor_level = self.factor_arr[i][0]
            cur_factor_level = self.factor_arr[i - 1][0]
            if next_factor_level == cur_factor_level:
                temp_arr.append([cur_factor_level, self.factor_arr[i - 1][1]])
            else:
                ans.append(temp_arr)
                temp_arr.append([cur_factor_level, self.factor_arr[i - 1][1]])
                temp_arr = []
            if i == len(self.factor_arr) - 1:
                temp_arr.append([next_factor_level, self.factor_arr[i][1]])
                ans.append(temp_arr)
                break
        #for i in ans:
            #print(i)
        #print('\n')
        return ans

    def main_fun(self):
        self.factor_arr = self.make_level_arr()
        lattice_height = len(self.factor_arr)
        lattice_width = 0
        for i in range(0, len(self.factor_arr) - 1):
            if lattice_width < len(self.factor_arr[i]):
                lattice_width = len(self.factor_arr[i])
            if i == 0:
                continue
            for j in range(0, len(self.factor_arr[i])):
                for k in range(0, len(self.factor_arr[i - 1])):
                    if self.compare_arr(self.factor_arr[i - 1][k][1], self.factor_arr[i][j][1]):
                        self.edges_list.append([self.findIndex(self.factor_arr[i][j]), self.findIndex(self.factor_arr[i - 1][k])])
        for i in range(0, len(self.factor_arr[len(self.factor_arr) - 1])):
            for j in range(0, len(self.factor_arr[len(self.factor_arr) - 2])):
                self.edges_list.append([self.findIndex(self.factor_arr[len(self.factor_arr) - 1][i]), self.findIndex(self.factor_arr[len(self.factor_arr) - 2][j])])
        return self.edges_list, lattice_width, lattice_height





