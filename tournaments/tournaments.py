from networkx.algorithms import tournament
import networkx as nx
from tournaments.findTournaments import make_factor_graph_from_factor_arr


class Tournaments:
    def __init__(self, edges_list, adjacency_list, vertexes, n, upper_matrix_form):
        self.n = n
        self.vertexes = vertexes
        self.edges_list = edges_list
        self.adjacency_list = adjacency_list
        self.tournament_list = []
        self.ans_factor_arr = []
        self.upper_matrix_form = upper_matrix_form

    def format_output_tournaments(self):
        for i in range(len(self.tournament_list)):
            print(f"   Факторграф (фото №{i + 1})")
            print(f"   уровень в решетке {self.ans_factor_arr[i][0]}")
            print("    ", self.ans_factor_arr[i][1])
            print("        Список дуг факторграфа")
            print("        ", self.tournament_list[i], "\n")

    def main_fun(self, factor_arr):
        #print("Дан орграф: ", "\n", self.edges_list)
        #print(self.upper_matrix_form)
        g = nx.DiGraph(self.edges_list)
        if not tournament.is_tournament(g):
            print("Данный орграф не является турниром")
            return
        else:
            #print("Является турниром")
            #print('\nТурниры конгруэнций:\n')
            for i in range(len(factor_arr)):
                for j in factor_arr[i][1]:
                    res = make_factor_graph_from_factor_arr(j, self.adjacency_list, self.vertexes)
                    probable_tournament, factor_vertexes = res[0], res[1]
                    factor_graph = nx.DiGraph(probable_tournament)
                    if len(factor_graph) > 0:
                        if tournament.is_tournament(factor_graph):
                            self.ans_factor_arr.append([factor_arr[i][0][0], factor_vertexes])
                            #self.tournament_list.append(probable_tournament)
                    if len(factor_graph) == 0:
                        self.ans_factor_arr.append([factor_arr[i][0][0], factor_vertexes])
                        #self.tournament_list.append(probable_tournament)
            #self.format_output_tournaments()
        return self.ans_factor_arr

