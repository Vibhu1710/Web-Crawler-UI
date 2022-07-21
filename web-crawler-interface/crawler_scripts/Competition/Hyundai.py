from config import *
from crawler_scripts.Competition.__info__ import rdsTableName


newline_replace = '|'
comma_replace = ';'


def replace_comma_newline(x):
    x_without_comma = x.replace(',', comma_replace)
    x_clean = x_without_comma.replace('\n', newline_replace)
    return x_clean


def run(websiteId, skip):

    driver = webdriver.Chrome(PATH)
    driver.get("https://www.hyundai.com/in/en/click-to-buy/find-a-dealer-and-website.html")

    DealershipSelect = Select(driver.find_element_by_id("dealership"))
    DealershipDropDown = [o.text for o in DealershipSelect.options][1:]

    DealershipDropDown = cm.cutList(websiteId, skip, dropDownList=DealershipDropDown, level=0)

    for DealershipName in DealershipDropDown:
        DealershipSelect = Select(driver.find_element_by_id("dealership"))
        DealershipSelect.select_by_visible_text(DealershipName)
        time.sleep(2)

        ModelSelect = Select(driver.find_element_by_id("Model"))
        ModelDropDown = [o.text for o in ModelSelect.options][1:]

        ModelDropDown = cm.cutList(websiteId, skip, dropDownList=ModelDropDown, level=1)

        for ModelName in ModelDropDown:
            ModelSelect = Select(driver.find_element_by_id("Model"))
            ModelSelect.select_by_visible_text(ModelName)
            time.sleep(2)

            stateSelect = Select(driver.find_element_by_id("State"))
            stateDropDown = [o.text for o in stateSelect.options]

            stateDropDown = cm.cutList(websiteId, skip, dropDownList=stateDropDown, level=2)

            for stateName in stateDropDown:
                stateSelect = Select(driver.find_element_by_id("State"))
                stateSelect.select_by_visible_text(stateName)
                time.sleep(2)

                skip = ldb.setLocalData(websiteId, DealershipName, ModelName, stateName)

                citySelect = Select(driver.find_element_by_id("City"))
                cityDropDown = [o.text for o in citySelect.options][1:]

                for cityName in cityDropDown:
                    citySelect = Select(driver.find_element_by_id("City"))
                    citySelect.select_by_visible_text(cityName)
                    time.sleep(2)

                    search = driver.find_element_by_xpath('//*[@id="searchForm"]/div/div/div[6]/div/button')
                    search.click()
                    time.sleep(2)

                    dealerTable = driver.find_elements_by_css_selector('div.fdNavView.resultClass')
                    for dealer in dealerTable:
                        print(dealer.text)
                        df_row = pd.DataFrame(
                            {'dealership': [DealershipName], 'model': [ModelName], 'state': [stateName],
                             'city': [cityName], 'DealerData': [replace_comma_newline(dealer.text)]})
                        extractManager.appendDataToDataPath(df_row, websiteId)



    df = extractManager.readCsvFromScrapedData(websiteId)
    df['DealerName'] = df.DealerData.str.extract('^([a-zA-Z 0-9]*)\|')
    df['DealerAddress'] = df.DealerData.str.extract('\|([^\|]+)\|Phone :')
    df['PostalCode'] = df.DealerData.str.extract('([0-9]*)\|Phone')
    df['TelephoneNo'] = df.DealerData.str.extract('Phone : *([\w\W]+)\|Email')
    df['EmailAddress'] = df.DealerData.str.extract('Email : *(.*)\|Website')
    df['Website'] = df.DealerData.str.extract('Website : *(.*)\|Get')
    extractManager.writeCsvToScrapedData(df, websiteId)

    extractManager.transferDataToS3(rdsTableName, websiteId)
    driver.quit()
