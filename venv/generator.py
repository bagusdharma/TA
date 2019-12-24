import random
from math import ceil

random.seed(122)

d = 10
n = 30000
# n_insert = 100
missing_persentage = 20

data = []
for i in range(n):
    data.append([0]*d)

for i in range(0,n):
    base = random.uniform(0, 1)
    basedim = int(ceil(base / (1.0 / float(d)))) - 1
    data[i][basedim] = random.uniform(0, 1)
    for dim in range(0, d):
        if dim != basedim:
            baseotherdim = 1 - data[i][basedim]
            posneg = random.uniform(0, 1)
            if posneg <= 0.5:
                addsub = -1 * (0.5 - posneg) * 0.2
            else:
                addsub = (posneg - 0.5) * 0.2
            data[i][dim] = baseotherdim + addsub
            if data[i][dim] < 0:
                data[i][dim] = 0.0
            elif data[i][dim] > 1:
                data[i][dim] = 1.0

row = 'id'
for j in range(d):
    row = row + ',d%d' % (j+1)
print(row)
for i in range(n):
    row = '%d'%(i+1)
    for j in range(0,d):
        ran = random.randint(1, 100)
        if ran <= missing_persentage:
            row += '0'
        else:
            row += ',%d'%ceil(data[i][j]*100)
    print(row)


