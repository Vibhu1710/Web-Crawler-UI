from config import *
from crawler_scripts.Competition.__info__ import rdsTableName

comma_replace = ';'
newline_replace = '|'

# scraping functions
def replace_comma_newline(x):
    x_without_comma = x.replace(',',comma_replace)
    x_clean = x_without_comma.replace('\n',newline_replace)
    return x_clean

def run(websiteId, skip):
    increment = ldb.getIncrement(websiteId)
    driver = webdriver.Chrome(PATH)
    driver.get("https://www.mahindrasmallcv.com/ready-to-buy.aspx")

    # get the state drop down
    stateSelect = Select(driver.find_element_by_id("ddlResState"))
    stateDropDown = [o.text for o in stateSelect.options][1:]
    stateDropDown = cm.cutList(websiteId, skip, dropDownList=stateDropDown, level=0)

    for stateName in stateDropDown:
        stateSelect = Select(driver.find_element_by_id("ddlResState"))
        stateSelect.select_by_visible_text(stateName)
        time.sleep(4)
        # get the city drop down
        citySelect = Select(driver.find_element_by_id("ddlResCity"))
        cityDropDown = [o.text for o in citySelect.options][1:]
        cityDropDown = cm.cutList(websiteId, skip, dropDownList=cityDropDown, level=1)

        for cityName in cityDropDown:
            citySelect = Select(driver.find_element_by_id("ddlResCity"))
            citySelect.select_by_visible_text(cityName)


            search = driver.find_element_by_id("lnkSearch")
            search.click()
            time.sleep(4)

            skip = ldb.setLocalData(websiteId, stateName, cityName, increment=increment)


            dealerTable = driver.find_element_by_id("dlDealer")
            dealerList = dealerTable.find_elements_by_class_name('brdrtbB')
            for dealer in dealerList:
                print(dealer.text)

                df_row = pd.DataFrame({'state':[stateName],'city':[cityName],'DealerData':[dealer.text]})

                df_row['email'] = df_row['DealerData'].str.extract('(\S+@\S+)')[0]

                df_row['dealernumber'] = df_row.DealerData.str.extract('([0-9]+)$')[0]

                df_row['dealername'] = df_row.DealerData.str.extract('^(.*)\n')[0]

                df_row['dealeraddress'] = df_row.DealerData.str.extract('^.*\n(.*)\n')[0]

                df_row['pincode'] = df_row.DealerData.str.extract('\n.*-([0-9]+)\n')[0]



                if rds.existsInRDS(df_row, rdsTableName, websiteId, ['email']):
                    # insertion was done -- new record found
                    increment += 1
                    skip = ldb.setLocalData(websiteId, stateName, cityName, increment=increment)
                    print('New record found !')

                extractManager.appendDataToDataPath(df_row, websiteId)


    extractManager.transferDataToS3(rdsTableName, websiteId)
    driver.quit()
