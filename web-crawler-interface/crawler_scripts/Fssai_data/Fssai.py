from config import *
from crawler_scripts.Fssai_data.__info__ import rdsTableName

from skimage.transform import resize
from PIL import Image
from urllib.request import urlopen
import pickle


spot_at = 10
max_attempts = 15
max_buffer_attempts = 1000
infinite_trials = 50


with open(r'crawler_scripts/computer_digit_classifier.pkl', 'rb') as fid:
    mod = pickle.load(fid)


def decodeCaptcha(url):
    image = np.array(Image.open(urlopen(url)))
    image = image[:, :, 0]
    image = image / 255
    # remove top and bottom whites
    image = image[(image != 1).any(axis=1)]

    # Cut out individual digits
    mask = (image != 1).any(axis=0)
    img_lst = []
    i = 0
    j = 0
    while j < len(mask):
        while j < len(mask) and not mask[j]:
            i = i + 1
            j = j + 1
        while j < len(mask) and mask[j]:
            j = j + 1
        if j < len(mask):
            img_lst.append(image[:, i:j])
        i = j

    # padding around the cutout digits and resizing images to (28,28)
    img_mr_lst = []
    for img in img_lst:
        temp = np.pad(img, (2, 2), 'constant', constant_values=1.)
        img_mr_lst.append(resize(temp, (28, 28)))

    # flattening for feeding in the model
    img_mr = np.array(np.array(img_mr_lst).reshape(6, 784)).reshape(6, -1)
    return ''.join(list(mod.predict(img_mr)))


def checkIfAvailable(driver, previous, element_id):
    eleSelect = Select(driver.find_element_by_xpath(element_id))
    optionList = eleSelect.options[1:]

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
            res = input('Shall I ignore this? (y/n):')
            if res == 'y' or res == 'Y' or res == 'yy':
                break
        elif attempt > max_attempts:
            raise Exception('Element Unavailable :( !!')
        print('attempt ' + str(attempt) + ' unsuccessful !')
        time.sleep(1)
        attempt += 1
    print('attempt ' + str(attempt) + ' successful !')


def run(websiteId, skip):

    driver = webdriver.Chrome(PATH)


    statexpath = '//*[@id="content"]/div[1]/div/div[1]/div/div/form/div[2]/div/div[2]/select'
    districtxpath = '//*[@id="content"]/div[1]/div/div[1]/div/div/form/div[3]/div/div[1]/select'
    prev_district = '-'

    driver.get("https://foscos.fssai.gov.in/advance-fbo-search")

    time.sleep(10)

    stateSelect = Select(driver.find_element_by_xpath(statexpath))
    stateDropDown = [o.text for o in stateSelect.options][1:]
    stateDropDown = cm.cutList(websiteId, skip, dropDownList=stateDropDown, level=0)

    for stateName in stateDropDown:

        trial = 0
        while 1:
            try:
                stateSelect = Select(driver.find_element_by_xpath(statexpath))
                stateSelect.select_by_visible_text(stateName)
                break
            except Exception as err:
                trial += 1
                if trial == infinite_trials:
                    raise Exception('unable to access state dropdown')
                print('accessing state gave error..')
                print('Retrying..')
                time.sleep(1)

        print('Selected State - ' + stateName)

        checkUntilFound(driver, prev_district, districtxpath)

        districtSelect = Select(driver.find_element_by_xpath(districtxpath))
        districtDropDown = [o.text for o in districtSelect.options]
        prev_district = districtDropDown[1]
        districtDropDown = districtDropDown[1:]
        districtDropDown = cm.cutList(websiteId, skip, dropDownList=districtDropDown, level=1)


        for districtName in districtDropDown:
            trial = 0
            while 1:
                try:
                    districtSelect = Select(driver.find_element_by_xpath(districtxpath))
                    districtSelect.select_by_visible_text(districtName)
                    break
                except:
                    trial+=1
                    if trial == infinite_trials:
                        raise Exception('unable to access district dropdown')
                    print('accessing district gave error..')
                    print('Retrying..')
                    time.sleep(1)

            print('Selected District - ' + districtName)

            skip = ldb.setLocalData(websiteId, stateName, districtName)

            captchaImg = driver.find_element_by_xpath(
                '//*[@id="content"]/div[1]/div/div[1]/div/div/form/div[7]/div/div[1]/p/img')
            captchaNum = decodeCaptcha(captchaImg.get_attribute('src'))
            captchaInput = driver.find_element_by_xpath(
                '//*[@id="content"]/div[1]/div/div[1]/div/div/form/div[7]/div/div[2]/div/input')
            captchaInput.clear()
            captchaInput.send_keys(captchaNum)
            driver.find_element_by_xpath('//*[@id="content"]/div[1]/div/div[1]/div/div/form/button[1]').click()

            notification = driver.find_elements_by_xpath('//*[@id="Body"]/app-root/simple-notifications/div')
            for notice in notification:
                if notice.text == 'Please enter valid captcha code.':
                    try:
                        time.sleep(2)
                        captchaImg = driver.find_element_by_xpath(
                            '//*[@id="content"]/div[1]/div/div[1]/div/div/form/div[7]/div/div[1]/p/img')
                        captchaNum = decodeCaptcha(captchaImg.get_attribute('src'))
                        captchaInput = driver.find_element_by_xpath(
                            '//*[@id="content"]/div[1]/div/div[1]/div/div/form/div[7]/div/div[2]/div/input')
                        captchaInput.clear()
                        captchaInput.send_keys(captchaNum)
                        driver.find_element_by_xpath(
                            '//*[@id="content"]/div[1]/div/div[1]/div/div/form/button[1]').click()
                    except:
                        pass
                    break

            recAvailable = True
            attempt = 0
            while 1:
                try:
                    driver.find_element_by_xpath('//*[@id="content"]/div[1]/div/div[2]/div/form/p[2]')
                    break
                except:
                    attempt += 1
                    if attempt > spot_at:
                        print('~~~~~~~~~~~`' + districtName + ' might not have any records~~~~~~~~~~')
                        recAvailable = False
                        break
                    print('data page not loading..')
                    print('Retrying..')
                    time.sleep(2)

            prev_record = '-'
            while recAvailable:
                try:
                    df = pd.read_html(driver.page_source)[0]
                except:
                    input('read_html error !!..what to do now :( ')
                    break
                df = df.replace(',', ';', regex=True)
                df = df.replace('\n', '|', regex=True)

                df['License No./Registration No.'] = df['License No./Registration No.'].astype(str)

                df.columns = ['SNo', 'FBO_Company_Name', 'Premises_Address', 'License_No_Registration_No',
                              'License_Type', 'Valid_Active/Inactive', 'List of Products']

                df['State'] = stateName
                df['District'] = districtName

                tot_count = driver.find_element_by_xpath('//*[@id="content"]/div[1]/div/div[2]/div/form/p[2]').text[12:]
                if prev_record == tot_count:
                    print('----end of the page----')
                    driver.find_element_by_xpath('//*[@id="table-datatables"]/div/div/div[3]/button').click()
                    trial = 0
                    while 1:
                        try:
                            Select(driver.find_element_by_xpath(districtxpath))
                            break
                        except:
                            trial+=1
                            if trial == infinite_trials:
                                raise Exception('unable to return to the main page')
                            print('accessing main page gave error..')
                            print('Retrying..')
                            time.sleep(1)
                    break

                if prev_record != str(df.SNo.iloc[-1]):
                    print('Tot records : ' + tot_count + ', left : ' + str(int(tot_count) - df.SNo.iloc[-1]))

                    extractManager.appendDataToDataPath(df, websiteId)
                    temp = str(df.SNo.iloc[-1])
                    try:
                        driver.find_element_by_xpath(
                            '//*[@id="data-table-simple_wrapper"]/div/app-custom-pagination/ul/li[2]/a').click()
                        prev_record = temp
                    except:
                        pass


    extractManager.transferDataToS3(rdsTableName, websiteId)
    driver.quit()

