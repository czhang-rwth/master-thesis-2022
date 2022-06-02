import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

data_path = r'C:\Simbench_Data\1-LV-rural3--1-sw\2022 haushalt'
incidence_path = r'C:\Simbench_Data\1-LV-rural3--1-sw\incidence matrix.xlsx'

# read the voltage data
voltage = pd.read_excel(data_path + r'\res_bus\vm_pu.xlsx')
voltage.drop('Unnamed: 0', inplace=True, axis=1)
to_remove = []
for column in voltage.columns:
    if voltage[column].nunique() == 1:
        to_remove.append(column)

for column in to_remove:
    voltage.drop(column, inplace=True, axis=1)

print(voltage)

# read the incidence matrix
incidence_matrix = pd.read_excel(incidence_path)
incidence_matrix.drop('Unnamed: 0', inplace=True, axis=1)
incidence_matrix = incidence_matrix.set_index(voltage.columns)
print(incidence_matrix)

# create the correlation matrix of the voltage dataframe and export as excel
def correlation_full_timelength_toExcel(method): #method: pearson, kendall, spearman
    global voltage
    global data_path

    corr_matrix = voltage.corr(method)
    corr_matrix.to_excel(data_path + r'\\' + method + '.xlsx')

    return None

# create the correlation matrix depending on different time lengths
def correlation(method, timelength): #method: pearson, kendall, spearman
    global voltage
    corr_matrix  = voltage[:][:timelength].corr(method)

    return corr_matrix

# create incidence matrix based on estimation
def estimated_incidence_matrix(corr_matrix): # corr_matrix is Dataframe
    global voltage

    G = nx.Graph()
    G.add_nodes_from(voltage.columns)

    for start in range(len(corr_matrix)):
        for end in range(start + 1, len(corr_matrix)):
            G.add_edge(voltage.columns[start], voltage.columns[end], weight=corr_matrix.iloc[start, start] - corr_matrix.iloc[start, end])
            G.add_edge(voltage.columns[end], voltage.columns[start], weight=corr_matrix.iloc[start, start] - corr_matrix.iloc[start, end])

    mst_matrix = pd.DataFrame(index=voltage.columns, columns=voltage.columns)
    mst = nx.minimum_spanning_tree(G, algorithm='kruskal')
    for edge in mst.edges(data=True):
        mst_matrix.loc[edge[0], edge[1]] = 1
        mst_matrix.loc[edge[1], edge[0]] = 1
    mst_matrix = mst_matrix.fillna(0)

    return mst_matrix

# compare the estimation incidence matrix with the real incidence matrix based on Days
def comparison_based_on_Day(method): #method: pearson, kendall, spearman
    global data_path
    global voltage
    global incidence_matrix

    reality = incidence_matrix # Dataframe
    one_day = int(len(voltage.index)/365) # 35040 / 365 = 96
    mistakes = []

    for t in range(one_day, len(voltage.index) + 1, one_day):
        corr_matrix = correlation(method, t) # Dataframe
        estimation = estimated_incidence_matrix(corr_matrix) # Dataframe

        mistake = 0
        for i in range(len(estimation)):
            for j in range(i + 1, len(estimation)):
                if reality.iloc[i,j] != estimation.iloc[i,j]:
                    mistake += 1
        mistakes.append(mistake)
        print(len(mistakes), mistake, t)

    plt.figure(figsize=(8,8))
    plt.title('Number of estimation mistakes dependent on observation days and ' + method + ' correlation')
    plt.xlabel('number of days')
    plt.ylabel('estimation mistakes')
    plt.plot(range(1,len(mistakes)+1), mistakes)
    plt.savefig(data_path + '\estimation mistakes days ' + method +'.png', dpi=500)

    return None

# compare the estimation incidence matrix with the real incidence matrix based on time points within littel Days
def comparison_within_lttle_days(method, num_days): #method: pearson, kendall, spearman
    global data_path
    global voltage
    global incidence_matrix

    reality = incidence_matrix  # Dataframe
    one_day = int(len(voltage.index) / 365)  # 35040 / 365 = 96
    mistakes = []

    for t in range(2, num_days*one_day+1):
        corr_matrix = correlation(method, t) # Dataframe
        estimation = estimated_incidence_matrix(corr_matrix) # Dataframe

        mistake = 0
        for i in range(len(estimation)):
            for j in range(i + 1, len(estimation)):
                if reality.iloc[i, j] != estimation.iloc[i, j]:
                    mistake += 1
        mistakes.append(mistake)
        print(num_days*one_day, t, mistake)

    plt.figure(figsize=(8, 8))
    plt.title('Number of estimation mistakes dependent on time points and ' + method + ' correlation, ' + str(num_days) + ' days')
    plt.xlabel('number of time points')
    plt.ylabel('estimation mistakes')
    plt.plot(range(2, num_days*one_day+1), mistakes)#, s=2)
    plt.savefig(data_path + r'\estimation mistakes ' + str(num_days) + ' days ' + method + '.png', dpi=300)

    return None

def comparison_within_lttle_days_allMethods(num_days):
    global data_path
    global voltage
    global incidence_matrix

    reality = incidence_matrix # Dataframe
    one_day = int(len(voltage.index) / 365) # 35040 / 365 = 96
    mistakes_pearson = []
    mistakes_spearman = []
    mistakes_kendall = []

    for t in range(2, num_days * one_day+1):
        corr_matrix_pearson = correlation('pearson', t)
        estimation_pearson = estimated_incidence_matrix(corr_matrix_pearson)
        corr_matrix_spearman = correlation('spearman', t)
        estimation_spearman = estimated_incidence_matrix(corr_matrix_spearman)
        corr_matrix_kendall = correlation('kendall', t)
        estimation_kendall = estimated_incidence_matrix(corr_matrix_kendall)

        mistake_pearson = 0
        mistake_spearman = 0
        mistake_kendall = 0

        for i in range(len(estimation_pearson)):
            for j in range(i + 1, len(estimation_pearson)):
                if reality.iloc[i,j] != estimation_pearson.iloc[i,j]:
                    mistake_pearson += 1
                if reality.iloc[i,j] != estimation_spearman.iloc[i,j]:
                    mistake_spearman += 1
                if reality.iloc[i,j] != estimation_kendall.iloc[i,j]:
                    mistake_kendall += 1
        mistakes_pearson.append(mistake_pearson)
        mistakes_spearman.append(mistake_spearman)
        mistakes_kendall.append(mistake_kendall)
        print(num_days * one_day, t, mistake_pearson, mistake_spearman, mistake_kendall)

    plt.figure(figsize=(9, 9))
    plt.title('Number of estimation mistakes dependent on time points and all correlation methods, ' + str(num_days) + ' days')
    plt.xlabel('number of time points')
    plt.ylabel('estimation mistakes')
    plt.plot(range(2, num_days * one_day + 1), mistakes_pearson, label='pearson')  # , s=2)
    plt.plot(range(2, num_days * one_day + 1), mistakes_spearman, label='spearman')
    plt.plot(range(2, num_days * one_day + 1), mistakes_kendall, label='kendall')
    plt.legend()
    plt.savefig(data_path + r'\estimation mistakes ' + str(num_days) + ' days ' + 'all corr methods.png', dpi=300)

    return None

# which functions do you want to realize?
correlation_full_timelength_toExcel('pearson')
comparison_based_on_Day('pearson')
comparison_within_lttle_days('pearson', 5)
comparison_within_lttle_days_allMethods(5)