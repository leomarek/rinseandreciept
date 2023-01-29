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
import Levenshtein as lv

# creat vendor id map
#ref = {"amount": "RM152.00", "date": "27/06/2018", "vendor_name": "OCEAN LC PACKAGING ENTERPRISE", "vendor_address": "41-1, JLN RADIN ANUM 2, SRI PETALING, 57000 KUALA LUMPUR.", "documentid": "00d0715617779"}

fieldWeights = [1,1,1,1]

path_to_json = os.getcwd()
json_files = [os.getcwd()+"\lshashpy3\\test_results\\"+pos_json for pos_json in os.listdir(os.getcwd()+"\lshashpy3\\test_results") if pos_json.endswith('.json')]
# parse recieptData as python dictionary:
recieptData = []
for recieptDataJson in json_files:
    file = open(recieptDataJson)
    recieptData.append(json.loads(file.read()))

# create 6-bit hashes for input data of 3 dimensions:
lsh = ls.LSHash(6, 4)

def getdatapoint(reference, data):
    reference = reference
    #init weights
    id = data["documentid"]

    if not "total" in data.keys():
        total = ""
    else:
        total = data["total"]

    #do date
    try:    
        dateInfo = data["date"]
        dt_time = parser.parse(dateInfo).date()
        date = str(dt_time)
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

    addressdist = lv.ratio(reference["vendor_address"],address)*fieldWeights[3]
    venddist = lv.ratio(reference["vendor_name"],vendor)*fieldWeights[2]
    datedist = lv.ratio(reference["date"],date)*fieldWeights[1]
    amountdist = lv.ratio(reference["amount"],total)*fieldWeights[0]

    return [amountdist,datedist,venddist,addressdist], id

def run(reference):
    df = pd.read_csv(os.getcwd()+"\lshashpy3\\test_transactions.csv")

    # index each
    for index, row in df.iterrows():
        amount = str(row['amount'])
        vendor = row['vendor_name']
        address = row['vendor_address']
        date = row['date']
        dp = getdatapoint(reference,{"vendor_name":vendor,"date":date,"vendor_address":address,"amount":amount, "documentid":row['documentid']})
        # print(dataPoint)
        # print(type(dataPoint))
        #data is [total,date,vId], extra data is docid
        lsh.index(dp[0],extra_data=dp[1])
        # print(dp)
        # print()


    matches = 0
    misses = 0

    for dataPoint in recieptData:
        #print(dp[0])
        dp = getdatapoint(reference,dataPoint)
        match = lsh.query(dp[0], num_results=1, distance_func="l1norm")
        if match!=[] and match[0][0][1] == dataPoint['documentid']:
            matches+=1
        else:
            misses+=1
    print(misses)
    print(matches)
    print("success rate:"+str(matches/(matches+misses)))
    return(matches/(matches+misses))

reference = {"vendor_name":"HSJASJAHCOKMVGEJAONWAUD","date":"12898367833","vendor_address":"12761 HAJVDCCKAUWGXYJKAEUG 2981782","amount":"RM18.46$", "documentid":""}
score = run(reference)


# df = pd.read_csv(os.getcwd()+"\lshashpy3\\test_transactions.csv")
#     # index each
# best = (0.0, None)
# for index, row in df.iterrows():

#     amount = str(row['amount'])
#     vendor = row['vendor_name']
#     address = row['vendor_address']
#     date = row['date']
#     reference = {"vendor_name":vendor,"date":date,"vendor_address":address,"amount":amount, "documentid":row['documentid']}
#     score = run(reference)
#     if score>=best[0]:
#         best = (score, reference)


# testjson = '{"documentid": "00d0472780579","paymentid": "00p0878907338","amount": 7.8,"date": "2018-4-4","vendor_name": "RESTTORAN WAN SHENG","vendor_address": "NO.2, JALAN TEMENGUNG 19/9, SEKSYEM 9, BANDAR MAHKOTA CHERAS, 43200CHERAS, SELANGOR"}'
# testjsondict = json.loads(testjson)
# #query a data point
# print(testjsondict)
# print()
# print(getdatapoint(testjsondict))
# print()
# nn = lsh.query(getdatapoint(testjsondict)[0], num_results=1, distance_func="euclidean")
# print(nn)

