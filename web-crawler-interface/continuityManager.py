import database.LocalDataBaseMonitor as ldb

def cutList(websiteId, skip, dropDownList, level = 0, index = False, defaultStartIndex = 0):

    splitIndex = defaultStartIndex
    if skip != -100:
        localSkip = 0
        levelData = '-'

        data = ldb.getWebsiteData(websiteId)[0]
        level0Data = data[1]
        level1Data = data[2]
        level2Data = data[3]

        if level == 0:
            levelData = level0Data
            if level1Data == '-':
                localSkip = skip

        elif level == 1:
            levelData = level1Data
            if level2Data == '-':
                localSkip = skip

        elif level == 2:
            levelData = level2Data
            localSkip = skip


        if levelData in dropDownList:
            splitIndex = dropDownList.index(levelData)
            if (splitIndex + localSkip) >= 0:
                splitIndex = splitIndex + localSkip
                dropDownList = dropDownList[splitIndex:]
            else:
                dropDownList = dropDownList[splitIndex:]

    if index:
        return splitIndex

    return dropDownList
