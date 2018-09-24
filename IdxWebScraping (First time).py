# Objective: This python script is used to retrieve company announcement from IDX website
#            Please use the this script for your first time web scraping or when new ticker added
#
# Workflow: 1. Create new csv for output the result
#           2. Import list of ticker from csv
#           3. Retrieve json data from IDX by each ticker
#           4. Convert json to dataframe format and output the result to the new csv
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


# Function 1: create new csv file for output result
def CreateCsv(OutputFilePath):
    with open(OutputFilePath, "w", newline='') as csvFile:
        writer = csv.writer(csvFile, delimiter=",")
        writer.writerow(['id', 'ticker', 'title', 'date', 'pdfID', 'filename', 'filePath'])


# Function 2: import ticker
def ReadTicker(TickerListPath):
    with open(TickerListPath, "r", newline='') as csvFile:
        reader = csv.reader(csvFile)
        TickerList = list(reader)

    return TickerList


# Function 3: retrieve all announcement for specific ticker
def Idx_spider(Ticker, OutputFilePath):
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
    with open(OutputFilePath, "a", newline='') as csvFile:
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
                        ticker_trim = ticker.strip()                        # Remove spacebar in the ticker
                        title = ann.get('JudulPengumuman', None)            # Title
                        date = ann.get('TglPengumuman', None)               # Date
                        attmId = attm.get('Id', None)                       # Attachment id
                        attmFilename = attm.get('OriginalFilename', None)   # File name
                        attmPath = attm.get('FullSavePath', None)           # File path

                        # Output a row of result the csv
                        writer.writerow([annId, ticker_trim, title, date, attmId, attmFilename, attmPath])
            else:
                # If the annonucement have no attachment
                annId = str(ann.get('Id', None))
                ticker = ann.get('Kode_Emiten', None)
                ticker_trim = ticker.strip()
                title = ann.get('JudulPengumuman', None)
                date = ann.get('TglPengumuman', None)

                # Output a row of result the csv
                writer.writerow([annId, ticker_trim, title, date])

            i += 1


# File path to create csv for output result
outputFilePath = "File Location to output result"
# File path to import list of ticker
tickerListPath = "File that contains ticker

# Create new csv file to output result
CreateCsv(outputFilePath)

# Import ticker
tickerList = ReadTicker(tickerListPath)

# Retrieve info from IDX website by each ticker
for ticker in tickerList:
    Idx_spider(str(ticker[0]), outputFilePath)
    print(ticker[0])
