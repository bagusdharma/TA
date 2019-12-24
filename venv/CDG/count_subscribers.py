import json
import glob
import sys
import threading
import datetime

def basic_target():
    t = dict()
    t["id"] = "target"
    t["label"] = "target"
    t["child"] = 0
    t["parent"] = 0
    t["visited"] = False
    t["is_root"] = False
    return t

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

def find_bottom(set, v, attribute):
    bottom_cand = list(set)
    result = []
    i = 1;
    for cand in bottom_cand:
        is_bottom = True
        for r in bottom_cand:
            if r is cand:
                continue
            else:
                if is_dominating(v[cand], v[r], attribute):
                    is_bottom = False
                    break
        if is_bottom:
            result.append(cand)
    return result

def generick_target(attr_input, attribute):
    target = basic_target()
    attr_value = attr_input.split(',')
    for x in range(len(attribute)):
        target[attribute[x]] = int(attr_value[x])
    return target

def calculate_cost(preference, g, attribute):
    cost = 0
    is_first = True
    for attr in attribute:
        cost += preference[attr]
        is_first = False
    return cost

def generatekey(x):
    results = list()
    for attr in attribute:
        results.append(graph_full[x][attr])
    return tuple(results)

def search_clean_cut(graph, node, target, edges, attribute, is_initial = False):
    cut = list()
    if not is_initial:
        if node in visited:
            print "Returned because node",node,"has been visited"
            return cut
        else:
            visited.append(node)
    if is_initial or is_dominating(graph[node], target, attribute):
        if is_initial:
            child_dict = {k: v for k, v in graph.iteritems() if v["is_root"]}
            child = child_dict.keys()
        else:
            cut.append(node)
            child = [d['to'] for d in edges if d['from'] == node]
        for next in child:
            cut += search_clean_cut(graph, next, target, edges, attribute)
    return cut


# ---------------------- MAIN PROGRAM ----------------------
time_start = datetime.datetime.now()
print "Program started"
try:
    session = sys.argv[2].split(',')
    session_name = session[0]
    session_type = session[1]
    session_full_id = "_"+session_name+"_"+session_type
except IndexError:
    session = False
    session_name = ""
    session_type = ""
    session_full_id = ""
visited = list()
with open('session'+session_full_id+'/graph.json') as f:
    data = json.load(f)
    graph = dict(data)
with open('session'+session_full_id+'/attribute.json') as f:
    data = json.load(f)
    attribute = list(data)
with open('session'+session_full_id+'/edges.json') as f:
    data = json.load(f)
    edges = list(data)
target = generick_target(sys.argv[1], attribute)
threads = []
gross_cut = search_clean_cut(graph,False,target,edges,attribute, True)
potential_subs = len(gross_cut)
print "\n\n====================\n"
print "FINAL RESULTS:"
print "Potential subscribers: "+str(potential_subs)
print "\n"
results = {
    "target": target,
    "potential_subs": potential_subs,
}
with open("session"+session_full_id+"/countsubs_results.json", 'w') as fp:
    json.dump(results, fp)

print "RUNTIME RESULTS:"
time_end = datetime.datetime.now()
full_runtime = time_end - time_start
print "Program finished with runtime " + str(full_runtime)
print "\n"
