import numpy
import picos as pic
import networkx as nx


def mu_delta(num_nodes):
    mu = {}
    delta = {}
    for k in range(num_nodes):
        for j in range(num_nodes):
            if k != j:
                m = numpy.random.rand() * 10
                d = numpy.random.rand() * m
                mu[(k, j)] = m
                delta[(k, j)] = d
    return mu, delta


def build_graph(num_nodes):
    g = nx.DiGraph()
    for k in range(num_nodes):
        g.add_node(k)
        for j in range(num_nodes):
            if k != j:
                g.add_edge(k, j)
    return g


def nominal_model(num_nodes, g, mu):
    prob = pic.Problem()

    # add flow variables
    x = {}
    for e in g.edges():
        x[e] = pic.RealVariable('x[{0}]'.format(e))

    # add total flow variable
    v = pic.RealVariable('v')

    # add flow constraints
    prob.add_list_of_constraints([pic.sum([x[p, i] for p in g.nodes() if p != i]) ==
                                  pic.sum([x[i, j] for j in g.nodes() if j != i])
                                  for i in g.nodes() if i not in (0, num_nodes)])
    prob.add_constraint(pic.sum([x[j, num_nodes - 1]
                                 for j in g.nodes() if j != num_nodes - 1]) == 1)  # flows to last node
    prob.add_constraint(pic.sum([x[0, j]
                                 for j in g.nodes() if j != 0]) == 1)  # flows from first node

    # add capacity constraints
    prob.add_list_of_constraints([x[e] <= 0.5 for e in g.edges()])

    # add non-negativity constraints
    prob.add_list_of_constraints([x[e] >= 0 for e in g.edges()])

    # setting objective
    prob.add_constraint(v >= pic.sum([mu[e] * x[e] for e in g.edges()]))
    prob.set_objective('min', v)
    sol = prob.solve()
    time = sol.searchTime

    print('Nominal model: optimal total flow is', v, 'and run time is', time)
    return prob, x, v, time


if __name__ == '__main__':
    # Setting Parameters
    num_nodes = 10  # number of nodes
    Gamma = 1
    mu, delta = mu_delta(num_nodes)
    g = build_graph(num_nodes)  # generate the network

    # solve the nominal model
    prob, x, v, time = nominal_model(num_nodes, g, mu)
