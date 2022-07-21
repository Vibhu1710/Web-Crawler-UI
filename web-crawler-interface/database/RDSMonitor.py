import mysql.connector
# import pandas as pd

# rds database connector
rdsDb = mysql.connector.connect(host="ace-edr-instance-1.c3pibyraeohf.ap-south-1.rds.amazonaws.com", user="admin", passwd="", database="Data-repository", use_unicode=True, charset='utf8', use_pure=True)

mycursor = rdsDb.cursor()

# table Name to column names Mape
tableMap = {}

def getTableMap():
    return tableMap

def getTableToColumnsMap():
    rdsDb.reconnect()
    mycursor.execute("show tables")
    allTables = mycursor.fetchall()
    allTables  = [table[0] for table in allTables]
    map = {table : [] for table in allTables}

    for table in allTables:
        mycursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}'")
        tableColumns = mycursor.fetchall()
        tableColumns = [column[0] for column in tableColumns]
        map[table] = tableColumns
    print(map)
    return map


# def getColumnList(rdsTableName):
#     mycursor.execute(f"SELECT COLUMN_NAME,COLUMN_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{rdsTableName}'")
#     tableFields = mycursor.fetchall()
#     return tableFields


def createExecuteStringForExists(df_row, rdsTableName):
    executeStr = "SELECT EXISTS(SELECT 1 FROM " + rdsTableName + " WHERE"
    fields = list(df_row.columns.values)

    for field in fields[:-1]:
        executeStr += (" " + field + "='" + str(df_row.loc[0,field]) + "' AND")

    executeStr += (" " + fields[-1] + "='" + str(df_row.loc[0,fields[-1]]) + "')")
    print(executeStr)
    return executeStr


# def createExecuteStringForInsert(df_row, rdsTableName):
#     executeStr = "INSERT INTO " + rdsTableName + " ("
#     fields = list(df_row.columns.values)
#
#     executeStr += (','.join(fields))
#     executeStr += ") VALUES ("
#
#     for field in fields[:-1]:
#         executeStr += "'" + df_row.loc[0,field] + "',"
#
#     executeStr += "'" + df_row.loc[0,fields[-1]] + "')"
#     print(executeStr)
#     return executeStr



# rds based functions
def existsInTable(df_row, rdsTableName):
    global mycursor
    attempt = 0
    while 1:
        try:
            mycursor.execute(createExecuteStringForExists(df_row, rdsTableName))
            break
        except Exception as err:
            rdsDb.reconnect()
            mycursor = rdsDb.cursor()
            attempt+=1
            if attempt == 5:
                raise Exception('was not able to access mySQL database')
            print(str(err))
            print('facing issues in accessing the mySQL database..retrying')

    record = mycursor.fetchall()
    return record[0][0]

# def insertInRDS(df_row, rdsTableName):
#     mycursor.execute(createExecuteStringForInsert(df_row, rdsTableName))
#     rdsDb.commit()


def existsInRDS(df_row, rdsTableName, websiteId, notForExistList = []):

    df_row = df_row.replace(',', ';', regex=True)
    df_row = df_row.replace('\n', '|', regex=True)

    tableFields = tableMap[rdsTableName]

    websiteColName = 'Website'
    if 'Website' in tableFields:
        websiteColName = 'Website'
    elif 'website' in tableFields:
        websiteColName = 'website'

    df_row[websiteColName] = [websiteId]
    dfColumns = list(df_row.columns.values)

    commonFields = list(set(dfColumns).intersection(tableFields))

    commonFieldsForExist = []
    for col in commonFields:
        if col not in notForExistList:
            commonFieldsForExist += [col]

    df_row_for_exists = df_row.loc[:, commonFieldsForExist]
    # df_row_for_insert = df_row.loc[:, commonFields]

    try:
        if existsInTable(df_row_for_exists, rdsTableName) == 0:
            # insertInRDS(df_row_for_insert, rdsTableName)
            return True
    except Exception as e:
        print('!!-------------------', str(e), '-------------------!!')

    return False
