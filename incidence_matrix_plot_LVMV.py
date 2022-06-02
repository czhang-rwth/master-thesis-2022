import numpy as np
import pandas as pd
import networkx as nx
import simbench as sb
import matplotlib.pyplot as plt
import pandapower.plotting as ppplot

def incidence_matrix_topology(simbench_net, file_path_matrix, file_path_topology):
    # DON'T change the zorder! That's important! DON'T CHANGE ZORDER!!!!!!
    # but you can change the size for different net topology plot

    # import simbench net
    net = sb.get_simbench_net(simbench_net)

    # create incidence matrix
    # create the numpy array for all connections
    from_bus = np.array(net.line.from_bus).reshape(-1,1)
    to_bus = np.array(net.line.to_bus).reshape(-1,1)
    connections = np.hstack((from_bus, to_bus))

    # the incidence matrix should look like this
    trafo_bus = net.trafo.hv_bus
    main_bus = net.bus.drop(trafo_bus, axis=0).index # inplace = False
    incidence_matrix = pd.DataFrame(columns=main_bus, index=main_bus)

    for i in connections:
        incidence_matrix[i[0]][i[1]] = 1
        incidence_matrix[i[1]][i[0]] = 1

    incidence_matrix = incidence_matrix.fillna(0)
    incidence_matrix.to_excel(file_path_matrix)

    # create topology
    # empty all geodata for better plotting, the plotting with geodata is too chaotic
    net.bus_geodata.drop(net.bus_geodata.index, inplace=True)
    net.line_geodata.drop(net.line_geodata.index, inplace=True)
    ppplot.create_generic_coordinates(net, respect_switches=False) # create the best coordinates for buses # whether you wanna no cycle
    x = np.array(net.bus_geodata.x).reshape(-1, 1)
    y = np.array(net.bus_geodata.y).reshape(-1, 1)
    coordinates = np.hstack((x, y))

    main_bus_collection = ppplot.create_bus_collection(net, buses=main_bus, color='skyblue', size=.05, zorder=3) #zorder: the larger, the later plotted
    trafo_bus_collection = ppplot.create_bus_collection(net, buses=trafo_bus, color='yellow', size=.05, zorder=3)
    line_collection = ppplot.create_line_collection(net, color='grey', use_bus_geodata=True, linewidth=.45) #use_bus_geodata is automatically set to True, since net.line_geodata is empty.
    trafo_collection = ppplot.create_trafo_collection(net, color='green')

    ppplot.draw_collections([main_bus_collection, trafo_bus_collection, line_collection, trafo_collection])

    G = nx.Graph()
    G.add_nodes_from(net.bus.index)

    node_coordinates = dict(zip(net.bus.index, coordinates))
    node_labels = dict(zip(net.bus.index, net.bus.index))

    nx.draw_networkx_labels(G, node_coordinates, node_labels, font_size=5.5) #default font size = 12
    plt.savefig(file_path_topology, dpi=500)

    return None

net_code = '1-MV-urban--2-sw'
incidence_matrix_topology(simbench_net = net_code, file_path_matrix=r'C:\Simbench_Data\\' + net_code + r'\incidence matrix.xlsx', file_path_topology=r'C:\Simbench_Data\\' + net_code + r'\topology.png')