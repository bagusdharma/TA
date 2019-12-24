import csv
import sys
import datetime
import threading
import psutil
import os

from pandas import DataFrame
from sklearn.cluster import KMeans


def load_initial_data(filename):
    data = {}
    with open(filename) as csv_file:
        read_csv = csv.reader(csv_file, delimiter=',')
        first_read = True
        header = []

        for row in read_csv:
            if first_read:
                header = row
                for key in header:
                    data[key] = []
                first_read = False
            else:
                for i, label in enumerate(header):
                    data[label].append(row[i])

    return data


def create_virtual_attrs_minimums(n_cluster, data, attrs):
    df = DataFrame(data, columns=attrs)
    k_means = KMeans(n_clusters=n_cluster).fit(df)
    result = k_means.predict(df)
    clusters = [[] for _ in range(n_cluster)]

    for i in range(len(result)):
        node = {
            "id": data["id"][i],
            "label": data["label"][i]
        }
        for attr_ in attrs:
            node[attr_] = float(data[attr_][i])

        clusters[int(result[i])].append(node)

    virtual_attrs_minimums = {}
    for attr_ in attrs:
        virtual_attrs_minimums[attr_] = [sys.maxint for _ in range(n_cluster)]

    for i, cluster in enumerate(clusters):
        for node in cluster:
            for attr_ in attrs:
                virtual_attrs_minimums[attr_][i] = min(virtual_attrs_minimums[attr_][i], node[attr_])

    return virtual_attrs_minimums


def get_children(n_cluster, data, attrs, virtual_attrs_minimums):
    children = [[] for _ in range(n_cluster)]

    for i in range(n_cluster):
        for j in range(len(data["id"])):
            node = {
                "id": data["id"][j],
                "label": data["label"][j]
            }

            for attr_ in attrs:
                node[attr_] = float(data[attr_][j])

            data_passed = True
            for attr_ in attrs:
                if data_passed and node[attr_] < virtual_attrs_minimums[attr_][i]:
                    data_passed = False
                else:
                    break

            if data_passed:
                children[i].append(node)

    return children


def normalize_attr(min, max, x):
    return (float(1-min)+float(x))/(float(1-min)+float(max))


def get_properties(attrs, data):
    properties = {}
    for attr_ in attrs:
        properties[attr_] = {
            "min": sys.maxint,
            "max": 0
        }

    for attr_ in attrs:
        for value in data[attr_]:
            properties[attr_]["min"] = min(properties[attr_]["min"], int(float(value)))
            properties[attr_]["max"] = max(properties[attr_]["max"], int(float(value)))

    return properties


def basic_target():
    t = dict()
    t["id"] = "target"
    t["label"] = "target"
    return t


def generate_target(attr_input, attrs):
    target = basic_target()
    attr_value = [int(value) for value in attr_input.split(',')]

    for i in range(len(attrs)):
        target[attrs[i]] = attr_value[i]

    return target


def score_target(attr_input, attrs, data):
    data_target = generate_target(attr_input, attrs)
    print data_target

    counter = 0
    for i in range(len(data["id"])):
        data_passed = True
        for attr_ in attrs:
            if data_passed and int(float(data[attr_][i])) < data_target[attr_]:
                data_passed = False
            else:
                break

        if data_passed:
            counter += 1

    return counter


def generate_weight(weight_inp, attrs):
    try:
        weight = dict()
        weight_list = weight_inp.split(',')
        for i in range(len(attrs)):
            weight[attrs[i]] = float(weight_list[i])
    except (IndexError, ValueError) as e:
        weight = dict()
        weight_default = 1.0 / float(len(attrs))
        for i in range(len(attrs)):
            weight[attrs[i]] = weight_default

    return weight


def get_cluster_penalties(virtual_attrs_minimums, attrs, properties):
    keys = virtual_attrs_minimums.keys()
    len_data = len(virtual_attrs_minimums[keys[0]])

    target = [int(val) for val in sys.argv[1].split(",")]
    weight = [float(val) for val in sys.argv[3].split(",")]

    penalties = []
    for i in range(len_data):
        cluster_penalty = 0.0
        for j, attr_ in enumerate(attrs):
            attr_normalized_before = normalize_attr(min=properties[attr_]["min"],
                                             max=properties[attr_]["max"],
                                             x=target[j])

            attr_normalized_after = normalize_attr(min=properties[attr_]["min"],
                                             max=properties[attr_]["max"],
                                             x=virtual_attrs_minimums[attr_][i])

            # abs_attr_ = abs(attr_normalized - target[j])
            abs_attr_ = abs(attr_normalized_after - attr_normalized_before)

            cluster_penalty += (abs_attr_ * (1.0 - weight[j]))
        penalties.append(cluster_penalty)

    return penalties


def create_n_cluster_solutions(cluster_children, penalties, attrs, virtual_attrs_minimums):
    threshold = int(sys.argv[2])

    solutions = []
    for i in range(len(cluster_children)):
        solution = {
            "subscribers": len(cluster_children[i]),
            "penalty": penalties[i],
        }
        for attr_ in attrs:
            solution[attr_] = virtual_attrs_minimums[attr_][i]

        if solution["subscribers"] >= threshold:
            solutions.append(solution)

    return solutions


def create_final_solutions(solutions):
    user_defined = int(sys.argv[4])
    n_solutions = min(len(solutions), user_defined)
    final_solutions = []
    counter = 0

    for solution in sorted(solutions, key=lambda x: x["penalty"]):
        if counter == n_solutions:
            break

        final_solutions.append(solution)
        counter += 1

    return final_solutions


def show_final_solutions(final_solutions):
    print "\nFinal Solutions:"
    for solution in final_solutions:
        print solution


def show_precompute_time(n_cluster, start_precompute_time):
    end_precompute_time = datetime.datetime.now()
    precompute_time = (end_precompute_time - start_precompute_time)
    print ">> Waktu proses Pre-Compute Time {} Cluster : ".format(n_cluster) + str(precompute_time)


def main():

    print "Process"
    data = load_initial_data("datasets/Forest_Cover/dimensi/dataset_30000_5.csv")
    # data = load_initial_data("datasets/independent/dataset_30000_3.csv")

    # print 'Data berhasil dimasukkan'
    # print '\n'
    # print data

    attrs = filter(lambda key: key.startswith('attr_'), list(data.keys()))

    print "Input Data Berhasil diproses dan dilakukan query refinement"

    target_subs_score = score_target(sys.argv[1], attrs, data)
    print "Subscribers : " + str(target_subs_score)

    properties = get_properties(attrs, data)
    n_clusters = [100, 75, 50, 25, 10]

    dummy_time = datetime.datetime.now()
    mutable_obj = {
        'sum_running_time': (dummy_time - dummy_time),
        'solutions': []
    }

    for n_cluster in n_clusters:
        def execute_clustering():
            start_precompute_time = datetime.datetime.now()
            virtual_points = create_virtual_attrs_minimums(n_cluster, data, attrs)
            cluster_children = get_children(n_cluster, data, attrs, virtual_attrs_minimums=virtual_points)
            show_precompute_time(n_cluster, start_precompute_time=start_precompute_time)

            s_time = datetime.datetime.now()
            cluster_penalties = get_cluster_penalties(virtual_points, attrs, properties)
            n_cluster_solutions = create_n_cluster_solutions(cluster_children=cluster_children,
                                                             penalties=cluster_penalties,
                                                             attrs=attrs,
                                                             virtual_attrs_minimums=virtual_points)
            e_time = datetime.datetime.now()
            r_time = e_time - s_time

            mutable_obj['sum_running_time'] += r_time
            mutable_obj['solutions'] += n_cluster_solutions

        t = threading.Thread(target=execute_clustering)
        t.start()
        t.join()

    # total solutions yang memenuhi ekpektasi_subs
    solutions = mutable_obj['solutions']
    sum_running_time = mutable_obj['sum_running_time']

    print '\n'
    print 'total virtual yang memenuhi ekspektasi : ' + str(len(solutions))

    # input user solutions yang memenuhi ekspektasi
    start_running_time = datetime.datetime.now()
    final_solutions = create_final_solutions(solutions)
    end_running_time = datetime.datetime.now()
    running_time = (end_running_time - start_running_time)

    sum_running_time += running_time

    show_final_solutions(final_solutions)

    print '\nRunning time : {}'.format(str(sum_running_time))
    print 'Average running time for {} expected solutions: {}'.format(sys.argv[4], str(sum_running_time / int(sys.argv[4])))

    process = psutil.Process(os.getpid())
    mem_usage = float(process.memory_info().rss) / 1000000.0
    print "Memory usage: " + str(mem_usage) + " MB "

if __name__ == '__main__':
    main()
