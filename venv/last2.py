import csv
import sys
import time
import datetime
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


def create_clusters(n_cluster, data):
    df = DataFrame(data, columns=["attr_0", "attr_1"])
    n_sub_cluster = n_cluster

    kmeans = KMeans(n_clusters=n_sub_cluster).fit(df)
    result = kmeans.predict(df)
    clusters = [[] for i in range(n_sub_cluster)]

    for i in range(len(result)):
        clusters[int(result[i])].append({
            "attr_0": float(data["attr_0"][i]),
            "attr_1": float(data["attr_1"][i]),
            "id": data["id"][i],
            "label": data["label"][i]
        })

    virtual_x_mins = [sys.maxint for i in range(n_sub_cluster)]
    virtual_y_mins = [sys.maxint for i in range(n_sub_cluster)]

    for i, cluster in enumerate(clusters):
        for node in cluster:
            virtual_x_mins[i] = min(virtual_x_mins[i], node["attr_0"])
            virtual_y_mins[i] = min(virtual_y_mins[i], node["attr_1"])

    return virtual_x_mins, virtual_y_mins


def get_children(n_cluster, data, virtual_x_mins, virtual_y_mins):
    start_time = datetime.datetime.now()
    children = [[] for i in range(n_cluster)]

    for i in range(n_cluster):
        for j in range(len(data['label'])):
            node = {
                "attr_0": float(data["attr_0"][j]),
                "attr_1": float(data["attr_1"][j]),
                "id": data["id"][j],
                "label": data["label"][j]
            }

            if node["attr_0"] >= virtual_x_mins[i] and node["attr_1"] >= virtual_y_mins[i]:
                children[i].append(node)

    end_time = datetime.datetime.now()
    processing_time = (end_time - start_time)

    print "\n-------- Waktu Proses dan Jumlah Anak {} Cluster ---------".format(n_cluster)
    print ">> Waktu proses penghitungan child dengan jumlah cluster {} : ".format(n_cluster) + str(processing_time)

    return children


def show_clustering_result(n_cluster, cluster_children, start_time, virtual_x_mins, virtual_y_mins):
    # for i in range(n_cluster):
    #     print "Banyak anak / score cluster ke-[{}] : ".format(i) + str(len(cluster_children[i]))
    #     print "xmin ke-[{}] : ".format(i) + str(virtual_x_mins[i])
    #     print "ymin ke-[{}] : ".format(i) + str(virtual_y_mins[i])

    end_time = datetime.datetime.now()
    processing_time = (end_time - start_time)
    print ">> Waktu proses pembuatan cluster berjumlah {} : ".format(n_cluster) + str(processing_time)


def normalize_attr(min, max, x):
    return (float(1-min)+float(x))/(float(1-min)+float(max))


def get_properties(attrs, data):
    properties = {
        "attr_0": {
            "min": sys.maxint,
            "max": 0
        },
        "attr_1": {
            "min": sys.maxint,
            "max": 0
        }
    }
    for attribute in attrs:
        for value in data[attribute]:
            properties[attribute]["min"] = min(properties[attribute]["min"], int(float(value)))
            properties[attribute]["max"] = max(properties[attribute]["max"], int(float(value)))

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
    counter = 0

    for i in range(len(data["attr_0"])):
        if int(float(data["attr_0"][i])) >= data_target["attr_0"] and int(float(data["attr_1"][i])) >= data_target["attr_1"]:
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


def get_cluster_penalties(virtual_x_mins, virtual_y_mins, properties):
    target = [int(val) for val in sys.argv[1].split(",")]
    weight = [float(val) for val in sys.argv[3].split(",")]

    penalties = []
    for i in range(len(virtual_x_mins)):
        attr_0_normalized = normalize_attr(properties["attr_0"]["min"], properties["attr_0"]["max"], virtual_x_mins[i])
        attr_1_normalized = normalize_attr(properties["attr_1"]["min"], properties["attr_1"]["max"], virtual_y_mins[i])

        abs_attr_0 = abs(attr_0_normalized - target[0])
        abs_attr_1 = abs(attr_1_normalized - target[1])

        cluster_penalty = abs_attr_0 * (1.0 - weight[0]) + abs_attr_1 * (1.0 - weight[1])
        penalties.append(cluster_penalty)

    return penalties


def create_n_cluster_solutions(cluster_children, penalties, virtual_x_mins, virtual_y_mins):
    threshold = int(sys.argv[2])
    solutions = []
    for i in range(len(cluster_children)):
        solution = {
            "subscribers": len(cluster_children[i]),
            "penalty": penalties[i],
            "virtual_x_min": virtual_x_mins[i],
            "virtual_y_min": virtual_y_mins[i]
        }
        if solution["subscribers"] >= threshold:
            solutions.append(solution)

    return solutions


def create_final_solutions(solutions):
    user_defined = int(sys.argv[4])
    n_solutions = min(len(solutions), user_defined)
    final_solutions = []
    counter = 0

    for solution in sorted(solutions, key=lambda x: x["penalty"]):
        if counter > n_solutions:
            break

        final_solutions.append(solution)
        counter += 1

    return final_solutions


def show_final_solutions(final_solutions):
    print "\nFinal Solutions:"
    for solution in final_solutions:
        print solution


def main():
    print "Process"
    data = load_initial_data("datasets/independent/dataset_100000_7.csv")
    # print data

    # attrs = filter(lambda key: key.startswith('attr_'), list(data.keys()))

    # attribute = list()


    # target_subs_score = score_target(sys.argv[1], ["attr_0", "attr_1"], data)
    # print target_subs_score

    ekpektasi_subs = int(sys.argv[2])
    # print ekpektasi_subs

    weight_target = generate_weight(sys.argv[3], ["attr_0", "attr_1"])
    # print weight_target

    # properties = get_properties(["attr_0", "attr_1"], data)
    # n_clusters = [100, 75, 50, 25, 10]
    # solutions = []
    #
    # for n_cluster in n_clusters:
    #     start_time = datetime.datetime.now()
    #     virtual_x_mins, virtual_y_mins = create_clusters(n_cluster, data)
    #     cluster_children = get_children(n_cluster, data, virtual_x_mins=virtual_x_mins, virtual_y_mins=virtual_y_mins)
    #     show_clustering_result(n_cluster, cluster_children, start_time=start_time, virtual_x_mins=virtual_x_mins, virtual_y_mins=virtual_y_mins)
    #
    #     counter = 0
    #     for children in cluster_children:
    #         if len(children) >= ekpektasi_subs:
    #             counter+=1
    #     print "Jumlah cluster yang memenuhi ekspektasi untuk n_cluster = {} adalah {}".format(n_cluster, counter)
    #
    #     cluster_penalties = get_cluster_penalties(virtual_x_mins, virtual_y_mins, properties)
    #     # print cluster_penalties
    #
    #     n_cluster_solutions = create_n_cluster_solutions(cluster_children=cluster_children,
    #                                                      penalties=cluster_penalties,
    #                                                      virtual_x_mins=virtual_x_mins,
    #                                                      virtual_y_mins=virtual_y_mins)
    #     solutions += n_cluster_solutions
    #
    # final_solutions = create_final_solutions(solutions)
    # print final_solutions


if __name__ == '__main__':
    main()
