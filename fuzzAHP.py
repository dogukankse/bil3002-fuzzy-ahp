# coding: utf-8
import numpy as np
file_path_1 = "./Wang et al_2008.prj"
file_path_2 = "./Tyagi et al_2017.prj"



#parse işlemleri başladı
file_text = []
with open(file_path_1) as file:
    file_text = list(map(lambda x: x.replace("\n",""), file.readlines()))


altenative_count = int(file_text[0])
altenative_names = []
for line in file_text[1:altenative_count+1]:
    altenative_names.append(line)
last_index = altenative_count+1


lines = file_text[altenative_count+1:]
title_indexes = []
for index,line in enumerate(lines):
    if line.count(";") == 1:
        title_indexes.append(index)
title_indexes.append(len(lines))        
#parse işlemleri bitti


# In[57]:


#dosyadan tüm matrisleri okur
matrixes = []
for index,i in enumerate(title_indexes):
    if i > 0:
        matrixes.append(lines[title_indexes[index-1]:i])   
for matrix in matrixes:
    for index,elm in enumerate(matrix):
        if elm.count(";") > 1:
            matrix[index] = list(map(lambda x: [float(i) for i in list(x.split(" "))],elm.split(";")))


# In[58]:


#dosyadan okunan matrisleri gruplandırır
matrix_groups = []
for index,matrix in enumerate(matrixes):
    if index == 0:
        continue
    if int(matrix[0].split(";")[1]) > 0:    
        t = matrixes[index:index + int(matrix[0].split(";")[1])+1]
        matrix_groups.append(t)


#üçgensel üyeliklere sahip matrisin verilen satır toplamını alır
def sumTriRow(row,index):
    s = 0
    for i in row:
        s= s+i[index]
    return s

#matrisin transpozunu alır
def transpose(l):
    return list(map(list, zip(*l)))


#verilen matrisin tüm satır roplamını alır (RSi)
def sumTriRows(matrix):
    srows = []
    for row in matrix:
        r = []
        for i in range(3):
            r.append(sumTriRow(row,i))
        srows.append(r)
    return srows


#listedeki tüm elemanları toplar
def sumL(l):
    s = 0;
    for i in l:
        s = s + i
    return s

#matrisin verilen index harici satır toplamını alır
def sumTriRowsWithoutIndex(matrix,lmu,withoutindex):
    srows = []
    for index,row in enumerate(matrix):
        if index == withoutindex:
            continue
        srows.append(sumTriRow(row,lmu))
    return sumL(srows)


#verilen üst ve alt matrislere göre ağırlıklar hesaplanır
def calcPriorityWeight(parent_weight,childs_weights):
    kk =[]
    for i in childs_weights:
        k =0
        for j_index,j in enumerate(i):
            k+=(i[j_index]*parent_weight[j_index])
        kk.append(k)
        k=0
    return kk


#amaç matrisini döndürür
def aim():
    return matrixes[0][1:]


#verilen matrisin Si'lerini hesaplar
def calcSi(matrix):
    rsi = sumTriRows(matrix)
    calc = []
    for index,i in enumerate(rsi):
        c = []
        for jindex,s in enumerate(i):
            if jindex == 0:
                #print(s,sumTriRowsWithoutIndex(a,2,index))
                v = s/(s+sumTriRowsWithoutIndex(matrix,2,index))
                c.append(v)
            elif jindex == 1:
                #print(s,sumTriRowsWithoutIndex(a,1,index))
                v = s/(s+sumTriRowsWithoutIndex(matrix,1,index))
                c.append(v)
            elif jindex == 2:
                #print(s,sumTriRowsWithoutIndex(a,0,index))
                v = s/(s+sumTriRowsWithoutIndex(matrix,0,index))
                c.append(v)
             #print(s/(s+sumTriRowsWithoutIndex(a,0,index)))
        calc.append(c)
    return calc

#verilen iki matrisi karşılaştırır
def calcW(A,B):
    if A[1] >= B[1]:
        return 1
    elif B[0] <= A[2]:
        return (A[2] - B[0])/((A[2]-A[1])+(B[1]-B[0]))
    else:
        return 0

#ağırlıkları normalize eder
def normalize(l):
    s = sumL(l)
    n = []
    for i in l:
        n.append(i/s)
    return n

#karılaştırma vektörlerinde minleri seçerek ve değerler normalize edilerek ağırlık vektörleri oluşturulur
def calcAllW(matrix):
    si=calcSi(matrix)
    calc = []
    for i in range(len(si)):
        c = []
        for j in range(len(si)):
            if i != j:
                c.append(calcW(si[i],si[j]))
        calc.append(min(c))
    calc = normalize(calc)
    return calc

#tüm matrisler için ağırlıklar hesaplanır
matrixes_weighted = {}
for matrix in matrixes:
    k = calcAllW(matrix[1:])
    matrixes_weighted[matrix[0]] = k[0]

#alt matrisler alınır
for key,value in matrixes_weighted.items():
    if key.split(";")[1] == '0':
        matrixes_weighted[key] = matrixes_weighted[key]


#alt matrisler ile üst matrislerin ağırlıkları arasında gerekli işlemler yapılarak
#sonuç ağırlıklar bulunur
priority_weights = []
for matrix_group in matrix_groups:
    merged = []
    for matrix in matrix_group:
        k = calcAllW(matrix[1:])
        merged.append(k)
    f = merged[0]
    del merged[0]
    merged = transpose(merged)
    kk = calcPriorityWeight(f,merged)
    priority_weights.append(kk)  


priority_weights = transpose(priority_weights)

aim_weights = calcAllW(aim())

print(calcPriorityWeight(aim_weights,priority_weights))


