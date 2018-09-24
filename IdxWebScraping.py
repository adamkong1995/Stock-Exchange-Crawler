# Objective: This python script is used to retrieve company announcement from IDX website
#            Please use the this script for your first time web scraping or when new ticker added
#
# Workflow: 1. Create temp csv for output the result
#           2. Import list of ticker from csv
#           3. Retrieve json data from IDX by each ticker
#           4. Convert json to dataframe format and output the result to the temp csv
#           5. Impoet previous web scraping to  a dataframe
#           6. Import current web scraping to a dataframe
#           7. Anti join two dataframe to detect any change
#
# Explanation of IDX website json structure:
#           type(jsonObject)                                 # dict
#           type(jsonObject['Replies'])                      # list
#           type(jsonObject['Replies'][i])                   # dict
#           type(jsonObject['Replies'][i]['pengumuman'])     # dict
#           type(jsonObject['Replies'][i]['attachments'])    # list


# Package for web crawler
import requests
from urllib.request import urlopen, Request

# Package for handling json data
import json
import csv

# Package for data manipulating
import pandas as pd
import numpy as np


# Function 1: create temp csv file for output result
def CreateTempCsv(TempPath):
    with open(TempPath, "w", newline='') as csvFile:
        writer = csv.writer(csvFile, delimiter=",")
        writer.writerow(['id', 'ticker', 'title', 'date', 'pdfID', 'filename', 'filePath'])


# Function 2: import ticker
def ReadTicker(TickerListPath):
    with open(TickerListPath, "r", newline='') as csvFile:
        reader = csv.reader(csvFile)
        TickerList = list(reader)

    return TickerList


# Function 3: import csv file to dataframe
def ReadCsv(path):
    df = pd.read_csv(path, sep=",", usecols=['id', 'ticker', 'title', 'date', 'pdfID', 'filename', 'filePath'])
    return df


# Function 3: Retrieve all announcement with specific ticker
def Idx_spider(Ticker, TempPath):
    # Get the number of announcement
    req = Request('http://www.idx.co.id/umbraco/Surface/ListedCompany/GetAnnouncement?kodeEmiten=' + Ticker + '&keyword=&indexFrom=0&pageSize=1&dateFrom=&dateTo', headers={'User-Agent': 'Mozilla/5.0'})
    html = urlopen(req).read()
    jsonObject = json.loads(html)
    pageNumber = str(jsonObject['ResultCount'])

    # Request HTTP website (With all announcement)
    req = Request('http://www.idx.co.id/umbraco/Surface/ListedCompany/GetAnnouncement?kodeEmiten=' + Ticker + '&keyword=&indexFrom=0&pageSize=' + pageNumber + '&dateFrom=&dateTo', headers={'User-Agent': 'Mozilla/5.0'})
    html = urlopen(req).read()
    jsonObject = json.loads(html)

    # Output Dataset to csv file (Announcement and Attachment)
    with open(TempPath, "a", newline='') as csvFile:
        writer = csv.writer(csvFile, delimiter=",")
        i = 0

        # For each annonucement
        while i < len(jsonObject['Replies']):
            ann = jsonObject['Replies'][i]['pengumuman']

            if len(jsonObject['Replies'][i]['attachments']) > 1:
                # If the announcement have attachment
                for attm in jsonObject['Replies'][i]['attachments']:
                    isAttm = attm.get('IsAttachment', None)
                    if isAttm:
                        annId = str(ann.get('Id',None))                     # Announcement Id
                        ticker = ann.get('Kode_Emiten', None)               # Ticker
                        ticker_trim = ticker.strip()
                        title = ann.get('JudulPengumuman', None)            # Title
                        date = ann.get('TglPengumuman', None)               # Date
                        attmId = attm.get('Id', None)                       # Attachment id
                        attmFilename = attm.get('OriginalFilename', None)   # File name
                        attmPath = attm.get('FullSavePath', None)           # File path

                        # Write into csv
                        writer.writerow([annId, ticker_trim, title, date, attmId, attmFilename, attmPath])
            else:
                # If the annonucement have no attachment
                annId = str(ann.get('Id', None))            # Announcement Id
                ticker = ann.get('Kode_Emiten', None)       # Ticker
                ticker_trim = ticker.strip()
                title = ann.get('JudulPengumuman', None)    # Title
                date = ann.get('TglPengumuman', None)       # Date
                writer.writerow([annId, ticker_trim, title, date])

            i += 1


# Function 4: Detect new change in current dataframe compare to previous
def AntiJoin(current, previous):

    diff = set(current.id).difference(previous.id)
    print(current.id.isin(diff))


# Temp file to store web scraping in this time
tempPath = "\\\\fileserver2\\bloomberg Share$\\Adam\\Python Script\\py\\temp_test.csv"
# File path to import list of ticker
tickerListPath = "\\\\fileserver2\\bloomberg Share$\\Adam\\Python Script\\TickerList.csv"
# File path of last time web scraping result
previousResultPath = "\\\\fileserver2\\bloomberg Share$\\Adam\\Python Script\\py\\previousResult.csv"

# Create temp csv to store the data
CreateTempCsv(tempPath)

# Import ticker
tickerList = ReadTicker(tickerListPath)

# Retrieve info from IDX website by each ticker
for ticker in tickerList:
    Idx_spider(str(ticker[0]), tempPath)
    print(ticker[0])

# Import previous and current web scraping result to dataframe
previousResult = ReadCsv(previousResultPath)
currentResult = ReadCsv(tempPath)

# Anti join two dataframe to detect new announcement
AntiJoin(currentResult, previousResult)
