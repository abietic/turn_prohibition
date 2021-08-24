import networkx as nx
from copy import deepcopy
import random

from networkx.utils.decorators import open_file
from flow_gen import gen_flow
from turn_prohibition import turn_prohibition
from routing_with_turn_prohibits import routing_with_tp

def gen_lb_test_case(bandwidth=10000.0):
    fh = open("test.edgelist", "rb")
    G = nx.read_edgelist(fh, nodetype=int)
    fh.close()
    for (u, v) in G.edges:
        G[u][v]['bandwidth'] = bandwidth
        G[u][v]['used'] = 0.0
        G[u][v]['rate'] = 1.0
    return G.to_directed()

def lb_solve(g=nx.MultiDiGraph()):
    g = deepcopy(g)
    for_tp = g.to_undirected()
    prohibited_turns = turn_prohibition(for_tp)
    target_gen_flow_cnt = g.number_of_edges() * 400
    print(target_gen_flow_cnt)
    allocated_flow = list()
    for f in gen_flow(g, target_gen_flow_cnt, degree_req= lambda g,s,d:g.degree[s]==2 and g.degree[d]==2):
        # rp = routing_with_tp(g, prohibited_turns, f.src, f.dst, weight_label='rate')
        # can_alloc = True
        # pmem = list()
        # for i in range(len(rp) - 1):
        #     p = 's_' + str(rp[i]) +'->'+ str(rp[i+1])
        #     # 不对，要改
        #     if g[rp[i]][rp[i+1]]['bandwidth'] - f.bandwidth - g[rp[i]][rp[i+1]]['used'] < 0.0:
        #         can_alloc = False
        #         break
        #     pmem.append(p)
        can_alloc = False
        if not can_alloc:
            # if running with turn prohibition is not schedulable any more,
            # try activate prohibited resources
            rp = nx.shortest_path(g, f.src, f.dst, weight='rate')
            can_alloc = True
            pmem = list()
            for i in range(len(rp) - 1):
                p = 's_' + str(rp[i]) +'->'+ str(rp[i+1])
                # 不对，要改
                if g[rp[i]][rp[i+1]]['bandwidth'] - f.bandwidth - g[rp[i]][rp[i+1]]['used'] < 0.0:
                    can_alloc = False
                    break
                pmem.append(p)
        if can_alloc:
            for i in range(len(rp) - 1):
                g[rp[i]][rp[i+1]]['used'] += f.bandwidth
                g[rp[i]][rp[i+1]]['rate'] = 1.0 + g[rp[i]][rp[i+1]]['used'] / g[rp[i]][rp[i+1]]['bandwidth']
            f.allocated_path = pmem
            allocated_flow.append(f)
        else:
            break
    return allocated_flow


if __name__ == "__main__":
    tg = gen_lb_test_case()
    ret = lb_solve(tg)
    print(len(ret))
    of = open("lb.flowlist", "w")
    of.write(str(len(ret))+'\n')
    for f in ret:
        of.write('{}\n{}\n{}\n{}\n'.format(len(f.allocated_path), f.period, f.size, f.bandwidth))
        for p in f.allocated_path:
            of.write(p+'\n')

