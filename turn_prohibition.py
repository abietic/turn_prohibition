import networkx as nx
from copy import deepcopy
from networkx.algorithms import components

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

# TODO didn't consider special node
def choose_node_default(g=nx.Graph(), has_special_node=False, special_node_label=-1):
    nd_lst = list(g.nodes)
    if has_special_node:
        nd_lst.remove(special_node_label)
        if len(nd_lst) == 0:
            return special_node_label
    return min(g.degree(nd_lst), key=lambda k: k[1])[0]

def choose_node_link_weight(g=nx.Graph(), has_special_node=False, special_node_label=-1):
    nd_lst = list(g.nodes)
    if has_special_node:
        nd_lst.remove(special_node_label)
    def cal_weight(gr, n_2_cal):
        total_weight = 0
        for adj in list(gr.neighbors(n_2_cal)):
            total_weight += int(gr[n_2_cal][adj]['weight'])
        return total_weight
    weight_map = {n:cal_weight(g, n) for n in nd_lst}
    print('before del :')
    print (weight_map)
    return min(nd_lst, key=lambda k: weight_map[k])

# TODO didn't support the situation when special node already exist
def check_connectivity(g=nx.Graph(), node_label=-1, has_special_node=False, special_node_label=-1):
    connected = True
    reborn_turns = None
    special_nodes_and_comps = None
    g = deepcopy(g)
    tg = deepcopy(g)
    tg.remove_node(node_label)
    sub_graph_cnt = nx.number_connected_components(tg)
    # if deletion of the node breaks the graph's connectivity
    if sub_graph_cnt > 1:
        connected = False
        reborn_turns = set()
        special_nodes_and_comps = {}
        special_node_candidates = sorted(list(g.neighbors(node_label)))
        special_link_candidate_cnt = len(special_node_candidates)
        # choose special links from deleted links to reborn prohibited 
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
        # fill reborn turns and components with special nodes
        for f in range(sub_graph_cnt):
            for t in range(f+1, sub_graph_cnt):
                turn = (
                    special_node_candidates[f], node_label, special_node_candidates[t])
                reborn_turns.add(turn)
        for sp_n in special_node_candidates:
            comp = tg.subgraph(
                nx.node_connected_component(tg, sp_n)).copy()
            if has_special_node and comp.has_node(special_node_label):
                special_nodes_and_comps[special_node_label] = comp
                continue
            special_nodes_and_comps[sp_n] = comp
    return connected, reborn_turns, special_nodes_and_comps


def turn_prohibition(g=nx.Graph(), has_special_node=False, special_node_label=-1, choose_node=choose_node_default):
    if g.number_of_nodes() <= 1:
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
        # calculate may probibit turns
        may_prohib = set()
        adj_cnt = len(adjs)
        for f in range(adj_cnt):
            for t in range(f + 1, adj_cnt):
                turn = (adjs[f], node_chosen, adjs[t])
                may_prohib.add(turn)
        connective, reborn_turns, specials_components = check_connectivity(g, node_chosen, has_special_node, special_node_label)
        # if deleting the chosen node makes the 
        if not connective:
            may_prohib.difference_update(reborn_turns)
            print('remove turns : ')
            print(may_prohib)
            print('split into components : ')
            cmp_cnt = 0
            for spn, comp in specials_components.items():
                print('component numner ' + str(cmp_cnt) + ' : ')
                cmp_cnt += 1
                comp_prohib_turns = turn_prohibition(comp, has_special_node=True, special_node_label=spn, choose_node=choose_node)
                print('remove turns : ')
                print(may_prohib)
                may_prohib.update(comp_prohib_turns)
            turns_need_prohibit.update(may_prohib)
            break
        else:
            print('remove turns : ')
            print(may_prohib)
            turns_need_prohibit.update(may_prohib)
            g.remove_node(node_chosen)
    return turns_need_prohibit

if __name__ == "__main__":
    tg1 = gen_test_case2()
    tp = turn_prohibition(tg1, choose_node=choose_node_link_weight)
    print(tp)