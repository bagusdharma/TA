

import random
import sys
import csv

try:
    num_of_rows = int(sys.argv[1])
except IndexError:
    num_of_rows = 100000

try:
    num_of_attr = int(sys.argv[2])
except IndexError:
    num_of_attr = 2

res = []
title_row = ["id", "label"]
for i in range(num_of_attr):
    title_row.append("attr_"+str(i))
res.append(title_row)
for i in range(num_of_rows):
    data_row = [i+1, "r-"+str(i+1)]

    decimal1 = random.randint(1, 9999)
    float_point1 = random.random()
    data_row.append(float("%.2f" % (float(decimal1) + float(float_point1))))

    decimal2 = random.randint(1, 9999)
    float_point2 = random.random()
    data_row.append(float("%.2f" % (float(decimal2) + float(float_point2))))

    res.append(data_row)

csvfile = "dataset_test.csv"
with open(csvfile, "w") as output:
    writer = csv.writer(output, lineterminator='\n')
    writer.writerows(res)
