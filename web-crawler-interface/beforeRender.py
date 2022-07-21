import glob
import database.LocalDataBaseMonitor as ldb


# mention your custom names here..Otherwise default folder names / file names will get rendered
# for instance, Mahindra will be rendered as it is because it's not mentioned in this custom map
customMap = {
    # website categories
    'Competition': 'Competition Websites',
    'Leads': 'Leads Websites',
    'Fssai_data': 'Fssai Website',

    # website names
    'Luminous': 'Luminous Battery',
    'Daikin': 'Daikin ACs',
    'Godrej': 'Godrej Interio',
    'Malabar': 'Malabar Cements',
    'Usha': 'Usha Fans',
}

def getFolderMap(folderType = 'custom'):
    scraperFilesList = glob.glob('.\crawler_scripts\*\*.py')

    folderMap = {}

    for scraperFile in scraperFilesList:
        temp = scraperFile.split('\\')
        folder = temp[-2]

        # folder name customisations
        if folderType == 'custom':
            if folder in customMap:
                folder = customMap[folder]

        if folder not in folderMap:
            folderMap[folder] = []

        file = temp[-1]
        file = file.split('.')[0]
        if file.isalpha():
            websiteCustomName = file
            # Website Name customisations
            if file in customMap:
                websiteCustomName = customMap[file]

            folderMap[folder] += [{'WebsiteId': file, 'WebsiteName': websiteCustomName}]

    return folderMap


def getRenderMap():
    
    renderMap = getFolderMap()

    for folder in renderMap:
        for row in renderMap[folder]:
            websiteId = row['WebsiteId']

            # getting data from local database
            data = ldb.getWebsiteData(websiteId)

            # new website scraper file added to crawler_scripts
            if len(data) == 0:
                ldb.createNewWebsiteData(websiteId)
                data = ldb.getWebsiteData(websiteId)

            data = data[0]
            row['State'] = data[1]
            row['City'] = data[2]
            row['Pin'] = data[3]
            row['Increment'] = data[4]
            row['RowCount'] = data[5]
            row['LastRun'] = data[6]
            row['Condition'] = data[8]

    return renderMap
