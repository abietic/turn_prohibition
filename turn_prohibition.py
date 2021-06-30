import networkx as nx
from copy import deepcopy

from numpy import select


def gen_test_case1():
    fh = open("test_case_1.edgelist", "rb")
    G = nx.read_edgelist(fh, nodetype=int)
    fh.close()
    return G


def gen_test_case2():
    fh = open("test_case_2.edgelist", "rb")
    G = nx.Graph(nx.read_edgelist(fh, nodetype=int, data=(("weight", float),)))
    label_map = {"CA1": 1, "CA2": 2, "WA": 3, "UT": 4, "IL": 5, "TX": 6, "MI": 7,
                 "CO": 8, "NE": 9, "GA": 10, "MD": 11, "PA": 12, "NY": 13, "NJ": 14}
    for label, id in label_map.items():
        G.nodes[id]["label"] = label
    fh.close()
    return G


def choose_node_default(g=nx.Graph(), has_special_node=False, special_node_label=-1):
    return min(g.degree, key=lambda k: k[1])[0]

# TODO didn't support the situation when special node already exist
def check_connectivity(g=nx.Graph(), node_label=-1, has_special_node=False, special_node_label=-1):
    connected = True
    reborn_turns = None
    special_nodes_and_comps = None
    g = deepcopy(g)
    tg = deepcopy(g)
    tg.remove_node(node_label)
    sub_graph_cnt = nx.number_connected_components(tg)
    # if deletion of the node make the graph's connectivity 
    if sub_graph_cnt > 1:
        connected = False
        reborn_turns = set()
        special_nodes_and_comps = {}
        special_node_candidates = sorted(list(g.neighbors(node_label)))
        special_link_candidate_cnt = len(special_node_candidates)
        # if all candidate links are special links
        if sub_graph_cnt != special_link_candidate_cnt:
            cur_con_cnt = sub_graph_cnt + 1
            tg.add_node(node_label)
            special_nodes = list()
            # select special nodes
            for cn in special_node_candidates:
                tg.add_edge(node_label, cn)
                tes_con_cnt = nx.number_connected_components(tg)
                # found a valid special link, select it
                if tes_con_cnt == cur_con_cnt - 1:
                    special_nodes.append(cn)
                # this candidate is not valid any more, drop it and continue the selection
                else:
                    tg.remove_edge(node_label, cn)
                if tes_con_cnt == 1:
                    break
            special_node_candidates = sorted(special_nodes)
            tg.remove_node(node_label)
        for f in range(sub_graph_cnt):
            for t in range(f+1, sub_graph_cnt):
                turn = (
                    special_node_candidates[f], node_label, special_node_candidates[t])
                reborn_turns.add(turn)
        for sp_n in special_node_candidates:
            comp = tg.subgraph(
                nx.node_connected_components(tg, sp_n)).copy()
            if has_special_node and comp.has_node(special_node_label):
                special_nodes_and_comps[special_node_label] = comp
                continue
            special_nodes_and_comps[sp_n] = comp
    return connected, reborn_turns, special_nodes_and_comps


def turn_prohibition(g=nx.Graph(), has_special_node=False, special_node_label=-1, choose_node=choose_node_default):
    if g.number_of_nodes() == 1:
        return
    # have a copy of the original graph to avoid mutation
    g = deepcopy(g)
    # set to store prohibited turns
    turns_need_prohibit = set()
    # loop to delete node in the graph one by one
    while g.number_of_nodes() > 1:
        # choose a node that fulfil the requirement
        node_chosen = choose_node(g, has_special_node, special_node_label)
        # get it's adjacent nodes
        adjs = sorted(list(g.neighbors(node_chosen)))
        # cal may probibit turns
        may_prohib = set()
        adj_cnt = len(adjs)
        for f in range(adj_cnt):
            for t in range(f + 1, adj_cnt):
                turn = (adjs[f], node_chosen, adjs[t])
                may_prohib.add(turn)
    return turns_need_prohibit
