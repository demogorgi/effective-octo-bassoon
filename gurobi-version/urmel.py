#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# this file contains the simulator_step-method to perform a single simulator step

import importlib
import sys
from os import path
import re
import glob
import os
import gurobipy as gp
from gurobipy import GRB
from constants import *
from functions import *
from model import *
import yaml

output = path.join(sys.argv[1],'output')
if not os.path.exists(output):
    os.makedirs(output)
else:
    files = glob.glob(path.join(output,"*"))
    for f in files:
        os.remove(f)

def simulator_step(config, agent_decisions, compressors, step, dt):
    # m ist the simulator model with agent decisisons, compressor specs and timestep length incorporated
    m = simulate(agent_decisions, compressors, dt)
    # optimize the model ( = do a simulation step)
    m.optimize()
    # get the model status
    status = m.status
    # if solved to optimallity
    if status == 2:
        if config['write_lp']: m.write(output + "/" + config['name'] + "_" + str(step).rjust(5, '0') + ".lp")
        if config['write_sol']: m.write(output + "/" + config['name'] + "_" + str(step).rjust(5, '0') + ".sol")
        # store solution in dictionary
        sol = {}
        for v in m.getVars():
            sol[v.varName] = v.x
            #print('%s %g' % (v.varName, v.x))
        #print(sol)
        # set old to old_old and current value to old for flows and pressures
        for node in no.nodes:
            sc.var_node_p_old_old[node], sc.var_node_p_old[node]
            sc.var_node_p_old[node], sol["var_node_p[%s]" % node]
        for non_pipe in co.non_pipes:
            sc.var_non_pipe_Qo_old_old[non_pipe] = sc.var_non_pipe_Qo_old[non_pipe]
            sc.var_non_pipe_Qo_old[non_pipe] = sol["var_non_pipe_Qo[%s,%s]" % non_pipe]
        for pipe in co.pipes:
            sc.var_pipe_Qo_in_old_old[pipe] = sc.var_pipe_Qo_in_old[pipe]
            sc.var_pipe_Qo_in_old[pipe] = sol["var_pipe_Qo_in[%s,%s]" % pipe]
            sc.var_pipe_Qo_out_old_old[pipe] = sc.var_pipe_Qo_out_old[pipe]
            sc.var_pipe_Qo_out_old[pipe] = sol["var_pipe_Qo_out[%s,%s]" % pipe]
        return sol
    # if infeasible write IIS for analysis and debugging
    elif status == 3 and config['write_ilp']:
        print("Model is infeasible. %s.ilp written." % config['name'])
        m.computeIIS()
        m.write(output + "/" + config['name'] + "_" + str(step).rjust(5, '0') + ".ilp")
    # don't know yet, what else
    else:
        print("Solution status is %d, don't know what to do." % status)
