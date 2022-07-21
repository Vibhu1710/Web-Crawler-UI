import sqlite3
import time
from threading import Lock


sqliteConnection = sqlite3.connect(r'database/LocalDataBase.db', check_same_thread=False)
cursor = sqliteConnection.cursor()
lock = Lock()

# Condition Column Possible Values :
# -1 : Error
# 0 : Normal (Running or Still)
# 1 : Completed

# Change Column Possible Values :
# 0 : No Change
# 1 : Change Happened


# General LocalData Functions
def getWebsiteData(websiteId):
    sqlite_select_Query = f'''SELECT * FROM LocalData where WebsiteId='{websiteId}';'''
    lock.acquire(True)
    cursor.execute(sqlite_select_Query)
    data = cursor.fetchall()
    lock.release()
    return data

def getIncrement(websiteId):
    sqlite_select_Query = f'''SELECT Increment FROM LocalData where WebsiteId='{websiteId}';'''
    lock.acquire(True)
    cursor.execute(sqlite_select_Query)
    data = cursor.fetchall()[0][0]
    lock.release()
    return data

def getRowCount(websiteId):
    sqlite_select_Query = f'''SELECT RowCount FROM LocalData where WebsiteId='{websiteId}';'''
    lock.acquire(True)
    cursor.execute(sqlite_select_Query)
    data = cursor.fetchall()[0][0]
    lock.release()
    return data

def setLastRunRowCount(websiteId, lastRun, rowCount):
    sqlite_update_Query = f'''UPDATE LocalData
        SET LastRun="{lastRun}", RowCount='{rowCount}'
        WHERE WebsiteId = '{websiteId}';'''
    lock.acquire(True)
    cursor.execute(sqlite_update_Query)
    lock.release()
    sqliteConnection.commit()



def createNewWebsiteData(websiteId):
    sqlite_select_Query = f'''INSERT INTO LocalData
        VALUES ('{websiteId}', '-', '-', '-', 0, '-', '-', 0, 0);'''
    lock.acquire(True)
    cursor.execute(sqlite_select_Query)
    cursor.fetchall()
    lock.release()




# Functions for handling GET update Requests
def fetchWhenChange(websiteId):
    sqlite_select_Query = f'''SELECT Change FROM LocalData where WebsiteId='{websiteId}';'''
    print("in fetchWhenChange "+websiteId)
    # Wait till Change is 0
    while 1:
        lock.acquire(True)
        cursor.execute(sqlite_select_Query)
        change = cursor.fetchall()[0][0]
        lock.release()
        if change == 1:
            break
        time.sleep(3)

    print('change found')
    # Change has been made. Return the new Data
    sqlite_select_Query = f'''SELECT State,City,Pin,Increment,Condition FROM LocalData where WebsiteId='{websiteId}';'''
    lock.acquire(True)
    cursor.execute(sqlite_select_Query)
    websiteLogData = cursor.fetchall()[0]
    lock.release()
    # set Change to 0 before leaving
    resetLocalData(websiteId)
    print('reset done')
    return websiteLogData


def setLocalData(websiteId, state='-', city='-', pin='-', increment=-1):
    print("in setLocalData "+websiteId)
    sqlite_update_Query = f'''UPDATE LocalData
    SET State = '{state}', City = '{city}', Pin = '{pin}', Increment = {increment}, Change = 1
    WHERE WebsiteId = '{websiteId}';'''
    lock.acquire(True)
    cursor.execute(sqlite_update_Query)
    sqliteConnection.commit()
    lock.release()
    return -100  # for skip variable

def resetLocalData(websiteId):
    print("in resetLocalData "+websiteId)
    sqlite_update_Query = f'''UPDATE LocalData
    SET Change = 0
    WHERE WebsiteId = '{websiteId}';'''

    lock.acquire(True)
    cursor.execute(sqlite_update_Query)
    sqliteConnection.commit()
    lock.release()


def reportOnCompletion(websiteId):
    print("in reportOnCompletion")

    # Need to add Last Run Calculation field
    # Maybe even the RowCount field

    sqlite_update_Query = f'''UPDATE LocalData
        SET State = '-', City = '-', Pin = '-', Increment = 0, Condition = 1, Change = 1
        WHERE WebsiteId = '{websiteId}';'''
    lock.acquire(True)
    cursor.execute(sqlite_update_Query)
    sqliteConnection.commit()
    lock.release()


def reportOnError(websiteId):
    print('in reportOnError')
    sqlite_update_Query = f'''UPDATE LocalData
            SET Condition = -1, Change = 1
            WHERE WebsiteId = '{websiteId}';'''

    lock.acquire(True)
    cursor.execute(sqlite_update_Query)
    sqliteConnection.commit()
    lock.release()


def cleanLocalDataOnStart(websiteId):
    print("in cleanLocalData")

    sqlite_update_Query = f'''UPDATE LocalData
        SET Change=0, Condition=0
        WHERE WebsiteId = '{websiteId}';'''

    lock.acquire(True)
    cursor.execute(sqlite_update_Query)
    sqliteConnection.commit()
    lock.release()
