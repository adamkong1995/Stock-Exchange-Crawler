# Objective: This python script is used to retrieve company announcement from IDX website
#               and send email alert to users when new announcement was found

import requests
import json
import csv
import pandas as pd
import os
import win32com.client as win32
from bs4 import BeautifulSoup


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
    diff = current.announcementId.isin(diff)
    diff = diff.to_frame('isDiff')
    return diff


# Function 5: send a table of new announcement to user
def SendEmail(newResult):
    To = "test@test.com"   # Feel free to change

    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = To
    mail.Subject = "Listed Company Information Alert (IDX)"
    mail.HTMLBody = """\
    <html>
    <head>
    <style>
    table {
        border-collapse: collapse;
        font-family:"Courier New", Courier, monospace;
        font-size:60%
    }
    </style>
    </head>

    <body>
        <p>Listed company information alert (IDX):<br>
        <br>
        </p>
    """

    newResult = newResult[['ticker', 'title', 'date', 'filePath']]
    newResult.rename(columns={list(newResult)[0]: 'Ticker', list(newResult)[1]: 'Announcement title', list(newResult)[2]: 'date', list(newResult)[3]: 'Attachment'}, inplace=True)
    newResult.date.loc[:] = newResult.date.str[:10]  # date formatting
    htmlContent = newResult.to_html(index=False, escape=False).replace('<table border="1" class="dataframe">', '<table>').replace('<th>', '<th style = "background-color: #5C6067; color: #61A8FA; border-collapse: collapse;">')
    htmlContent = addHyperlink(htmlContent)
    mail.HTMLBody = mail.HTMLBody + htmlContent

    mail.HTMLBody = mail.HTMLBody + """
    </body>
    </html>
    """
    mail.Send()


# Function 6: add hyperlink in html table
def addHyperlink(html):
    html = BeautifulSoup(html, "html.parser")
    rows = html.tbody.find_all("tr")
    for row in rows:
        for cell in row:
            if "http" in cell.string:
                link = cell.string
                cell.string = ""
                newTag = html.new_tag("a", href=link)
                cell.append(newTag)
                cell.a.string = link
                
    return str(html)


# File path to import list of ticker
tickerListPath = 'TickerList.csv'
tickerList = ReadTicker(tickerListPath)
pd.set_option('display.max_colwidth', -1)

# File path of csv to contain web scraping result
resultPath = 'result.csv'

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
    difference = AntiJoin(result, previousResult)

    result = pd.merge(result, difference, left_index=True, right_index=True)
    newResult = result.query('isDiff==True')

    # if new announcement found
    if len(newResult.index) > 0:
        SendEmail(newResult)

result.to_csv(resultPath, sep=',')
