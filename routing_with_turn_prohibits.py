import networkx as nx
from copy import deepcopy
import uuid

def gen_trans_test_case():
    fh = open("trans_test.edgelist", "rb")
    G = nx.read_edgelist(fh, nodetype=int, data=(("weight", float),))
    fh.close()
    return G

def gen_link_graph(g=nx.Graph(), prohibited_turns=set(), weight_label='weight') -> nx.MultiDiGraph:
    lkg = nx.MultiDiGraph()
    for n in g.nodes:
        adjs = sorted(list(nx.neighbors(g, n)))
        adj_cnt = len(adjs)
        for adi1 in range(adj_cnt):
            for adi2 in range(adi1 + 1, adj_cnt):
                ad1, ad2 = adjs[adi1], adjs[adi2]
                turn = (ad1, n, ad2)
                if turn in prohibited_turns:
                    continue
                s1ton, snto1, s2ton, snto2 = '{}_{}'.format(ad1, n), '{}_{}'.format(n, ad1), '{}_{}'.format(ad2, n), '{}_{}'.format(n, ad2)
                w1n, w2n = g[n][ad1][weight_label], g[n][ad2][weight_label]
                lkg.add_edge(s1ton, snto2, weight=w2n)
                lkg.add_edge(s2ton, snto1, weight=w1n)

    return lkg

def routing_with_tp(g=nx.Graph(), prohibited_turns=set(), src=-1, dst=-1, weight_label='weight'):
    # first check if src and dst are neighbours
    if g.has_edge(src, dst):
        return [src, dst]
    # or we need to do the routing
    g = deepcopy(g)
    src_ad, dst_ad = uuid.uuid1().int, uuid.uuid1().int
    g.add_edge(src_ad, src)
    g[src_ad][src].update({weight_label:0})
    g.add_edge(dst, dst_ad)
    g[dst][dst_ad].update({weight_label:0})
    g.add_edge(src, src_ad)
    g[src][src_ad].update({weight_label:0})
    g.add_edge(dst_ad, dst)
    g[dst_ad][dst].update({weight_label:0})
    lkg = gen_link_graph(g, prohibited_turns, weight_label)
    sou, tar = '{}_{}'.format(src_ad, src), '{}_{}'.format(dst, dst_ad)
    sp = nx.shortest_path(lkg,source=sou,target=tar, weight=weight_label)
    splen = len(sp)
    routing_path = list()
    for i in range(splen - 1):
        passing = int(sp[i].split('_')[1]) 
        routing_path.append(passing)
    return routing_path



if __name__ == "__main__":
    tg = gen_trans_test_case()
    ttg = routing_with_tp(tg, set([(1,3,4)]), 1, 4)
    print(ttg)
