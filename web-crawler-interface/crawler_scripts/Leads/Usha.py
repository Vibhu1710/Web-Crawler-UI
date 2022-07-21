from config import *
from crawler_scripts.Leads.__info__ import rdsTableName


def run(websiteId, skip):

    driver = webdriver.Chrome(PATH)
    driver.get('https://www.ushafans.com/store-finder')
    action = webdriver.ActionChains(driver)
    cities = []

    # Click ByCity
    time.sleep(7)
    element = WebDriverWait(driver, 100).until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="block-system-main"]/div/section/div/div[1]/div[2]/ul/li[3]')))
    driver.find_element_by_xpath('//*[@id="block-system-main"]/div/section/div/div[1]/div[2]/ul/li[3]').click()

    # Collect Cities
    element = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.ID, 'browsers')))
    req1 = driver.find_element_by_id('browsers')
    req2 = req1.find_elements_by_tag_name('option')
    for city_s in req2:
        city = city_s.get_attribute('value')
        cities.append(city)

    cities = cm.cutList(websiteId, skip, dropDownList=cities, level=0)

    # Send cities
    ele = driver.find_element_by_xpath('//*[@id="selected"]')
    for city in cities:
        ele = driver.find_element_by_xpath('//*[@id="selected"]')
        element = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, '//*[@id="selected"]')))
        ele.send_keys(city)

        element = driver.find_element_by_xpath('//*[@id="selected"]')  # or your another selector here
        action.move_to_element(element)
        action.perform()
        action.move_by_offset(10, 20)
        # Click Submit
        driver.find_element_by_xpath('//*[@id="edit-submit-store-findercity"]').click()

        skip = ldb.setLocalData(websiteId, city)

        # Extract Data
        dlr_info = driver.find_elements_by_class_name('storesingle-left')

        for dlr in dlr_info:
            dealer = dlr.text
            x = dealer.split('\n')
            pin = (x[1].split('-')[-1]).strip()
            try:
                row = pd.DataFrame(
                    {'City': [city], 'DealerName': [x[0]], 'DealerAddress': [x[1]], 'DealerNumber': [x[2]],
                     'Pincode': [pin]})
                extractManager.appendDataToDataPath(row, websiteId)

            except:
                row = pd.DataFrame({'City': [city], 'DealerName': [x[0]], 'DealerAddress': [x[1]], 'DealerNumber': [''],
                                    'Pincode': [pin]})
                extractManager.appendDataToDataPath(row, websiteId)

            print(dealer)
            print(pin)


    extractManager.transferDataToS3(rdsTableName, websiteId)
    driver.quit()
