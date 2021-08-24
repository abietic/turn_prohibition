import networkx as nx
from copy import deepcopy
import random
from flow_info import flow_info

def gen_flow(g=nx.Graph(), num=1000, size_range=(0.025,0.095), period_range=(0.0025,0.0095), deadline_range = None, degree_req=None):
    total_gen = 0
    nodes = list(g.nodes)
    while total_gen < num:
        choice = random.sample(nodes, 2)
        src, dst = choice[0], choice[1]
        if degree_req is not None:
            if not degree_req(g, src, dst):
                # print('src:{}, dst:{}'.format(g.degree[src], g.degree[dst]))
                continue
        # gen period
        period = random.uniform(period_range[0],period_range[1])
        # gen packet size
        size = random.uniform(size_range[0],size_range[1])
        # cal bandwidth
        bandwidth = size / period
        deadline = period
        if deadline_range is not None:
            deadline = random.uniform(deadline_range[0], deadline_range[1])
        yield flow_info(src, dst, period, size, bandwidth, deadline)
        total_gen += 1
