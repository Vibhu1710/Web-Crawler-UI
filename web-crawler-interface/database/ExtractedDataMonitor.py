from beforeRender import getFolderMap
from database.RDSMonitor import getTableMap
from database.LocalDataBaseMonitor import setLastRunRowCount, getRowCount
import pandas as pd
import os
import boto3
from io import StringIO
from datetime import date
import locale


# mention just the folder name path Eg:- C:/Downloads , do not put slash in the end, also use forward slashes '/' in paths
DATA_PATH = r"extracted_data_default_directory"


ACCESS_KEY = ''
SECRET_ACCESS_KEY = ''
S3_BUCKET_NAME = 'analytics-msil-dev'
S3_DUMP_FILE_PATH = 'Interns-2022/updated-scraped-data-repo/'
S3_PIPELINE_FILE_PATH = 'external-data-repo/'


def readCsvFromScrapedData(websiteId):
    return pd.read_csv(returnLocalFilePath(websiteId), dtype='object')

def writeCsvToScrapedData(df, websiteId):
    df.to_csv(returnLocalFilePath(websiteId), index=False)

def returnLocalFilePath(websiteId):
    return DATA_PATH + '/' + websiteId + '.csv'

def returnS3DumpFilePath(websiteId):
    return S3_DUMP_FILE_PATH + websiteId + '.csv'


def returnS3PipelineFilePath(websiteId):
    folderMap = getFolderMap('real')
    print(folderMap)
    pipelineFolder = ''

    for folder in folderMap:
        for file in folderMap[folder]:
            if file['WebsiteId'] == websiteId:
                pipelineFolder = folder
                break

    print('folder: ', pipelineFolder, 'website:', websiteId)

    pipelineFolderFirst = pipelineFolder.replace('_','-')
    return S3_PIPELINE_FILE_PATH + pipelineFolderFirst + '/Inbox_' + pipelineFolder + '/'+ websiteId + '.csv'


# helper function
def commaNewlineReplace(df):
    df = df.replace(',', ';', regex=True)
    df = df.replace('\n', '|', regex=True)
    return df


def appendDataToDataPath(df_row, websiteId):

    df_row = commaNewlineReplace(df_row)

    filePath = returnLocalFilePath(websiteId)
    if os.path.isfile(filePath):
        df_row.to_csv(filePath, mode='a', index=False, header=False)
    else:
        df_row.to_csv(filePath, mode='a', index=False, header=True)



def transferDataToS3(rdsTableName, websiteId):

    df = pd.read_csv(returnLocalFilePath(websiteId), dtype='object')
    df.drop_duplicates(inplace=True)

    tableMap = getTableMap()
    tableColumnNames = tableMap[rdsTableName]

    # format df as per rds table format
    df = pd.DataFrame(df, columns=tableColumnNames)

    # set the website column to websiteId
    if 'website' in list(df.columns.values):
        df['website'] = websiteId
    elif 'Website' in list(df.columns.values):
        df['Website'] = websiteId

    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    # create s3 session
    s3_res = createS3Session()

    # move df to s3 dump folder
    s3_res.Object(S3_BUCKET_NAME, returnS3DumpFilePath(websiteId)).put(Body=csv_buffer.getvalue())

    # move df to s3 pipeline folder
    s3_res.Object(S3_BUCKET_NAME, returnS3PipelineFilePath(websiteId)).put(Body=csv_buffer.getvalue())

    # remove scraped data from local
    removeScrapedFile(websiteId)

    # calculate and set rowCount and lastRun
    rowCount = df.shape[0]
    prevCount = getRowCount(websiteId)
    rowCount = formatRowCount(rowCount, prevCount)

    lastRun = todaysDate()
    setLastRunRowCount(websiteId, lastRun, rowCount)


def createS3Session():
    session = boto3.Session(
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_ACCESS_KEY
    )

    # Returning S3 Resource From the Session.
    return session.resource('s3')


def removeScrapedFile(websiteId):
    # remove Local Scraped File
    os.remove(returnLocalFilePath(websiteId))

def todaysDate():
    today = date.today()
    day = today.day
    month = today.strftime('%B')
    year = today.year
    return str(day) + ' ' + month + " '" + str(year)[-2:]

def numberToCommaSeparatedString(num):
    locale.setlocale(locale.LC_MONETARY, 'en_IN')
    return locale.currency(num, grouping=True)[2:-3]

def formatRowCount(rowCount, prevCount):

    prevCount = prevCount.split()[0].replace(',', '')

    if prevCount.isdigit():
        prevCount = int(prevCount)
    else:
        prevCount = 0

    diff = rowCount - prevCount
    if diff < 0:
        formattedCount = numberToCommaSeparatedString(rowCount) + ' (-' + numberToCommaSeparatedString(abs(rowCount - prevCount)) + ')'
    else:
        formattedCount = numberToCommaSeparatedString(rowCount) + ' (+' + numberToCommaSeparatedString(abs(rowCount - prevCount)) + ')'

    return formattedCount
