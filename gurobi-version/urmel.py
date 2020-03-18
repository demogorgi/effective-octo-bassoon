#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# this file manages the iterative process
# it works for example with python3, gurobi 8.0.1, yaml 5.3
# >python3 urmel.py (or ./urmel.py)

from constants import *
from functions import *
from init_scenario import *
import gurobipy as gp
from gurobipy import GRB
from network.nodes import *
from network.connections import *
from model import *
import yaml

# manual file with compressor data is read
# the dictionary does not change during the process
with open(r'input_data/compressors.yml') as file:
    compressors = yaml.load(file, Loader=yaml.FullLoader)
    #print(compressors)

# manual file with initial gas network control is read
# the dictionary changes with every new control
with open(r'input_data/init_decisions.yml') as file:
    agent_decisions = yaml.load(file, Loader=yaml.FullLoader)
    #print(agent_decisions)
    
name = "urmel"
m = simulator_model(name + ".py",agent_decisions)
m.optimize()
m.write(name + ".lp")

print("-------------------------------------")
print(m.getVarByName("va_DA[N23,N23_1]"))
print("-------------------------------------")
print(m.getAttr('VarName', m.getVars()))
print("-------------------------------------")

if m.status == 3:
    print("Model is infeasible. %s.ilp written." % name)
    m.computeIIS()
    m.write(name + ".ilp")
