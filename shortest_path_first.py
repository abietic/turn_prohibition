import networkx as nx
from copy import deepcopy
import random
from flow_gen import gen_flow


def gen_spf_test_case(bandwidth=10000.0):
    fh = open("test.edgelist", "rb")
    G = nx.read_edgelist(fh, nodetype=int)
    fh.close()
    for (u, v) in G.edges:
        G[u][v]['bandwidth'] = bandwidth
    return G.to_directed()


def spf_solve(g=nx.MultiDiGraph()):
    g = deepcopy(g)
    sp = nx.shortest_path(g, weight='delay')
    target_gen_flow_cnt = g.number_of_edges() * 400
    print(target_gen_flow_cnt)
    allocated_flow = list()
    for f in gen_flow(g, target_gen_flow_cnt, degree_req= lambda g,s,d:g.degree[s]==2 and g.degree[d]==2):
        rp = sp[f.src][f.dst]
        can_alloc = True
        pmem = list()
        for i in range(len(rp) - 1):
            p = 's_' + str(rp[i]) +'->'+ str(rp[i+1])
            if g[rp[i]][rp[i+1]]['bandwidth'] - f.bandwidth < 0.0:
                can_alloc = False
                break
            pmem.append(p)
        if can_alloc:
            f.allocated_path = pmem
            allocated_flow.append(f)
            for i in range(len(rp) - 1):
                g[rp[i]][rp[i+1]]['bandwidth'] -= f.bandwidth
        else:
            break
    return allocated_flow


if __name__ == "__main__":
    tg = gen_spf_test_case()
    ret = spf_solve(tg)
    print(len(ret))
    of = open("spf.flowlist", "w")
    of.write(str(len(ret))+'\n')
    for f in ret:
        of.write('{}\n{}\n{}\n{}\n'.format(len(f.allocated_path), f.period, f.size, f.bandwidth))
        for p in f.allocated_path:
            of.write(p+'\n')
    of.flush()
    of.close()