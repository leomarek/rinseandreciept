import re
import lshashpy3 as ls
import os, json
import datetime
from fuzzywuzzy import fuzz
import dateutil.parser as parser
from fuzzywuzzy import process
from mpl_toolkits import mplot3d
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# creat vendor id map
vendorMap =[]

path_to_json = os.getcwd()
json_files = [os.getcwd()+"\lshashpy3\\test_results\\"+pos_json for pos_json in os.listdir(os.getcwd()+"\lshashpy3\\test_results") if pos_json.endswith('.json')]
# parse recieptData as python dictionary:
recieptData = []
for recieptDataJson in json_files:
    file = open(recieptDataJson)
    recieptData.append(json.loads(file.read()))

# create 16-bit hashes for input data of 3 dimensions:
lsh = ls.LSHash(8, 3)

def getdatapoint(data):
    #init weights
    id = data["documentid"]
    vid = -1
    #do total
    try:
        total = data["amount"]
        #total = float(re.sub(r'[^0-9,.]', '', data["amount"]))
        
    except:
        total = '$53.0'
    #do date
    try:    
        dateInfo = data["date"]
        dt_time = parser.parse(dateInfo).date()
        date = dt_time
    except:
        date = ""

    #do vendor
    if not "vendor_name" in data.keys():
        vendor = ""
    else:
        vendor = data["vendor_name"]

    if not "vendor_address" in data.keys():
        address = ""
    else:
        address = data["vendor_address"]

    #for compare in vendorMap:
        #vcompare = fuzz.token_sort_ratio(compare[0],vendor)
        #acompare = fuzz.token_sort_ratio(compare[1],address)
        #if (vcompare>30):
        #    vid = vendorMap.index(compare)
        #    break
    if vid == -1:
        vendorMap.append((vendor,address))
        vid = vendorMap.index((vendor,address))
    return [str(total),str(date),address,vendor],id
    
df = pd.read_csv(os.getcwd()+"\lshashpy3\\test_transactions.csv")

# index each
csvlist = []
for index, row in df.iterrows():
    amount = str(row['amount'])
    vendor = row['vendor_name']
    address = row['vendor_address']
    date = row['date']
    dp = getdatapoint({"vendor_name":vendor,"date":date,"vendor_address":address,"amount":amount, "documentid":row['documentid']})
    csvlist.append((""+str(dp[0][0])+str(dp[0][1])+str(dp[0][2])+str(dp[0][3]),dp[1]))


matchcount = 0
misses = 0

dplist = []
for dataPoint in recieptData:
    #print(dataPoint)
    dp = getdatapoint(dataPoint)
    dplist.append((""+str(dp[0][0])+str(dp[0][1])+str(dp[0][2])+str(dp[0][3]),dp[1]))
matches = {}

# for dp in dplist:
#     maxval = 0
#     for csv in csvlist:
#         if(fuzz.ratio(dp[0],csv[0])>=maxval):
#             maxval = fuzz.ratio(dp[0],csv[0])
#             if maxval>93:
#                 matches[dp] = csv

for dp in dplist:
    if dp not in matches:
        maxval = 0
        for csv in csvlist:
            if(fuzz.ratio(dp[0],csv[0])>=maxval):
                maxval = fuzz.ratio(dp[0],csv[0])
                matches[dp] = csv
        

for entry in matches.keys():
    if entry[1]==matches[entry][1]:
        matchcount+=1
    else:
        # print(matches[entry])
        # print(entry)
        # print("------")
        misses+=1
print(misses)
print(matchcount)
#print(matches)
print("success rate:"+str(100*matchcount/(matchcount+misses))+"%")

# testjson = '{"documentid": "00d0472780579","paymentid": "00p0878907338","amount": 7.8,"date": "2018-4-4","vendor_name": "RESTTORAN WAN SHENG","vendor_address": "NO.2, JALAN TEMENGUNG 19/9, SEKSYEM 9, BANDAR MAHKOTA CHERAS, 43200CHERAS, SELANGOR"}'
# testjsondict = json.loads(testjson)
# #query a data point
# print(testjsondict)
# print()
# print(getdatapoint(testjsondict))
# print()
# nn = lsh.query(getdatapoint(testjsondict)[0], num_results=1, distance_func="euclidean")
# print(nn)

