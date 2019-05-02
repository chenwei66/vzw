import re, time
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import mysql.connector


def waitElementPresent(driver, locator, timeout):
    elem = None
    try:
        elem = WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))
    except Exception as ex:
        print(ex)
    return elem

def getWebDriver():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')

    driver = webdriver.Chrome(options=options)          
    return driver

def loadReviewPageWithOption(driver, url, reviewOption):
    driver.get(url)

    # wait "Reviews" tab availabe and click
    locReview = (By.ID, "reviewsLink") 
    reviewTab = waitElementPresent(driver, locReview, 10)
    if not reviewTab:
        raise RuntimeError("ReviewLink Not Found")
    reviewTab.click()

    # wait "reviewsFaqsDropDown" and click
    locReviewsFaqsDropDown = (By.CSS_SELECTOR, "div.reviewsFaqsDropDown")
    reviewsFaqsDropDown = waitElementPresent(driver, locReviewsFaqsDropDown, 10)
    if not reviewsFaqsDropDown:
        raise RuntimeError("ReviewsFaqsDropDown Not Found")
    reviewsFaqsDropDown.click()

    # wait DropDwon sub-menu and click reviewOption
    locSelectMenuOuter = (By.CSS_SELECTOR, "div.Select-menu-outer")
    selectMenuOuter = waitElementPresent(driver, locSelectMenuOuter, 10)
    if not selectMenuOuter:
        raise RuntimeError("DropDwon Not Found")
    option = selectMenuOuter.find_element(By.ID, reviewOption)
    if not option:
        raise RuntimeError("SubMenu Option Not Found")
    option.click()

def _parseOnePage(driver):
    ret = []
    for one in driver.find_elements(By.CSS_SELECTOR, "#reviews div.row.border_grayThree.onlyTopBorder.noSideMargin"):
        userNickName = one.find_element(By.CSS_SELECTOR, "div.flex > div:nth-child(2) > span:nth-child(1)").text
        timeStr = one.find_element(By.CSS_SELECTOR, "div.flex > div:nth-child(2) > span:nth-child(2)").text
        reviewTitle = one.find_element(By.CSS_SELECTOR, "div.NHaasDS75Bd.wrapText").text
        reviewText = one.find_element(By.CSS_SELECTOR, "div.NHaasDS55Rg.wrapText > span").text
        ret.append({"UserNickname": userNickName, "Title": reviewTitle, "ReviewText": reviewText, "timestr":timeStr})
    return ret

def _timeStr2Date(timestr):
    m = re.match(r"(\d+)\W+days?\W+ago", timestr)
    if m:
        return datetime.now() - timedelta(days=int(m.group(1)))
    
    m = re.match(r"(\d+)\W+months?\W+ago", timestr)
    if m:
        return datetime.now() - timedelta(days=365/12*int(m.group(1)))
    
    m = re.match(r"(\d+)\W+years?\W+ago", timestr)
    if m:
        return datetime.now() - timedelta(days=365*int(m.group(1)))
    
    raise RuntimeError("Unsupported TimeStr [%s]" % timestr)


def parseReviews(driver, nums):
    ret = []

    locTitle = (By.CSS_SELECTOR, "#tile_container h1")
    title = driver.find_element(*locTitle)
    if not title:
        raise RuntimeError("Title Not Found")
    txtDevice = title.text

    while len(ret) < nums:
        time.sleep(3)
        for one in _parseOnePage(driver):
            one['SubmissionTime'] = one.pop('timestr')
            one['Device'] = txtDevice
            ret.append(one)
        
        driver.find_element(By.CSS_SELECTOR, "#pagination li.nextClick.displayInlineBlock.padLeft5 > a").click()
    
    return ret

def saveToDb(data):
    mydb = mysql.connector.connect(
        host="localhost",
        user="wchen",
        passwd="Wei12345"
    )

    mycursor = mydb.cursor()
    mycursor.execute("CREATE DATABASE IF NOT EXISTS reviewDb")

    mydb = mysql.connector.connect(
        host="localhost",
        user="wchen",
        passwd="Wei12345",
        database="reviewDb"
    )

    mycursor = mydb.cursor()
    mycursor.execute("DROP TABLE IF EXISTS s_review")
    mycursor.execute("CREATE TABLE s_review (id INT AUTO_INCREMENT PRIMARY KEY, Device VARCHAR(20), Title VARCHAR(80))")
    mycursor.execute("ALTER TABLE s_review ADD COLUMN ReviewText VARCHAR(300)")
    mycursor.execute("ALTER TABLE s_review ADD COLUMN submitTime VARCHAR(30)")
    mycursor.execute("ALTER TABLE s_review ADD COLUMN userName VARCHAR(30)")

    sql = "INSERT INTO s_review (Device, Title, ReviewText, submitTime, userName) VALUES (%s, %s, %s, %s, %s)"

    for one in data:
        ddd = (one["Device"], one["Title"], one["ReviewText"], one["SubmissionTime"], one["UserNickname"])
        mycursor.execute(sql, ddd)

    mydb.commit()


driver = getWebDriver()
productionUrl = 'https://www.verizonwireless.com/smartphones/samsung-galaxy-s7/'
reviewOption = "react-select-2--option-5" # Newest

loadReviewPageWithOption(driver, productionUrl, reviewOption)

# crawl 100 records and export results to MySql
ret = parseReviews(driver, 100)
driver.close()
saveToDb(ret)


