import random
import sys
import json
import csv

MAX_VALUE = 10000
DISTANCE = 1
try:
    num_of_rows = int(sys.argv[1])
except IndexError:
    num_of_rows = 100
try:
    num_of_cols = int(sys.argv[2])
except IndexError:
    num_of_cols = 2
with open('datasets/attribute2.json') as f:
    attribute = list(json.load(f))
res = list()
res.append(attribute[0:2+num_of_cols])
attribute_value = attribute[2:2+num_of_cols]
for idx in range(0,num_of_rows):
    res_temp = [idx+1, "R"+str(idx+1)]

    base = random.randint(0,MAX_VALUE)
    basedim = random.randint(0,num_of_cols-1)

    for attr in attribute_value:
        if attr == attribute_value[basedim]:
            res_temp.append(base)
        else:
            # valueotherdim = MAX_VALUE - base + random.randint(- DISTANCE,DISTANCE)
            valueotherdim = MAX_VALUE - ((base + random.randint(- DISTANCE, DISTANCE)) * 0.2)
            if valueotherdim < 0:
                res_temp.append(0)
            elif valueotherdim > MAX_VALUE:
                res_temp.append(MAX_VALUE)
            else:
                res_temp.append(valueotherdim)
    res.append(res_temp)
with open("datasets/anti_correlated/dataset_"+str(num_of_rows)+"_"+str(num_of_cols)+".csv", "w") as output:
    writer = csv.writer(output, lineterminator='\n')
    writer.writerows(res)
