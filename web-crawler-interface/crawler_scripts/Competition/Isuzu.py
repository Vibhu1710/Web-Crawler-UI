from config import *
from crawler_scripts.Competition.__info__ import rdsTableName

newline_replace = '|'
comma_replace = ';'


def replace_comma_newline(x):
    x_without_comma = x.replace(',', comma_replace)
    x_clean = x_without_comma.replace('\n', newline_replace)
    return x_clean


def run(websiteId, skip):

    PATH = r"C:\Program Files (x86)\chromedriver.exe"
    driver = webdriver.Chrome(PATH)

    driver.get("https://www.isuzu.in/locate-dealer/")


    # State Selection
    operation_state = Select(driver.find_element_by_id('isuzu_state'))
    StateMenu = [menu.text for menu in operation_state.options][1:]
    StateMenu = cm.cutList(websiteId, skip, dropDownList=StateMenu, level=0)

    for state in StateMenu:

        operation_state = Select(driver.find_element_by_id('isuzu_state'))
        operation_state.select_by_visible_text(state)
        time.sleep(3)

        # City Selection
        operation_city = Select(driver.find_element_by_id("isuzu_city"))
        CityMenu = [menu.text for menu in operation_city.options][1:]
        CityMenu = cm.cutList(websiteId, skip, dropDownList=CityMenu, level=1)

        for city in CityMenu:
            operation_city = Select(driver.find_element_by_id('isuzu_city'))
            operation_city.select_by_visible_text(city)

            time.sleep(3)

            # Dealer Selection
            operation_dealer = Select(driver.find_element_by_id("isuzu_dealer"))

            DealerMenu = [menu.text for menu in operation_dealer.options]

            # dropDown should be unchanged if using select_by_index
            startIndex = cm.cutList(websiteId, skip, dropDownList=DealerMenu, level=2, index=True, defaultStartIndex=1)

            for i in range(startIndex, len(DealerMenu)):
                dealer = DealerMenu[i]
                print(state, ',', city, ',', dealer, ':')

                operation_dealer = Select(driver.find_element_by_id('isuzu_dealer'))
                operation_dealer.select_by_index(i)

                time.sleep(3)

                skip = ldb.setLocalData(websiteId, state, city, dealer)

                pad = driver.find_element_by_class_name('form_pad')
                tables = pad.find_elements_by_tag_name('table')
                if len(tables) == 1:
                    df_row = pd.DataFrame({'state': state, 'city': city, 'dealername': [replace_comma_newline(dealer)],
                                           'SalesData': [replace_comma_newline(tables[0].text)],
                                           'ServiceData': [np.nan]})
                    print(tables[0].text)
                    extractManager.appendDataToDataPath(df_row, websiteId)

                elif len(tables) == 2:
                    df_row = pd.DataFrame({'state': state, 'city': city, 'dealername': [replace_comma_newline(dealer)],
                                           'SalesData': [replace_comma_newline(tables[0].text)],
                                           'ServiceData': [replace_comma_newline(tables[1].text)]})
                    print(tables[0].text)
                    print(tables[1].text)
                    extractManager.appendDataToDataPath(df_row, websiteId)

                else:
                    raise Exception('More than two tables !!')


    df = extractManager.readCsvFromScrapedData(websiteId)

    df['servicename'] = df.ServiceData.str.extract('^Name (.+?)\|')
    df['serviceaddress'] = df.ServiceData.str.extract('Address (.*?)\|')
    df['servicecontact'] = df.ServiceData.str.extract('Contact\s*(.*?)$')
    ind = df[df.serviceaddress.str.contains('mail', case=False) == True].index
    df.loc[ind, 'serviceemail'] = df.loc[ind, 'serviceaddress'].str.extract('([\w.-]+@[\w.-]+)')[0]

    df['salesname'] = df.SalesData.str.extract('^Name (.+?)\|')
    df['salesaddress'] = df.SalesData.str.extract('Address (.*?)\|')
    df['salescontact'] = df.SalesData.str.extract('Contact\s*(.*?)$')
    ind = df[df.salesaddress.str.contains('mail', case=False) == True].index
    df.loc[ind, 'salesemail'] = df.loc[ind, 'salesaddress'].str.extract('([\w.-]+@[\w.-]+)')[0]

    extractManager.writeCsvToScrapedData(df, websiteId)


    extractManager.transferDataToS3(rdsTableName, websiteId)
    driver.quit()
