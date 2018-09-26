# Objective: This python script is used to retrieve company announcement from IDX website
#            Please use the this script for your first time web scraping or when new ticker added


import requests
import json
import csv
import pandas as pd


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
    dataframe = pd.read_csv(path, sep=",", usecols=['id', 'ticker', 'title', 'date', 'pdfID', 'filename', 'filePath'])
    return dataframe


# Function 4: Retrieve all announcement with specific ticker
def Idx_spider(Ticker, TempPath):
    # Get the json data of specify ticker from IDX website
    req = requests.get('http://www.idx.co.id/umbraco/Surface/ListedCompany/GetAnnouncement?kodeEmiten=' + Ticker + '&keyword=&indexFrom=0&pageSize=9999&dateFrom=&dateTo')
    jsonObject = json.loads(req.text)

    # Output Dataset to csv file (Announcement and Attachment)
    with open(TempPath, "a", newline='') as csvFile:
        writer = csv.writer(csvFile, delimiter=",")
        i = 0

        # For each annonucement
        while i < len(jsonObject['Replies']):
            announcement = jsonObject['Replies'][i]['pengumuman']

            if len(jsonObject['Replies'][i]['attachments']) > 1:
                # If the announcement have attachment
                for attachment in jsonObject['Replies'][i]['attachments']:
                    isAttm = attachment.get('IsAttachment')
                    if isAttm:
                        announcementId = str(announcement.get('Id'))
                        ticker = announcement.get('Kode_Emiten').strip()
                        title = announcement.get('JudulPengumuman')
                        date = announcement.get('TglPengumuman')
                        attachmentId = attachment.get('Id')
                        fileName = attachment.get('OriginalFilename')
                        filePath = attachment.get('FullSavePath')

                        # Write into csv
                        writer.writerow([announcementId, ticker, title, date, attachmentId, fileName, filePath])
            else:
                # If the annonucement have no attachment
                announcementId = str(announcement.get('Id'))
                ticker = announcement.get('Kode_Emiten').strip()
                title = announcement.get('JudulPengumuman')
                date = announcement.get('TglPengumuman')
                writer.writerow([announcementId, ticker, title, date])

            i += 1


# Function 4: Detect new change in current dataframe compare to previous
def AntiJoin(current, previous):

    diff = set(current.id).difference(previous.id)
    print(current.id.isin(diff))


tempPath = "\\\\fileserver2\\bloomberg Share$\\Adam\\Python Script\\py\\temp_test.csv"
tickerListPath = "\\\\fileserver2\\bloomberg Share$\\Adam\\Python Script\\TickerList.csv"
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
