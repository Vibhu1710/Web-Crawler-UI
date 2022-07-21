from config import *
from crawler_scripts.Leads.__info__ import rdsTableName


infinite_trials = 25
spot_at = 5
max_attempts = 15
max_buffer_attempts = 350
banned_pins = ['144001', '230001', '231001']
newline_replace = '|'
comma_replace = ';'


def replace_comma_newline(x):
    x_without_comma = x.replace(',', comma_replace)
    x_clean = x_without_comma.replace('\n', newline_replace)
    return x_clean

def checkIfAvailable(driver, previous, element_id):
    trial = 0
    while 1:
        try:
            eleSelect = Select(driver.find_element_by_id(element_id))
            optionList = eleSelect.options
            break
        except:
            trial += 1
            if trial == infinite_trials:
                raise Exception('could not access the element')
            print('unable to access the element...')
            print('Retrying...')
            time.sleep(1)

    if len(optionList) != 0 and optionList[0].text == '':
        optionList = optionList[1:]

    if len(optionList) == 0:
        print('length 0')
        return False
    elif optionList[0].text == previous:
        print(previous)
        print('equal as before')
        return False

    return True


def checkUntilFound(driver, prev, ele_id):
    attempt = 1
    while not checkIfAvailable(driver, prev, ele_id):
        if attempt == spot_at:
            print('----------------------------------')
            print('prev value and current value coming same for the last ' + str(spot_at) + ' times :(')
            break
        elif attempt > max_attempts:
            raise Exception('Element Unavailable :( !!')
        print('attempt ' + str(attempt) + ' unsuccessful !')
        time.sleep(1)
        attempt += 1
    print('attempt ' + str(attempt) + ' successful !')


def waitTillBuffering(driver):
    buffer_attempt = 1
    while 1:
        element = driver.find_element_by_class_name("loading-mask")
        attributeValue = element.get_attribute("style")
        buffer_attempt = buffer_attempt + 1
        if attributeValue == 'display: none;':
            break
        elif buffer_attempt > max_buffer_attempts:
            print('---------------infinite buffering :( !!-----------------')
            print('probably a dead PIN')
            return True


def run(websiteId, skip):
    increment = ldb.getIncrement(websiteId)
    driver = webdriver.Chrome(PATH)

    prev_city = '-'
    prev_pin = '-'
    driver.get("https://www.luminousindia.com/store-locator")

    stateSelect = Select(driver.find_element_by_id("stateSelect"))
    stateDropDown = [o.text for o in stateSelect.options][1:]
    stateDropDown = cm.cutList(websiteId, skip, dropDownList=stateDropDown, level=0)

    for stateName in stateDropDown:
        stateSelect = Select(driver.find_element_by_id("stateSelect"))
        stateSelect.select_by_visible_text(stateName)
        print('Selected State - ' + stateName + ' , Prev City - ' + prev_city)

        trial = 0
        while 1:
            try:
                checkUntilFound(driver, prev_city, "citySelect")
                break
            except:
                trial += 1
                if trial == infinite_trials:
                    raise Exception('could not access state dropdown')
                print('trying to use checkUntilFound() to select state..')
                time.sleep(1)

        citySelect = Select(driver.find_element_by_id("citySelect"))
        cityDropDown = [o.text for o in citySelect.options]
        prev_city = cityDropDown[1]
        cityDropDown = cityDropDown[1:]
        cityDropDown = cm.cutList(websiteId, skip, dropDownList=cityDropDown, level=1)

        for cityName in cityDropDown:
            citySelect = Select(driver.find_element_by_id("citySelect"))
            citySelect.select_by_visible_text(cityName)
            print('Selected City - ' + cityName + ' , Prev Pin - ' + prev_pin)

            trial = 0
            while 1:
                try:
                    checkUntilFound(driver, prev_pin, "pincodeSelect")
                    break
                except:
                    trial += 1
                    if trial == infinite_trials:
                        raise Exception('could not access pin dropdown')
                    print('trying to use checkUntilFound() to select pin..')
                    time.sleep(1)

            pinSelect = Select(driver.find_element_by_id("pincodeSelect"))
            pinDropDown = [o.text for o in pinSelect.options]
            try:
                prev_pin = pinDropDown[0]
            except:
                print('No pin in this city..haha..moving to the next city...')
                continue

            pinDropDown = [pin for pin in pinDropDown if pin not in banned_pins]
            pinDropDown = cm.cutList(websiteId, skip, dropDownList=pinDropDown, level=2)

            for pin in pinDropDown:

                trial = 0
                while 1:
                    try:
                        pinSelect = Select(driver.find_element_by_id("pincodeSelect"))
                        pinSelect.select_by_visible_text(pin)
                        break
                    except:
                        trial += 1
                        if trial == infinite_trials:
                            raise Exception('could not access pin dropdown')
                        print('trying to access the pin dropdown')
                        time.sleep(1)

                print('Selected Pin - ', pin)
                while 1:
                    try:
                        driver.find_element_by_class_name("button").click()
                        break
                    except Exception as e:
                        if str(e).find('element click intercepted:') != -1:
                            print('Seems something is covering the Search button !')
                            res = input('press any key once the Search button is clear :)')
                        else:
                            raise Exception('Some other error for the Search button :(')

                deadOrNot = waitTillBuffering(driver)

                if deadOrNot:
                    banned_pins.append(pin)
                    driver.refresh()
                    time.sleep(2)

                    trial = 0
                    while 1:
                        try:
                            stateSelect = Select(driver.find_element_by_id("stateSelect"))
                            stateSelect.select_by_visible_text(stateName)
                            break
                        except:
                            trial += 1
                            if trial == infinite_trials:
                                raise Exception('could not access state dropdown')
                            print('trying to access state select dropdown')
                            time.sleep(1)

                    trial = 0
                    while 1:
                        try:
                            citySelect = Select(driver.find_element_by_id("citySelect"))
                            citySelect.select_by_visible_text(cityName)
                            break
                        except:
                            trial += 1
                            if trial == infinite_trials:
                                raise Exception('could not access city dropdown')
                            print('trying to access city dropdown')
                            time.sleep(1)

                    continue

                row = driver.find_element_by_id("store_details")
                columns = row.find_elements_by_class_name("column")
                print('------' + stateName + '------' + cityName + '------' + pin + '------')
                skip = ldb.setLocalData(websiteId, stateName, cityName, pin, increment=increment)

                for column in columns:
                    if column.text == 'No store found':
                        print('-------No store found :|-------')
                        pass
                    else:
                        print('=====================')
                        print(column.text)
                        print('=====================')
                        df_row = pd.DataFrame(
                            {'State': [stateName], 'City': [replace_comma_newline(cityName)], 'Pincode': [pin],
                             'DealerData': [replace_comma_newline(column.text)]})

                        # bringing record to row level
                        df_row['DealerName'] = df_row.DealerData.str.extract('^Name:\s*(.*)\s*\|Address')
                        df_row['DealerAddress'] = df_row.DealerData.str.extract('^.*Address:\s*(.*)\s*\|')
                        df_row['DealerNumber'] = df_row.DealerData.str.extract('Mobile:\s*(.*)\s*$')

                        if rds.existsInRDS(df_row, rdsTableName, websiteId):
                            # insertion was done -- new record found
                            increment += 1
                            skip = ldb.setLocalData(websiteId, stateName, cityName, pin, increment=increment)
                            print('New record found !')

                        # To-do - connection with s3
                        extractManager.appendDataToDataPath(df_row, websiteId) # csv file will be used



    extractManager.transferDataToS3(rdsTableName, websiteId)
    print(banned_pins)
    driver.quit()

