from config import *
from crawler_scripts.Leads.__info__ import rdsTableName



def run(websiteId, skip):
    increment = ldb.getIncrement(websiteId)
    driver = webdriver.Chrome(PATH)
    driver.get("https://www.crabtreeindia.com/our-network")

    # get the state dropdown
    stateSelect = Select(driver.find_element_by_id(
        "p_lt_ctl02_pageplaceholder_p_lt_ctl00_CustomTableForm_plcUp_form_State_dropDownList"))

    stateDropDown = [o.text for o in stateSelect.options][1:]
    stateDropDown = cm.cutList(websiteId, skip, dropDownList=stateDropDown, level=0)

    for stateName in stateDropDown:
        stateSelect = Select(driver.find_element_by_id(
            "p_lt_ctl02_pageplaceholder_p_lt_ctl00_CustomTableForm_plcUp_form_State_dropDownList"))
        stateSelect.select_by_visible_text(stateName)
        time.sleep(4)

        # get the district drop down
        DistrictSelect = Select(driver.find_element_by_id(
            "p_lt_ctl02_pageplaceholder_p_lt_ctl00_CustomTableForm_plcUp_form_City_dropDownList"))

        DistrictDropDown = [o.text for o in DistrictSelect.options][1:]
        DistrictDropDown = cm.cutList(websiteId, skip, dropDownList=DistrictDropDown, level=1)


        for DistrictName in DistrictDropDown:

            DistrictSelect = Select(driver.find_element_by_id(
                "p_lt_ctl02_pageplaceholder_p_lt_ctl00_CustomTableForm_plcUp_form_City_dropDownList"))
            time.sleep(2)
            DistrictSelect.select_by_visible_text(DistrictName)
            time.sleep(4)

            skip = ldb.setLocalData(websiteId, stateName, DistrictName, increment=increment)
            #   get the product drop down

            ProductSelect = Select(driver.find_element_by_id(
                "p_lt_ctl02_pageplaceholder_p_lt_ctl00_CustomTableForm_plcUp_form_ProductCategory_dropDownList"))
            ProductDropDown = [o.text for o in ProductSelect.options][1:]

            for ProductName in ProductDropDown:
                ProductSelect.select_by_visible_text(ProductName)
                search = driver.find_element_by_xpath('//*[@id="form"]/div[8]/div[1]/div/div[1]/div[2]/input')
                search.click()
                time.sleep(4)

                dealerTable = driver.find_element_by_class_name("dealerResult")
                dealerRecords = dealerTable.find_elements_by_class_name("col-sm-6")

                for dealer in dealerRecords:
                    print(dealer.text)

                    df_row = pd.DataFrame({'State': [stateName], 'City': [DistrictName], 'Summary': [dealer.text]})
                    df_row['DealerName'] = df_row.Summary.str.extract('^(.+)\n')
                    df_row['DealerAddress'] = df_row.Summary.str.extract('^.*\n([\w\W]+)\nPostal')
                    df_row['Pincode'] = df_row.Summary.str.extract(': *(.*)\nTelephone')
                    df_row['DealerNumber'] = df_row.Summary.str.extract('Telephone: *([\w\W]+)\nEmail')
                    df_row['Email'] = df_row.Summary.str.extract('Email: *(.*)$')
                    df_row['DealerNumber'] = df_row.DealerNumber.replace("\n", " , ", regex=True)
                    df_row['DealerAddress'] = df_row.DealerAddress.replace("\n", " , ", regex=True)


                    if rds.existsInRDS(df_row, rdsTableName, websiteId, ['Summary']):
                        # insertion was done -- new record found
                        increment += 1
                        skip = ldb.setLocalData(websiteId, stateName, DistrictName, increment=increment)
                        print('New record found !')

                    #   print(stateName, DistrictName, dealer.text)
                    extractManager.appendDataToDataPath(df_row, websiteId)


    extractManager.transferDataToS3(rdsTableName, websiteId)
    driver.quit()
