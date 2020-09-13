import importlib
import sys
import re
import numpy as np
import random

from urmel import *

from .utils import *
from .configs import penalties, c_values, win_ratios

args = dotdict({
    #Weights to calculate penalty for both agents
    'pressure_wt_factor': 1,
    's_flow_wt_factor': 0.1,
    'x_flow_wt_factor': 0.05,
    #Upper and lower limit for generating a drag factor value for RE
    'zeta_ub': 1200,
    'zeta_lb': 100,
    #Upper and lower limit for gas
    'gas_ub': 1,
    'gas_lb': 0,
    #Number to control uniform distribution in decision size
    'decision_size': 100,
    #Threshold accumulated c values
    'max_da_c': 1000,
})

wd = sys.argv[1].replace("/",".")
wd = re.sub(r'\.$', '', wd)

no = importlib.import_module(wd + ".nodes") #Nodes of the network(entry + exit +inner nodes)
co = importlib.import_module(wd + ".connections") #Connections of the network

special_pipes = []
for i in co.special:
    special_pipes.append(re.sub("\('(\S*)',\s'(\S*)'\)", r'\1,\2', str(i)))

original_nodes = []
for n in no.nodes:
    if '_aux' not in n:
        if '_HD' not in n:
            if '_ND' not in n:
                original_nodes.append(n)

entry_q_ub = no.q_ub['EH']
pr,dispatcher_dec, trader_nom, state_, smoothed_flow = ({} for i in range(5))

def get_nom_q_diff(solution):
    nom_q_diff = {}

    for k, v in solution.items():
        if re.search('nom_entry_slack_DA', k):
            res = re.sub('nom_entry_slack_DA\[(\S*)]', r'\1', k)
            if res == 'EN_aux0,EN' or res == 'EH_aux0,EH':
                nom_q_diff[k] = v

    nom_q_diff_EH, nom_q_diff_EN = [v for k,v in nom_q_diff.items()]

    return nom_q_diff_EH, nom_q_diff_EN

def get_c(decision, num_steps, start_step):
    accumulated_cs = {}
    c_EH, c_EN, c_eh, c_en = [0 for _ in range(4)]
    for i in range(num_steps):
        if start_step+i < numSteps:
            solution = simulator_step(decision, start_step+i, "ai")
            c_EH, c_EN = get_nom_q_diff(solution)
            c_eh += c_EH
            c_en += c_EN
            accumulated_cs[i] = [c_eh, c_en]

    return accumulated_cs

def get_agents_dict(step, agent_decisions):
    agents_dict = {}
    for k1,v1 in agent_decisions.items():
        for k2, v2 in v1.items():
            for k3, v3 in v2.items():
                if re.search('(exit|entry)_nom', k1):
                    key = k1+"_TA["+k3+"]"
                else:
                    key = k1+"_DA["+k3+"]"
                for i in range(step,-1,-1):
                    if i in v3:
                        break
                agents_dict[key] = v3[i]

    return agents_dict

def get_boundary_q_p(solution):
    #smoothed_flow
    x_p = {}
    for k, v in solution.items():
        if re.search('smoothed_special_pipe_flow_DA', k):
            smoothed_flow[k] = v
        if re.search('var_node_p\[(XN|XH)]', k):
            res = re.sub('var_node_p\[(\S*)]', r'\1', k)
            x_p[res] = v
    pressures = normalize_pressure(x_p.copy())
    smoothed_flows = normalize_smoothed_flows(smoothed_flow.copy())
    boundary_p_q = {**smoothed_flows, **pressures}
    return boundary_p_q

def get_smoothed_flow(solution):
    smoothed_flow = {}
    for k, v in solution.items():
        if re.search('smoothed_special_pipe_flow_DA', k):
            smoothed_flow[k] = v
    return smoothed_flow

def normalize_smoothed_flows(smoothed_flow):
    for label, value in smoothed_flow.items():
        if 'EH' in label:
            smoothed_flow[label] = round((value - no.q_lb['EH'])/(no.q_ub['EH'] - no.q_lb['EH']),2)
        if 'EN' in label:
            smoothed_flow[label] = round((value - no.q_lb['EN'])/(no.q_ub['EN'] - no.q_lb['EN']),2)
    return smoothed_flow

def get_state(step, agent_decisions, solution):
    global trader_nom, dispatcher_dec
    pr_q = get_boundary_q_p(solution)

    agents_dict = get_agents_dict(step,agent_decisions)
    trader_nom = {k:v for k, v in agents_dict.items() if re.search('_TA',k)}
    dispatcher_dec = {k:v for k, v in agents_dict.items() if re.search('_DA',k)}

    da_dec = normalize_dispatcher_dec(dispatcher_dec.copy())
    ta_dec = normalize_trader_noms(trader_nom.copy())


    for k, v in da_dec.items(): #Dispatcher decision
        state_[k] = v
    for k, v in ta_dec.items(): #Trader decision
        state_[k] = v
    for k,v in pr_q.items():
        state_[k] = v

    state = np.array([value for key, value in state_.items()])
    return state

def get_trader_nom(step, agent_decisions):
    dec_dict = get_agents_dict(step,agent_decisions)
    trader_noms = {k:v for k, v in dec_dict.items() if re.search('_TA',k)}
    return trader_noms.copy()

def get_dispatcher_dec():
    return dispatcher_dec.copy()

def set_dispatcher_dec(da_dec):
    global dispatcher_dec
    dispatcher_dec = da_dec

def get_old_action():
    old_action = list(v for k, v in get_dispatcher_dec().items())
    return old_action


def normalize_dispatcher_dec(decisions):
    for label, value in decisions.items():
        if re.search('zeta_DA', label):
            decisions[label] = value/10000
    return decisions

def normalize_pressure(pressure_dict):
    for label, value in pressure_dict.items():
        pressure_dict[label] = round((value - no.pressure_limits_lower[label])/(no.pressure_limits_upper[label] - no.pressure_limits_lower[label]),2)
    return pressure_dict

def normalize_trader_noms(decisions):
    norm = lambda value, lb, ub: (value - lb)/(ub - lb)
    for label, value in decisions.items():
        key = re.sub('nom\S*_TA\[(\S*)]', r'\1', label)
        if re.search('XH', key):
            decisions[label] = norm(value, no.q_lb['XH'], no.q_ub['XH'])
        elif re.search('XN', key):
            decisions[label] = norm(value, no.q_lb['XN'], no.q_ub['XN'])
        elif re.search('EH', key):
            decisions[label] = norm(value, no.q_lb['EH'], no.q_ub['EH'])
        elif re.search('EN', key):
            decisions[label] = norm(value, no.q_lb['EN'], no.q_ub['EN'])
    return decisions

def find_penalty(solution):

    pr_violations = 0 #Dispatcher pressure bound violations
    entry_flow_violations  = 0 #Dispatcher flow bound violations
    exit_flow_violations = 0
    trader_violations = 0 #Trader nomination violation
    entry_flow_violations_EN = 0
    entry_flow_violations_EH = 0
    exit_flow_violations_XN = 0
    exit_flow_violations_XH = 0

    for k, v in solution.items():
        if re.search('(ub|lb)_pressure_violation_DA', k):
            key = re.sub('(ub|lb)_pressure_violation_DA\[(\S*)]',r'\1_\2', k)
            if not re.search('_aux|_HD|_ND', key): pr_violations += max(0,v)

        if re.search('slack_DA', k):
            res = re.sub('(\S*)\[(\S*)]', r'\1\2', k)
            if 'entry' in res:
                if 'EN' in res:
                    entry_flow_violations_EN += v
                else:
                    entry_flow_violations_EH += v
            else:
                if 'XN' in res:
                    exit_flow_violations_XN += v
                else:
                    exit_flow_violations_XH += v

        if re.search('scenario_balance_TA', k):
            trader_violations += abs(v)

    entry_flow_violations = abs(entry_flow_violations_EN) + abs(entry_flow_violations_EH)
    exit_flow_violations = abs(exit_flow_violations_XN) + abs(exit_flow_violations_XH)

    dispatcher_penalty = int(args.pressure_wt_factor * pr_violations
                             + args.s_flow_wt_factor * entry_flow_violations
                             + args.x_flow_wt_factor * exit_flow_violations)
    trader_penalty = trader_violations

    return [dispatcher_penalty, trader_penalty]

def get_con_pos():
    va, rs, cs = [0 for _ in range(3)]
    for k,v in get_dispatcher_dec().items():
        if re.search('va', k):
            va += 1
        if re.search('zeta', k):
            rs += 1
        if re.search('compressor',k):
            cs += 1
    rs_pos = va
    gas_pos = va+rs
    cs_pos = va+rs+cs
    return rs_pos,gas_pos,cs_pos

def get_bn_pressures_flows(solution):
    exit_pr_flows = {}
    for k,v in solution.items():
        if re.findall(r"var_node_p\[("+'|'.join(no.exits)+r")]",k):
            exit_pr_flows[k] = v
        elif re.findall(r"var_node_Qo_in\[("+'|'.join(no.exits)+r")]",k):
            exit_pr_flows[k] = v
        elif re.findall(r"var_pipe_Qo_in\[("+'|'.join(special_pipes)+r")]",k):
            exit_pr_flows[k] = v
    return exit_pr_flows

#Function to remove duplicate entries from fixed_decisions.yml file
def remove_duplicate_decision(prev_agent_decisions, new_agent_decisions, step, label = None):
    key_label ='entry_nom' if label else '(va|zeta|gas|compressor)'
    for (k1,v1), (k2,v2) in zip(prev_agent_decisions.items(), new_agent_decisions.items()):
        if re.search(rf"{key_label}",k1):
            for (l1,v_1),(l2,v_2) in zip(v1.items(),v2.items()):
                for (label1, value1), (label2, value2) in zip(v_1.items(), v_2.items()):
                    for i in range(step-1, -1, -1):
                        if i in value1:
                            break
                    if value1[i] == value2[step]:
                        del value2[step]

    return new_agent_decisions

#Create csv to store agent decisions, boundary flows, pressures and agent penalty values
def create_dict_for_csv(agent_decisions, step = 0, timestamp = '', penalty = [], bn_pr_flows = {}):

    extracted_ = {}
    extracted_['Time'] = timestamp
    for i, j in agent_decisions.items():
        for k,l in j.items():
            for m,n in l.items():
                key = i+"["+m+"]"
                for p in range(step,-1,-1):
                    if p in n:
                        extracted_[key] = n[p]
                        break
    if not bn_pr_flows:
        for i in no.exits:
            extracted_[f"var_node_p[{i}]"] = None
        for i in no.exits:
            extracted_[f"var_node_Qo_in[{i}]"] = None
        for i in special_pipes:
            extracted_[f"var_pipe_Qo_in[{i}]"] = None
    else:
        for i, j in bn_pr_flows.items():
            extracted_[i] = round(j,3)
    if penalty:
        extracted_['Dispatcher Penalty'] = penalty[0]
        extracted_['Trader Penalty'] = penalty[1]
        extracted_['Accumulated C_EH'] = c_values[step][0]
        extracted_['Accumulated C_EN'] = c_values[step][1]
    else:
        extracted_['Dispatcher Penalty'] = None
        extracted_['Trader Penalty'] = None
        extracted_['Accumulated C_EH'] = None
        extracted_['Accumulated C_EN'] = None

    fieldnames = reordered_headers(list(extracted_.keys()))
    # fieldnames = list(extracted_.keys())

    return fieldnames, extracted_

def reordered_headers(fieldnames):
    order = [0,1,12,2,13,3,15,4,14,5,6,7,8,9,10,11,16,17,18,19]
    fieldnames = [fieldnames[i] for i in order]
    return fieldnames

def write_win_ratio():
    with open(path.join(data_path, 'output/nn_win_ratio.csv'), 'w+', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(win_ratios)
