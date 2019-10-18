# -*- coding: latin-1 -*-

from igraph import *

def read_graph(path):
    g = Graph()

    edges_count = 0
    nodes_count = 0

    f = open(path, "r")

    if f.mode == "r":
        lines = f.readlines()
        for line in lines:
            if "Nodes" in line:
                g.add_vertices(int(line[6:]))
                for node in g.vs:
                    node["label"] = nodes_count + 1
                    node["id"] = nodes_count + 1
                    node["terminal"] = False
                    nodes_count = nodes_count + 1
            elif line.find("E ") == 0:
                n = line.rsplit(" ")
                g.add_edges([(int(n[1]) - 1, int(n[2]) - 1)])
                g.es[edges_count]["weight"] = int(n[3])
                g.es[edges_count]["label"] = int(n[3])
                g.es[edges_count]["id"] = edges_count + 1
                edges_count = edges_count + 1
            elif line.find("T ") == 0:
                n = line.rsplit(" ")
                g.vs[int(n[1]) - 1]["terminal"] = True
    return g

#Plotar o gráfico
#Atenção: não recomendado para grafos grandes
#g = read_graph("./ES10FST/es10fst01.stp")
#layout = g.layout("fr")
#color_dict = {False: "white", True: "grey"}
#g.vs["color"] = [color_dict[terminal] for terminal in g.vs["terminal"]]
#plot(g, layout = layout)
