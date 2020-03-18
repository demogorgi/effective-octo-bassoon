# -*- coding: utf-8 -*-

# this file contains initial values for physics
# it has to be generated from state_sim.xml automatically later

import gurobipy as gp
from gurobipy import GRB

# Pressure old_old and pressure old in bar
nodes, var_node_p_old_old, var_node_p_old = gp.multidict({
    "EN_auxMin": [41.173249999999996,                    41.173249999999996],
    "EN_auxMax": [41.01325,                              41.01325],
    "EH_auxMin": [88.66025,                              88.66025],
    "EH_auxMax": [41.01325,                              41.01325],
    "XH": [88.44325,                                     88.44325],
    "XN": [39.79725,                                     39.79725],
    "N22": [40.935249999999996,                          40.935249999999996],
    "N23": [71.01325,                                    71.01325],
    "N25": [88.38825,                                    88.38825],
    "N18": [88.50225,                                    88.50225],
    "N19": [88.44325,                                    88.44325],
    "N20": [88.44325,                                    88.44325],
    "N12": [40.935249999999996,                          40.935249999999996],
    "N11": [41.03525,                                    41.03525],
    "N17": [88.56425,                                    88.56425],
    "N26": [40.95425,                                    40.95425],
    "N14": [40.32025,                                    40.32025],
    "N13": [40.82425,                                    40.82425],
    "N23_1": [88.50225,                                  88.50225],
    "EN": [41.12825,                                     41.12825],
    "EN_aux1": [41.173249999999996,                      41.173249999999996],
    "EN_aux2": [41.173249999999996,                      41.173249999999996],
    "EN_aux3": [41.173249999999996,                      41.173249999999996],
    "EH": [88.62825,                                     88.62825],
    "EH_aux1": [88.66025,                                88.66025],
    "EH_aux2": [88.66025,                                88.66025],
    "EH_aux3": [88.66025,                                88.66025],
    "N26_aux": [40.95425,                                40.95425],
    "N22_aux": [40.935249999999996,                      40.935249999999996],
    "N23_aux": [71.01325,                                71.01325]
})
                                                     
# Flow old_old and flow old of non-pipes in 1000 m³/h
non_pipes, var_non_pipe_Qo_old_old, var_non_pipe_Qo_old = gp.multidict({
    ("N22", "N23"): [0.0,                                  0.0],
    ("N25", "N26_aux"): [198.592,                          198.592],
    ("EN_auxMin", "EN_aux1"): [100.0,                      100.0],
    ("EN_auxMax", "EN_aux3"): [0.0,                        0.0],
    ("EH_auxMin", "EH_aux1"): [250.0,                      250.0],
    ("EH_auxMax", "EH_aux3"): [0.0,                        0.0],
    ("N26_aux", "N26"): [198.592,                          198.592],
    ("N22_aux", "N23_aux"): [0.0,                          0.0],
    ("N23", "N23_1"): [0.0,                                0.0]
})
                                                     
# Flow old_old and flow old for pipes (in and out) in 1000 m³/h
pipes, var_pipe_Qo_in_old_old, var_pipe_Qo_in_old, var_pipe_Qo_out_old_old, var_pipe_Qo_out_old = gp.multidict({
    ("N20", "XH"): [1.3789264103814909,                    1.3789264103814909,     1.3789264103814909,           1.3789264103814909],
    ("N12", "N22"): [-2.480096505841499,                   -2.480096505841499,     -2.480096505841499,           -2.480096505841499],
    ("N23_1", "N18"): [-1.38,                              -1.38,                  -1.38,                        -1.38],
    ("EH", "N17"): [216.52552480855354,                    216.52552480855354,     216.52552480855354,           216.52552480855354],
    ("N17", "N18"): [213.76369965976062,                   213.76369965976062,     213.76369965976062,           213.76369965976062],
    ("N18", "N19"): [208.24359538440717,                   208.24359538440717,     208.24359538440717,           208.24359538440717],
    ("N19", "N20"): [4.136849853877266,                    4.136849853877266,      4.136849853877266,            4.136849853877266],
    ("N11", "N12"): [175.31332285885182,                   175.31332285885182,     175.31332285885182,           175.31332285885182],
    ("EN", "N11"): [170.01764919958816,                    170.01764919958816,     170.01764919958816,           170.01764919958816],
    ("N19", "N25"): [199.9702438058299,                    199.9702438058299,      199.9702438058299,            199.9702438058299],
    ("N14", "XN"): [397.76470636997846,                    397.76470636997846,     397.76470636997846,           397.76470636997846],
    ("N26", "N13"): [200.92810271666386,                   200.92810271666386,     200.92810271666386,           200.92810271666386],
    ("N13", "N14"): [393.2307461269968,                    393.2307461269968,      393.2307461269968,            393.2307461269968],
    ("N12", "N13"): [185.25299952884447,                   185.25299952884447,     185.25299952884447,           185.25299952884447],
    ("EN_aux1", "EN"): [165.8560288388066,                 165.8560288388066,      165.8560288388066,            165.8560288388066],
    ("EN_aux2", "EN_aux1"): [48.32033175393595,            48.32033175393595,      48.32033175393595,            48.32033175393595],
    ("EN_aux3", "EN_aux2"): [16.107,                       16.107,                 16.107,                       16.107],
    ("EH_aux1", "EH"): [218.59794729347533,                218.59794729347533,     218.59794729347533,           218.59794729347533],
    ("EH_aux2", "EH_aux1"): [-23.033276607324822,          -23.033276607324822,    -23.033276607324822,          -23.033276607324822],
    ("EH_aux3", "EH_aux2"): [-7.678,                       -7.678,                 -7.678,                       -7.678],
    ("N22", "N22_aux"): [0.0,                              0.0,                    0.0,                          0.0],
    ("N23_aux", "N23"): [0.0,                              0.0,                    0.0,                          0.0]
})
