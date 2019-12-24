import json
import glob
import sys
import datetime
import time
import os, shutil
import resource
import csv

# find x data dominate y data
def is_dominating(subject, target, attribute):
    dominate = 0
    for attr in attribute:
        # kalau nilai atribut nya lebih besar dari target berarti x tidak mendominasi y
        # konsepnya cdg adalah atribut lebih kecil mendominasi atribut yg lebih besar
        if subject[attr] > target[attr]:
            return False
        elif subject[attr] < target[attr]:
            dominate+=1
    if dominate < 1:
        return False
    else:
        return True

    # note : skyline query = subjek masalah optimasi yg digunakan dalam kueri untuk memfilter hasil dari database
    #                         agar hanya objek yg dikeluarkan tidak lebih buruk dari yg lainnya

def is_skyline(target, set, v, attribute):
    skyline_cand = list(set)
    for candidate in skyline_cand:
        if target is candidate:
            continue
        elif is_dominating(v[candidate], v[target], attribute):
            return False
    return True

def find_skyline(set, v, attribute):
    skyline_cand = list(set)
    result = []
    i = 1
    for record in skyline_cand:
        if is_skyline(record, skyline_cand[0:i], v, attribute):
            result.append(record)
        i+=1
    return result

def normalize_attr(min, max, x):
    return (float(1-min)+float(x))/(float(1-min)+float(max))

def find_new_clean_cut(graph, node, min_subs, edges, attribute, root = [], is_initial = False):
    cut = list()
    clean_cut = list()

    if is_initial:
        child = root
    else:
        if node in node_visited:
            return list()
        else:
            node_visited.append(node)
            if graph[node]["score"] >= min_subs:
                return [node]
            child = [d['to'] for d in edges if d['from'] == node]
    for next in child:
        cut += find_new_clean_cut(graph, next, min_subs, edges, attribute)
    return cut

ts = time.time()
st_start = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d__%H:%M:%S')
time_start = datetime.datetime.now()
print "Program started"
expected_subs = int(sys.argv[1])
try:
    session = sys.argv[3].split(',')
    session_name = session[0]
    session_type = session[1]
    session_full_id = "_"+session_name+"_"+session_type
except IndexError:
    session = False
    session_name = ""
    session_type = ""
    session_full_id = ""
with open('session'+session_full_id+'/countsubs_results.json') as f:
    countsubs_results = dict(json.load(f))
with open('session'+session_full_id+'/edges.json') as f:
    edges = list(json.load(f))
with open('session'+session_full_id+'/attribute.json') as f:
    attribute = list(json.load(f))
with open('session'+session_full_id+'/graph.json') as f:
    graph = dict(json.load(f))
with open('session'+session_full_id+'/clean_cut_layer.json') as f:
    clean_cut_layer = dict(json.load(f))
with open('session'+session_full_id+'/properties.json') as f:
    properties = dict(json.load(f))
try:
    weight_inp = sys.argv[2]
    weight_list = weight_inp.split(',')
    weight = dict()
    for i in range(len(attribute)):
        weight[attribute[i]] = float(weight_list[i])
except (IndexError,ValueError) as e:
    weight = dict()
    weight_default = 1.0/float(len(attribute))
    for i in range(len(attribute)):
        weight[attribute[i]] = weight_default
print weight
layer_indices = clean_cut_layer.keys()
layer_indices = sorted(map(int, layer_indices))
layer = str([l for l in layer_indices if l <= expected_subs][-1])
node_visited = list()
new_clean_cut = find_new_clean_cut(graph, False, expected_subs, edges, attribute, clean_cut_layer[layer], True)
new_clean_cut = find_skyline(new_clean_cut, graph, attribute)
solution = None
solution_penalty = 999.0
normalized_before = dict()
for attr in attribute:
    normalized_before[attr] = normalize_attr(properties[attr]["min"], properties[attr]["max"], countsubs_results["target"][attr])
if len(new_clean_cut) <= 0:
    graph['00'] = dict()
    for attr in attribute:
        graph['00'][attr] = properties[attr]["max"]
    graph['00']['score'] = len(graph)-1
    graph['00']['label'] = "R00"
    new_clean_cut.append('00')

web_res = list()
first_row_web = list(attribute)
first_row_web.append('Subscribers')
first_row_web.append('Penalty')
web_res.append(first_row_web)
body_row_web = list()

for new in new_clean_cut:
    row_temp = list()
    print new
    penalty = 0.0
    for attr in attribute:
        row_temp.append(graph[new][attr])
        normalized_after = normalize_attr(properties[attr]["min"], properties[attr]["max"], graph[new][attr])
        penalty += ((normalized_after - normalized_before[attr]) * (1.0 - weight[attr]))
        print attr,":",graph[new][attr],((normalized_after - normalized_before[attr]) * weight[attr])
    if penalty < solution_penalty:
        solution = new
        solution_penalty = penalty
    row_temp.append(graph[new]["score"])
    if penalty < 0.0:
        row_temp.append(0.0)
    else:
        row_temp.append(penalty)
    body_row_web.append(row_temp)
    print "subscribers :",graph[new]["score"]
    print "penalty :",penalty
    print "\n"

print "Number of solution candidate",len(new_clean_cut)
print "BEST SOLUTION:"
print solution
for attr in attribute:
    print attr,":",graph[solution][attr]
print "subscribers :",graph[solution]["score"]
print "penalty :",solution_penalty
print "\n"
print "\nRUNTIME RESULTS:"
print "Number of nodes: "+str(len(graph))
time_end = datetime.datetime.now()
full_runtime = time_end - time_start
print "Program finished with runtime " + str(full_runtime)
mem_usage = 0.0
print "Memory usage:",mem_usage

body_row_web.sort(key=lambda x: float(x[-1]))
web_res += body_row_web
with open("session"+session_full_id+"/web_results.json", 'w') as fp:
    json.dump(web_res, fp)

res = list()
ts = time.time()
st_end = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d__%H:%M:%S')
res_data = list()
res_data.append(st_start)
res_data.append(st_end)
res_data.append("algo1")
res_data.append(len(graph))
res_data.append(len(attribute))
res_data.append(session_type)
res_data.append(expected_subs)
initial_value = list()
recomended_value = list()
weight_list = list()
for attr in attribute:
    initial_value.append(countsubs_results["target"][attr])
    recomended_value.append(graph[solution][attr])
    weight_list.append(weight[attr])
res_data.append("|".join(list(map(str, weight_list))))
res_data.append("|".join(list(map(str, initial_value))))
res_data.append("|".join(list(map(str, recomended_value))))
res_data.append(graph[solution]["label"])
res_data.append(solution_penalty)
res_data.append(full_runtime)
res_data.append(mem_usage)
res.append(res_data)
if session:
    print "Saved to session_log/solution_script.csv"
    with open("session_log/solution_script.csv", "a") as output:
        writer = csv.writer(output, lineterminator='\n')
        writer.writerows(res)
else:
    print session,"Saved to session_log/solution_manual.csv"
    with open("session_log/solution_manual.csv", "a") as output:
        writer = csv.writer(output, lineterminator='\n')
        writer.writerows(res)
