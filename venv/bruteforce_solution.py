import json
import sys
import datetime
import time
import os, shutil
try:
    import psutil
    enable_psutil = True
except ImportError as e:
    enable_psutil = False
import resource
import csv

def is_dominating(subject, target, attribute):
    dominate = 0
    for attr in attribute:
        if subject[attr] > target[attr]:
            return False
        elif subject[attr] < target[attr]:
            dominate+=1
    if dominate < 1:
        return False
    else:
        return True

def normalize_attr(min, max, x):
    return (float(1-min)+float(x))/(float(1-min)+float(max))

ts = time.time()
st_start = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d__%H:%M:%S')
time_start = datetime.datetime.now()
print "Program started"
count = 0
num_of_nodes = 0
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
dataset = dict()
attribute = list()
edges = list()
if session:
    dataset_filename = "datasets/"+session_type+"/dataset_"+session_name+".csv"
else:
    dataset_filename = "dataset.csv"
with open(dataset_filename) as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    init = True
    for row in readCSV:
        if init:
            attribute = list(row)
        else:
            dataset_data = dict()
            for idx in range(len(row)):
                if idx > 1:
                    dataset_data[attribute[idx]] = int(row[idx])
                else:
                    dataset_data[attribute[idx]] = row[idx]
            dataset[row[0]] = dataset_data
            dataset[row[0]]["score"] = 0
            dataset[row[0]]["ancestor"] = list()
            dataset[row[0]]["visited"] = False
            dataset[row[0]]["is_root"] = False
            num_of_nodes+=1
        init = False
with open('session'+session_full_id+'/properties.json') as f:
    properties = dict(json.load(f))
with open('session'+session_full_id+'/countsubs_results.json') as f:
    countsubs_results = dict(json.load(f))
attribute_value = list(attribute[2:])
try:
    weight_inp = sys.argv[2]
    weight_list = weight_inp.split(',')
    weight = dict()
    for i in range(len(attribute_value)):
        weight[attribute_value[i]] = float(weight_list[i])
except (IndexError,ValueError) as e:
    weight = dict()
    weight_default = 1.0/float(len(attribute_value))
    for i in range(len(attribute_value)):
        weight[attribute_value[i]] = weight_default
cand = list()
best_penalty = 999.9
solution = None
normalized_before = dict()
for attr in attribute_value:
    normalized_before[attr] = normalize_attr(properties[attr]["min"], properties[attr]["max"], countsubs_results["target"][attr])
for c in dataset:
    ancscore = 0
    for d in dataset:
        if is_dominating(dataset[d],dataset[c],attribute_value):
            ancscore+=1
    if ancscore >= expected_subs:
        penalty = 0.0
        for attr in attribute_value:
            normalized_after = normalize_attr(properties[attr]["min"], properties[attr]["max"], dataset[c][attr])
            penalty += ((normalized_after - normalized_before[attr]) * (1.0 - weight[attr]))
        if penalty < best_penalty:
            solution = c
            best_penalty = penalty
if solution == None:
    dataset['00'] = dict()
    for attr in attribute_value:
        dataset['00'][attr] = properties[attr]["max"]
    dataset['00']['score'] = len(dataset)-1
    dataset['00']['label'] = "R00"
    solution = "00"
    penalty = 0.0
    for attr in attribute_value:
        normalized_after = normalize_attr(properties[attr]["min"], properties[attr]["max"], dataset['00'][attr])
        penalty += ((normalized_after - normalized_before[attr]) * (1.0 - weight[attr]))
    best_penalty = penalty
print "BEST SOLUTION:"
print solution
for attr in attribute_value:
    print attr,":",dataset[solution][attr]
print "subscribers :",dataset[solution]["score"]
print "penalty :",best_penalty
print "\n"
print "\nRUNTIME RESULTS:"
print "Number of nodes: "+str(len(dataset))
time_end = datetime.datetime.now()
full_runtime = time_end - time_start
print "Program finished with runtime " + str(full_runtime)
if enable_psutil:
    process = psutil.Process(os.getpid())
    mem_usage = float(process.memory_info().rss)/1000000.0
    print "Memory usage:",mem_usage
else:
    mem_usage = 0.0

res = list()
ts = time.time()
st_end = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d__%H:%M:%S')
res_data = list()
res_data.append(st_start)
res_data.append(st_end)
res_data.append("bruteforce")
res_data.append(len(dataset))
res_data.append(len(attribute_value))
res_data.append(session_type)
res_data.append(expected_subs)
initial_value = list()
recomended_value = list()
weight_list = list()
for attr in attribute_value:
    initial_value.append(countsubs_results["target"][attr])
    recomended_value.append(dataset[solution][attr])
    weight_list.append(weight[attr])
res_data.append("|".join(list(map(str, weight_list))))
res_data.append("|".join(list(map(str, initial_value))))
res_data.append("|".join(list(map(str, recomended_value))))
res_data.append(dataset[solution]["label"])
res_data.append(best_penalty)
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
