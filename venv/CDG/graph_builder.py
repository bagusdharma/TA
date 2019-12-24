import random
import datetime
import time
import threading
import json
import sys
import csv
import copy
import os

try:
    import psutil
    enable_psutil = True
except ImportError as e:
    enable_psutil = False
# import resource

def format_graph(v_global, node, edges):
    root = find_skyline(node, v_global)
    for x in node:
        score = len(v_global[x]["ancestor"])
        v_global[x]["score"] = score+1
        del v_global[x]["ancestor"]
        if x in root:
            v_global[x]["is_root"] = True

def format_nodes(v, node):
    v_local = dict(v)
    result = list()
    for x in range(len(node)):
        v_local[node[x]]["label"] += "\n("
        a_idx = 0
        for a in attribute_value:
            if a_idx == 0:
                v_local[node[x]]["label"] += str(v_local[node[x]][a])
            else:
                v_local[node[x]]["label"] += ","+str(v_local[node[x]][a])
            a_idx += 1

        v_local[node[x]]["label"] += ")\n"+str(v_local[node[x]]['score'])
        result.append(v_local[node[x]])
    return result

def format_layer(v, node, start_point, edges, attribute, cut_size = False):
    global node_visited
    v_local = dict(v)
    result = dict()
    num_of_nodes = len(node)

    if not cut_size:
        cut_size = num_of_nodes/2

    for layer in range(0,num_of_nodes+1,cut_size):
        result_temp = search_clean_cut(v_local, False, layer, edges, attribute, start_point, True)

        result_temp = sorted(result_temp, key=generatekey)

        result_temp = find_skyline(result_temp, v_local)
        result[layer] = result_temp

        start_point = result[layer]
        node_visited = list()

        if len(result_temp) < 1:
            del result[layer]
            break
    return result

def search_clean_cut(graph, node, layer_size, edges, attribute, root = [], is_initial = False):
    cut = list()
    clean_cut = list()

    if is_initial:
        child = root
    else:

        if node in node_visited:
            return list()

        else:
            node_visited.append(node)

            if graph[node]["score"] >= layer_size:
                return [node]

            child = [d['to']
                     for d in edges
                     if d['from'] == node]

    for next in child:
        cut += search_clean_cut(graph, next, layer_size, edges, attribute)
    return cut

def slice_vertex(v, max):
  v_thread = []
  for x in range(0,len(v),max):
    v_thread.append(v[x:x+max])
  return v_thread

def remove_from_list(origin, to_remove):
  temp = set(to_remove)
  result = [value
            for value in origin
            if value not in to_remove]
  return result

def merge(first_list, second_list):
  return first_list + list(set(second_list) - set(first_list))

def is_dominating(subject, target):
    dominate = 0
    for attr in attribute_value:
        if subject[attr] > target[attr]:
            return False
        elif subject[attr] < target[attr]:
            dominate+=1
    if dominate < 1:
        return False
    else:
        return True

def is_skyline(target, set, v):
  skyline_cand = list(set)
  for candidate in skyline_cand:

    if target is candidate:
      continue

    elif is_dominating(v[candidate], v[target]):
      return False
  return True

def find_skyline(set, v):
  skyline_cand = list(set)
  result = []
  i = 1
  for record in skyline_cand:
    if is_skyline(record, skyline_cand[0:i], v):
      result.append(record)
    i += 1
  return result

def find_dominating(r, set, v):
  result = []
  for s in set:
    if r is s:
      continue

    elif is_dominating(v[r], v[s]):
      result.append(s)
  return result

def progress_report(node):
  global node_visited
  global num_of_nodes
  if enable_psutil:
      node_visited = merge(node_visited, [node])
      progress = float(len(node_visited))/float(num_of_nodes)*float(100)
      process = psutil.Process(os.getpid())
      mem_usage = float(process.memory_info().rss)/1000000.0
      sys.stdout.write("\rNumber of visited nodes: " + str(len(node_visited)) + " of " + str(num_of_nodes) + " nodes --- " + str(progress) + "% ("+str(mem_usage)+" MB)")
      sys.stdout.flush()

def generatekey(x):
    results = list()
    for attr in attribute_value:
        results.append(vertex[x][attr])
    return tuple(results)


def build_graph(node, thread_vertex, sub_vertex, is_initial = False):
    if not is_initial:
        if vertex[node]["visited"] or node not in thread_vertex:
            return
        else:
            child_cand = list(find_dominating(node, sub_vertex, vertex))
            vertex[node]["visited"] = True

            for c in child_cand:
                if node not in vertex[c]["ancestor"]:
                    vertex[c]["ancestor"].append(node)
    else:
        child_cand = thread_vertex

    child = find_skyline(child_cand, vertex)
    sub_vertex_cand = remove_from_list(list(child_cand), child)

    if not is_initial:
        for c in child:
            edge_temp = dict()
            edge_temp["to"] = c
            edge_temp["from"] = node
            edges.append(edge_temp)
        progress_report(node)

    for record in child:
        if is_initial:

            index_cut = sub_vertex.index(record)
            build_graph(record, thread_vertex, sub_vertex[index_cut:])
        else:
            build_graph(record, thread_vertex, sub_vertex_cand)
    return

class cdgThread(threading.Thread):
    def __init__(self, threadID, name, thread_vertex, sub_vertex):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.thread_vertex = thread_vertex
        self.sub_vertex = sub_vertex
    def run(self):
        print "\nTHREAD "+self.name+" started"
        build_graph(None, self.thread_vertex, self.sub_vertex, True)
        t_end = datetime.datetime.now()
        self.runtime = t_end - time_start
        print "THREAD "+self.name+" finished with runtime " + str(self.runtime)

ts = time.time()
st_start = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d__%H:%M:%S')
time_start = datetime.datetime.now()

print "Program started"
count = 0
node_visited = []
num_of_nodes = 0

try:
    max_nodes_in_thread = int(sys.argv[1])
except IndexError:
    max_nodes_in_thread = 10000

try:
    cut_size = int(sys.argv[2])
except IndexError:
    cut_size = False

# try:
#     session = sys.argv[3].split(',')
#     session_name = session[0]
#     session_type = session[1]
#     session_full_id = "_"+session_name+"_"+session_type
# except IndexError:
#     session = False
#     session_name = ""
#     session_type = ""
#     session_full_id = ""

vertex = dict()
attribute = list()
edges = list()

# if session:
#     dataset_filename = "datasets/"+session_type+"/dataset_"+session_name+".csv"
# else:
dataset_filename = "datasets/independent/node/dataset_50000_3.csv"

with open(dataset_filename) as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    init = True
    for row in readCSV:
        if init:
            attribute = list(row)
        else:
            vertex_data = dict()
            for idx in range(len(row)):
                if idx > 1:
                    vertex_data[attribute[idx]] = int(row[idx])
                else:
                    vertex_data[attribute[idx]] = row[idx]
            vertex[row[0]] = vertex_data
            vertex[row[0]]["score"] = 0
            vertex[row[0]]["ancestor"] = list()
            vertex[row[0]]["visited"] = False
            vertex[row[0]]["is_root"] = False
            num_of_nodes += 1
        init = False

attribute_value = list(attribute[2:])
properties = dict()

for attr in attribute_value:
    vertex_min = sorted(vertex, key=lambda x: (vertex[x][attr]))
    properties[attr] = {
        "min": vertex[vertex_min[0]][attr],
        "max": vertex[vertex_min[-1]][attr]
    }

vertex_sorted = sorted(vertex, key=generatekey)
vertex_thread = slice_vertex(vertex_sorted, max_nodes_in_thread)
threads = []

for t in range(0,len(vertex_thread)):
    threads.append(cdgThread(t+1, "Graph Builder #"+str(t+1), vertex_thread[t], vertex_sorted))
for t in threads:
    t.start()
for t in threads:
    t.join()

# folder = 'CDG/session/30k_3d'
# for the_file in os.listdir(folder):
#     file_path = os.path.join(folder, the_file)
#     try:
#         if os.path.isfile(file_path):
#             os.unlink(file_path)
#     except Exception as e:
#         print(e)

format_graph(vertex, vertex_sorted, edges)
with open("session/IND/node/50k_3d/graph.json", 'w') as fp:
    json.dump(vertex, fp)

node_visited = list()

first_layer_root = {k: v for k, v in vertex.iteritems() if v["is_root"]}
first_layer_root = first_layer_root.keys()
clean_cut_layer = format_layer(vertex, vertex_sorted, first_layer_root, edges, attribute_value, cut_size)

with open("session/IND/node/50k_3d/clean_cut_layer.json", 'w') as fp:
    json.dump(clean_cut_layer, fp)
del clean_cut_layer

nodes = format_nodes(vertex, vertex_sorted)

with open("session/IND/node/50k_3d/nodes.json", 'w') as fp:
    json.dump(nodes, fp)
del nodes

with open("session/IND/node/50k_3d/attribute.json", 'w') as fp:
    json.dump(attribute_value, fp)

with open("session/IND/node/50k_3d/properties.json", 'w') as fp:
    json.dump(properties, fp)
del properties

with open("session/IND/node/50k_3d/edges.json", 'w') as fp:
    json.dump(edges, fp)
del edges

print "\nRUNTIME RESULTS:"
print "Number of nodes: "+str(num_of_nodes)

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
res_data.append("algo1")
res_data.append(num_of_nodes)
res_data.append(len(attribute_value))
# res_data.append(session_type)
res_data.append(len(threads))
res_data.append(full_runtime)
res_data.append(mem_usage)
res.append(res_data)

# if session:
with open("session_log/graph_script.csv", "a") as output:
    writer = csv.writer(output, lineterminator='\n')
    writer.writerows(res)

# else:
#     with open("CDG/session_log/graph_manual.csv", "a") as output:
#         writer = csv.writer(output, lineterminator='\n')
#         writer.writerows(res)
