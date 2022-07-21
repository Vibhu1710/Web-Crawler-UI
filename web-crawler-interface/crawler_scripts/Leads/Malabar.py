from config import *
from crawler_scripts.Leads.__info__ import rdsTableName


def run(websiteId, skip):
    driver = webdriver.Chrome(PATH)
    driver.get("https://malabarcements.co.in/en/stockist")

    # get the state dropdown
    stateSelect = Select(driver.find_element_by_id("state_id"))
    stateDropDown = [o.text for o in stateSelect.options][1:]
    stateDropDown = cm.cutList(websiteId, skip, dropDownList=stateDropDown, level=0)

    for stateName in stateDropDown:
        stateSelect = Select(driver.find_element_by_id("state_id"))
        stateSelect.select_by_visible_text(stateName)
        time.sleep(5)
        # get the district drop down
        DistrictSelect = Select(driver.find_element_by_id("district_id"))
        DistrictDropDown = [o.text for o in DistrictSelect.options][1:]
        DistrictDropDown = cm.cutList(websiteId, skip, dropDownList=DistrictDropDown, level=1)

        for DistrictName in DistrictDropDown:
            DistrictSelect = Select(driver.find_element_by_id("district_id"))
            DistrictSelect.select_by_visible_text(DistrictName)

            time.sleep(5)

            dealerTable1 = driver.find_elements_by_class_name("tenderrow1")
            dealerTable2 = driver.find_elements_by_class_name("tenderrow2")
            # dealerList = dealerTable.find_elements_by_class_name('brdrtbB')

            skip = ldb.setLocalData(websiteId, stateName, DistrictName)

            for dealerRow in dealerTable1:
                dealerInfos = dealerRow.find_elements_by_tag_name('tbody')
                for dealer in dealerInfos:
                    print(dealer.text)
                    print('-----------')
                    df_row = pd.DataFrame({'State': [stateName], 'City': [DistrictName], 'Summary': [dealer.text]})
                    extractManager.appendDataToDataPath(df_row, websiteId)

            for dealerRow in dealerTable2:
                dealerInfos = dealerRow.find_elements_by_tag_name('tbody')
                for dealer in dealerInfos:
                    print(dealer.text)
                    print('-----------')
                    df_row = pd.DataFrame({'State': [stateName], 'City': [DistrictName], 'Summary': [dealer.text]})
                    extractManager.appendDataToDataPath(df_row, websiteId)


    df = extractManager.readCsvFromScrapedData(websiteId)
    df['DealerName'] = df.Summary.str.extract('^(.+?)\|')
    df['DealerAddress'] = df.Summary.str.extract('^.*?\|([\w\W]+)\|Tel')
    df['DealerAddress'] = df.DealerAddress.replace('\|', ' ', regex=True)
    df['DealerNumber'] = df.Summary.str.extract(': *(.*)$')
    extractManager.writeCsvToScrapedData(df, websiteId)

    extractManager.transferDataToS3(rdsTableName, websiteId)
    driver.quit()
