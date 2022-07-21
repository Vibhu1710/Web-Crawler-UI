from config import *
from crawler_scripts.Leads.__info__ import rdsTableName

max_attempts = 25

def run(websiteId, skip):
    increment = ldb.getIncrement(websiteId)

    driver = webdriver.Chrome(executable_path=PATH)
    driver.get("https://www.godrejinterio.com/storelocator")

    pinCodeDf = pd.read_csv("crawler_scripts/pincode.csv", dtype='object')

    pins = list(pinCodeDf['Pincode'])
    pins = cm.cutList(websiteId, skip, dropDownList=pins, level=0)

    for i in range(max_attempts):
        try:
            ip = driver.find_element_by_css_selector("div .pc-field")
            break
        except:
            print('trying to access pin input')
            time.sleep(1)


    for pin in pins:
        ip.clear()
        ip.send_keys(pin)
        submit = driver.find_element_by_id("locateStoreBtn")
        driver.execute_script("arguments[0].click();", submit);

        time.sleep(2)

        for i in range(max_attempts):
            try:
                element = driver.find_element_by_class_name("storeList")
                break
            except:
                print('trying to find the store list')
                time.sleep(1)

        boxes = element.find_elements_by_css_selector("div .storeListItem")
        count = 0

        skip = ldb.setLocalData(websiteId, pin, increment=increment)

        for box in boxes:

            count += 1
            total = box.text
            name = box.find_element_by_class_name("storeName")
            name = name.text
            address = box.find_element_by_class_name("store-detal-desc")
            address = address.text
            realpin = address[-6:]
            phone = box.find_element_by_class_name("PhoneNo")
            phone = phone.text

            data = {'DealerName': [name], 'DealerAddress': [address], 'DealerNumber': [phone], 'Summary': [total],
                    'Pincode': [realpin], 'State': [''], 'PinSearched': [pin]}

            df_row = pd.DataFrame(data)
            state = ''

            try:
                if pinCodeDf.loc[pinCodeDf['Pincode'] == realpin, 'StateName'].size > 0:
                    state = pinCodeDf.loc[pinCodeDf['Pincode'] == realpin, 'StateName'].iloc[0]
            except:
                pass

            df_row['State'] = [state]

            if rds.existsInRDS(df_row, rdsTableName, websiteId, ['Summary','PinSearched']):
                # insertion was done -- new record found
                increment += 1
                # notify ui about the increment change
                skip = ldb.setLocalData(websiteId, pin, increment=increment)
                print('New record found !')

            extractManager.appendDataToDataPath(df_row, websiteId)


    extractManager.transferDataToS3(rdsTableName, websiteId)
    driver.quit()
