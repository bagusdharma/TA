from numpy.random import choice
import sys
import csv


PREFERENCE_VALUE_WEIGHT = 0.55
OTHER_VALUE_WEIGHT = 1.0 - PREFERENCE_VALUE_WEIGHT

try:
    num_of_rows = int(sys.argv[1])
except IndexError:
    num_of_rows = 100
attribute_properties = sys.argv[2:]
attribute = list()
for attr_prop in attribute_properties:
    attr_item = attr_prop.split(',')
    attr_temp = dict()
    attr_temp["label"] = attr_item[0]
    attr_temp["min"] = int(attr_item[1])
    attr_temp["max"] = int(attr_item[2])
    attr_temp["increment"] = int(attr_item[3])
    try:
        prefered_value = attr_item[4].split('/')
        weight = PREFERENCE_VALUE_WEIGHT/float(len(prefered_value))
        attr_temp["preference"] = map(int, prefered_value)
        attr_temp["preference_weight"] = weight
    except IndexError:
        attr_temp["preference"] = list()
        attr_temp["preference_weight"] = 0.0
    attribute.append(attr_temp)
res = []
title_row = ["id", "label"]
for attr in attribute:
    title_row.append(attr["label"])
res.append(title_row)
for i in range(num_of_rows):
    data_row = [i+1, "r-"+str(i+1)]
    for attr in attribute:
        min = attr["min"]
        max = attr["max"]
        increment = attr["increment"]
        cand = range(min, max+1, increment)
        weight = list()
        if len(attr["preference"]) > 0:
            default_weight = OTHER_VALUE_WEIGHT/float(len(cand)-len(attr["preference"]))
        else:
            default_weight = 1.0/float(len(cand))
        for c in cand:
            if c in attr["preference"]:
                weight.append(attr["preference_weight"])
            else:
                weight.append(default_weight)
        data_row.append(choice(cand, p=weight))
    res.append(data_row)
csvfile = "dataset_real.csv"
with open(csvfile, "w") as output:
    writer = csv.writer(output, lineterminator='\n')
    writer.writerows(res)
