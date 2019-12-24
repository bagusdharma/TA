import csv
import sys
import datetime
import threading
import psutil
import os
from pandas import DataFrame
from sklearn.cluster import KMeans

FUNCTION load_initial_data(filename):
    data <- {}
    with open(filename) as csv_file:
        read_csv <- csv.reader(csv_file, delimiter=',')
        first_read <- True
        header <- []
        for row in read_csv:
            IF first_read:
                header <- row
                for key in header:
                    data[key] <- []
                ENDFOR
                first_read <- False
            ELSE:
                for i, label in enumerate(header):
                    data[label].append(row[i])
            ENDIF
        ENDFOR
                ENDFOR
    RETURN data
ENDFUNCTION

FUNCTION create_virtual_attrs_minimums(n_cluster, data, attrs):
    df <- DataFrame(data, columns=attrs)
    k_means <- KMeans(n_clusters=n_cluster).fit(df)
    result <- k_means.predict(df)
    clusters <- [[] for _ in range(n_cluster)]
                   ENDFOR
    for i in range(len(result)):
        node <- {
            "id": data["id"][i],
            "label": data["label"][i]
        }
        for attr_ in attrs:
            node[attr_] <- float(data[attr_][i])
        ENDFOR
        clusters[int(result[i])].append(node)
    ENDFOR
    virtual_attrs_minimums <- {}
    for attr_ in attrs:
        virtual_attrs_minimums[attr_] <- [sys.maxint for _ in range(n_cluster)]
    ENDFOR
                                                    ENDFOR
    for i, cluster in enumerate(clusters):
        for node in cluster:
            for attr_ in attrs:
                virtual_attrs_minimums[attr_][i] <- min(virtual_attrs_minimums[attr_][i], node[attr_])
    ENDFOR
        ENDFOR
            ENDFOR
    RETURN virtual_attrs_minimums
ENDFUNCTION

FUNCTION get_children(n_cluster, data, attrs, virtual_attrs_minimums):
    children <- [[] for _ in range(n_cluster)]
                   ENDFOR
    for i in range(n_cluster):
        for j in range(len(data["id"])):
            node <- {
                "id": data["id"][j],
                "label": data["label"][j]
            }
            for attr_ in attrs:
                node[attr_] <- float(data[attr_][j])
            ENDFOR
            data_passed <- True
            for attr_ in attrs:
                IF data_passed AND node[attr_] < virtual_attrs_minimums[attr_][i]:
                    data_passed <- False
                ELSE:
                    break
                ENDIF
            ENDFOR
            IF data_passed:
                children[i].append(node)
            ENDIF
    ENDFOR
        ENDFOR
    RETURN children
ENDFUNCTION

FUNCTION normalize_attr(min, max, x):
    RETURN (float(1-min)+float(x))/(float(1-min)+float(max))
ENDFUNCTION

FUNCTION get_properties(attrs, data):
    properties <- {}
    for attr_ in attrs:
        properties[attr_] <- {
            "min": sys.maxint,
            "max": 0
        }
    ENDFOR
    for attr_ in attrs:
        for value in data[attr_]:
            properties[attr_]["min"] <- min(properties[attr_]["min"], int(float(value)))
            properties[attr_]["max"] <- max(properties[attr_]["max"], int(float(value)))
    ENDFOR
        ENDFOR
    RETURN properties
ENDFUNCTION

FUNCTION basic_target():
    t <- dict()
    t["id"] <- "target"
    t["label"] <- "target"
    RETURN t
ENDFUNCTION

FUNCTION generate_target(attr_input, attrs):
    target <- basic_target()
    attr_value <- [int(value) for value in attr_input.split(',')]
                             ENDFOR
    for i in range(len(attrs)):
        target[attrs[i]] <- attr_value[i]
    ENDFOR
    RETURN target
ENDFUNCTION

FUNCTION score_target(attr_input, attrs, data):
    data_target <- generate_target(attr_input, attrs)
    OUTPUT data_target
    counter <- 0
    for i in range(len(data["id"])):
        data_passed <- True
        for attr_ in attrs:
            IF data_passed AND int(float(data[attr_][i])) < data_target[attr_]:
                data_passed <- False
            ELSE:
                break
            ENDIF
        ENDFOR
        IF data_passed:
            counter += 1
        ENDIF
    ENDFOR
    RETURN counter
ENDFUNCTION

FUNCTION generate_weight(weight_inp, attrs):
    try:
        weight <- dict()
        weight_list <- weight_inp.split(',')
        for i in range(len(attrs)):
            weight[attrs[i]] <- float(weight_list[i])
        ENDFOR
    except (IndexError, ValueError) as e:
        weight <- dict()
        weight_default <- 1.0 / float(len(attrs))
               ENDFUNCTION

        for i in range(len(attrs)):
            weight[attrs[i]] <- weight_default
                                      ENDFUNCTION

        ENDFOR
    RETURN weight
ENDFUNCTION

FUNCTION get_cluster_penalties(virtual_attrs_minimums, attrs, properties):
    keys <- virtual_attrs_minimums.keys()
    len_data <- len(virtual_attrs_minimums[keys[0]])
    target <- [int(val) for val in sys.argv[1].split(",")]
                       ENDFOR
    weight <- [float(val) for val in sys.argv[3].split(",")]
                         ENDFOR
    penalties <- []
    for i in range(len_data):
        cluster_penalty <- 0.0
        for j, attr_ in enumerate(attrs):
            attr_normalized_before <- normalize_attr(min=properties[attr_]["min"],
                                             max=properties[attr_]["max"],
                                             x=target[j])
                              ENDFOR
            attr_normalized_after <- normalize_attr(min=properties[attr_]["min"],
                                             max=properties[attr_]["max"],
                                             x=virtual_attrs_minimums[attr_][i])
            # abs_attr_ <- abs(attr_normalized - target[j])
            abs_attr_ <- abs(attr_normalized_after - attr_normalized_before)
                                                                      ENDFOR
            cluster_penalty += (abs_attr_ * (1.0 - weight[j]))
        ENDFOR
        penalties.append(cluster_penalty)
    ENDFOR
    RETURN penalties
ENDFUNCTION

FUNCTION create_n_cluster_solutions(cluster_children, penalties, attrs, virtual_attrs_minimums):
    threshold <- int(sys.argv[2])
    solutions <- []
    for i in range(len(cluster_children)):
        solution <- {
            "subscribers": len(cluster_children[i]),
            "penalty": penalties[i],
        }
        for attr_ in attrs:
            solution[attr_] <- virtual_attrs_minimums[attr_][i]
        ENDFOR
        IF solution["subscribers"] >= threshold:
            solutions.append(solution)
        ENDIF
    ENDFOR
    RETURN solutions
ENDFUNCTION

FUNCTION create_final_solutions(solutions):
    user_defined <- int(sys.argv[4])
         ENDFUNCTION

    n_solutions <- min(len(solutions), user_defined)
                                           ENDFUNCTION

    final_solutions <- []
    counter <- 0
    for solution in sorted(solutions, key=lambda x: x["penalty"]):
        IF counter = n_solutions:
            break
        ENDIF
        final_solutions.append(solution)
        counter += 1
    ENDFOR
    RETURN final_solutions
ENDFUNCTION

FUNCTION show_final_solutions(final_solutions):
    OUTPUT "\nFinal Solutions:"
    for solution in final_solutions:
        OUTPUT solution
ENDFUNCTION

    ENDFOR
FUNCTION show_precompute_time(n_cluster, start_precompute_time):
    end_precompute_time <- datetime.datetime.now()
    precompute_time <- (end_precompute_time - start_precompute_time)
    OUTPUT ">> Waktu proses Pre-Compute Time {} Cluster : ".format(n_cluster) + str(precompute_time)
ENDFUNCTION

                                                           ENDFOR
FUNCTION main():
    OUTPUT "Process"
    # data <- load_initial_data("datasets/anti_correlated/dataset_30000_3.csv")
    data <- load_initial_data("datasets/independent/dataset_30000_3.csv")
    attrs <- filter(lambda key: key.startswith('attr_'), list(data.keys()))
    target_subs_score <- score_target(sys.argv[1], attrs, data)
    OUTPUT "Subscribers : " + str(target_subs_score)
    properties <- get_properties(attrs, data)
    n_clusters <- [100, 75, 50, 25, 10]
    dummy_time <- datetime.datetime.now()
    mutable_obj <- {
        'sum_running_time': (dummy_time - dummy_time),
        'solutions': []
    }
    for n_cluster in n_clusters:
        FUNCTION execute_clustering():
            start_precompute_time <- datetime.datetime.now()
            virtual_points <- create_virtual_attrs_minimums(n_cluster, data, attrs)
            cluster_children <- get_children(n_cluster, data, attrs, virtual_attrs_minimums=virtual_points)
            show_precompute_time(n_cluster, start_precompute_time=start_precompute_time)
            s_time <- datetime.datetime.now()
            cluster_penalties <- get_cluster_penalties(virtual_points, attrs, properties)
            n_cluster_solutions <- create_n_cluster_solutions(cluster_children=cluster_children,
                                                             penalties=cluster_penalties,
                                                             attrs=attrs,
                                                             virtual_attrs_minimums=virtual_points)
            e_time <- datetime.datetime.now()
            r_time <- e_time - s_time
            mutable_obj['sum_running_time'] += r_time
            mutable_obj['solutions'] += n_cluster_solutions
        ENDFUNCTION

        t <- threading.Thread(target=execute_clustering)
        t.start()
        t.join()
    # total solutions yang memenuhi ekpektasi_subs
    ENDFOR
    solutions <- mutable_obj['solutions']
    sum_running_time <- mutable_obj['sum_running_time']
    OUTPUT '\n'
    OUTPUT 'total virtual yang memenuhi ekspektasi : ' + str(len(solutions))
    # input user solutions yang memenuhi ekspektasi
    start_running_time <- datetime.datetime.now()
    final_solutions <- create_final_solutions(solutions)
    end_running_time <- datetime.datetime.now()
    running_time <- (end_running_time - start_running_time)
    sum_running_time += running_time
    show_final_solutions(final_solutions)
    OUTPUT '\nRunning time (exclude pre compute): {}'.format(str(sum_running_time))
                                                     ENDFOR
    OUTPUT 'Average running time for {} expected solutions: {}'.format(sys.argv[4], str(sum_running_time / int(sys.argv[4])))
                                ENDFOR
    process <- psutil.Process(os.getpid())
    OUTPUT "Memory usage: " + str(mem_usage) + " MB "
ENDFUNCTION

IF __name__ = '__main__':
    main()
