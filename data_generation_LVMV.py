import pickle
import random
import pandas as pd
import numpy as np
import simbench as sb
import pandapower.control as control
import pandapower.timeseries as timeseries
from pandapower.timeseries.data_sources.frame_data import DFData

def create_net(filepath, profiles_filepath):
    net_codes = ['1-LV-rural1--1-sw',
                 '1-LV-rural2--1-sw',
                 '1-LV-rural3--1-sw',
                 '1-LV-semiurb4--1-sw',
                 '1-LV-semiurb5--1-sw',
                 '1-LV-urban6--1-sw']#,
                 #'1-MV-rural--0-sw',
                 #'1-MV-semiurb--0-sw',
                 #'1-MV-urban--0-sw',
                 #'1-MV-comm--0-sw']

    unused_timeseries = list(range(2000))

    with open(profiles_filepath, 'rb') as f:
        pickle_data = pickle.load(f)

    for code in net_codes:
        net = sb.get_simbench_net(code)
        n_loads = net.load.shape[0]
        n_sgen = net.sgen.shape[0]

        load_p = pd.DataFrame()
        num_ts = random.sample(unused_timeseries, n_loads)
        #tech = ['E-Mob', 'Wärmepumpe', 'Klimaanlage']
        for i in num_ts:
            a = np.reshape([x * 0.001 for x in pickle_data["2022"][i]["Haushalt"]], (-1,1))
            #tech_num = random.randint(0, 3)
            #tech_random = random.sample(tech, tech_num)
            #for j in tech_random:
            #    a += np.reshape([x * 0.001 for x in pickle_data["2022"][i][j]], (-1,1))
            a = pd.DataFrame(a)
            load_p = pd.concat([load_p, a], axis=1)
            unused_timeseries.remove(i)
        load_p = load_p.set_axis([str(x) for x in range(n_loads)], axis=1)
        print(load_p, '\n')

        sgen_p = pd.DataFrame()
        num_ts = random.sample(unused_timeseries, n_sgen)
        for i in num_ts:
            a = pd.DataFrame([x * 0.001 for x in pickle_data["2022"][i]["PV"].reshape(-1, 1)])
            sgen_p = pd.concat([sgen_p, a], axis=1)
            unused_timeseries.remove(i)
        sgen_p = sgen_p.set_axis([str(x) for x in range(n_sgen)], axis=1)
        print(sgen_p, '\n')

        # Use constControl to write the time data to the calculation
        ds = DFData(sgen_p)
        const_sgen = control.ConstControl(net, element='sgen', element_index=net.sgen.index, variable='p_mw', data_source=ds, profile_name=sgen_p.columns)
        ds = DFData(load_p)
        const_load = control.ConstControl(net, element='load', element_index=net.load.index, variable='p_mw', data_source=ds, profile_name=load_p.columns)

        ow = timeseries.OutputWriter(net, output_path=filepath + code + r'\2022 haushalt', output_file_type='.xlsx')
        ow.log_variable('res_bus', 'vm_pu')
        ow.log_variable('res_bus', 'p_mw')
        # ow.log_variable('res_bus', 'va_degree')
        timeseries.run_timeseries(net, time_steps=None)

path = r'C:\Users\c.zhang\Downloads\loads_dictionary.pkl'
create_net(filepath=r'C:\Simbench_Data\\', profiles_filepath=path)