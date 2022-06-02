import pandas as pd
import networkx as nx
from scipy.special import comb

corr_path = r'C:\Simbench_Data\1-LV-rural3--1-sw\2022 haushalt\pearson.xlsx'
incidence_path = r'C:\Simbench_Data\1-LV-rural3--1-sw\incidence matrix.xlsx'

corr_matrix = pd.read_excel(corr_path)
corr_matrix.drop('Unnamed: 0', inplace=True, axis=1)
corr_matrix = corr_matrix.set_index(corr_matrix.columns)
print(corr_matrix)

incidence_matrix = pd.read_excel(incidence_path)
incidence_matrix.drop('Unnamed: 0', inplace=True, axis=1)
incidence_matrix = incidence_matrix.set_index(incidence_matrix.columns)
print(incidence_matrix)

G = nx.Graph()
G.add_nodes_from(incidence_matrix.columns)

for start in range(len(corr_matrix)):
    for end in range(start+1, len(corr_matrix)):
        G.add_edge(corr_matrix.columns[start], corr_matrix.columns[end], weight=corr_matrix.iloc[start,start] - corr_matrix.iloc[start,end])
        G.add_edge(corr_matrix.columns[end], corr_matrix.columns[start], weight=corr_matrix.iloc[start,start] - corr_matrix.iloc[start,end])

mst_matrix = pd.DataFrame(index=incidence_matrix.index, columns=incidence_matrix.columns)
mst = nx.minimum_spanning_tree(G, algorithm='kruskal')
for edge in mst.edges(data=True):
    mst_matrix.loc[edge[0],edge[1]] = 1
    mst_matrix.loc[edge[1],edge[0]] = 1
mst_matrix = mst_matrix.fillna(0)

edges = sorted(mst.edges(data=True), key=lambda x:x[2]['weight'], reverse=True)
for edge in edges:
    print(edge)

mistake = 0
correct = 0
connection_combis = comb(len(corr_matrix), 2)
should_be_there = []
shouldnot_be_there = []

for i in range(len(corr_matrix)):
    for j in range(i+1, len(corr_matrix)):
        if incidence_matrix.iloc[i,j] != mst_matrix.iloc[i,j] and incidence_matrix.iloc[i,j] == 1:
            mistake += 1
            should_be_there.append((corr_matrix.columns[i],corr_matrix.columns[j]))
        elif incidence_matrix.iloc[i,j] != mst_matrix.iloc[i,j] and incidence_matrix.iloc[i,j] == 0:
            mistake += 1
            shouldnot_be_there.append((corr_matrix.columns[i],corr_matrix.columns[j]))
        else:
            correct += 1

print("\ntotal connection combinations: ", connection_combis)
print("correctness: ", correct)
print("mistakes: ", mistake)
print("Accuracy: ", correct/connection_combis)
print('connections should be there: ', should_be_there)
print('connections should not be there: ', shouldnot_be_there)