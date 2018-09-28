# Objective: This python script is used to retrieve company announcement from IDX website
#               and send email alert to users when new announcement was found

import requests
import json
import csv
import pandas as pd
import os


# Function 1: import ticker list
def ReadTicker(tickerListPath):
    tickerList = []
    with open(tickerListPath, "r", newline='') as csvFile:
        reader = csv.reader(csvFile)
        for row in reader:
            tickerList.extend(row)

    return tickerList


# Function 2: Retrieve all announcement with certain ticker
def Idx_spider(ticker):
    req = requests.get('http://www.idx.co.id/umbraco/Surface/ListedCompany/GetAnnouncement?kodeEmiten=' + ticker + '&keyword=&indexFrom=0&pageSize=9999&dateFrom=&dateTo')
    jsonObject = json.loads(req.text)

    data_list = []

    # For each annonucement
    for replies in jsonObject['Replies']:
        announcement = replies['pengumuman']
        announcementId = announcement.get('Id')
        ticker = announcement.get('Kode_Emiten').strip()
        title = announcement.get('JudulPengumuman')
        date = announcement.get('TglPengumuman')

        for attachment in replies['attachments']:
            if len(replies['attachments']) == 1:     # Case when no attachment in the announcement
                data_list.append([announcementId, ticker, title, date])
            elif attachment.get('IsAttachment'):
                attachmentId = attachment.get('Id')
                fileName = attachment.get('OriginalFilename')
                filePath = attachment.get('FullSavePath')

                data_list.append([announcementId, ticker, title, date, attachmentId, fileName, filePath])

    return data_list


# Function 3: import csv file to dataframe
def ReadCsv(path, headers):
    dataframe = pd.read_csv(path, sep=",", usecols=headers)
    return dataframe


# Function 4: Detect new announcement
def AntiJoin(current, previous):

    diff = set(current.announcementId).difference(previous.announcementId)
    print(current.announcementId.isin(diff))


# File path to import list of ticker
tickerListPath = '\\\\fileserver2\\bloomberg Share$\\Adam\\Python Script\\TickerList.csv'
tickerList = ReadTicker(tickerListPath)

# File path of csv to contain web scraping result
resultPath = '\\\\fileserver2\\bloomberg Share$\\Adam\\Python Script\\py\\result.csv'

# Create list to contain web scraping result
dataList = []

for ticker in tickerList:
    dataList.extend(Idx_spider(str(ticker)))
    print(ticker)

# Convert list to dataframe
headers = ['announcementId', 'ticker', 'title', 'date', 'attachmentId', 'fileName', 'filePath']
result = pd.DataFrame.from_records(dataList, columns=headers)

# Check if 'result.csv' is already existed
if (os.path.isfile(resultPath)):
    previousResult = ReadCsv(resultPath, headers)
    AntiJoin(result, previousResult)

    ###### Function to import email list ######
    ###### Function to send email alert ######

    result.to_csv(resultPath, sep=',')
else:
    result.to_csv(resultPath, sep=',')
    print('not exist')
