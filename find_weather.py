from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
import time
import os


download_path = os.path.abspath("./weather")

chrome_options = Options()
chrome_options.add_experimental_option(
    "prefs",
    {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False,
    },
)
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-gpu")

service = Service("./chromedriver/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    print("날씨 데이터를 다운하겠습니다. 잠시만 기다려주세요...")
    url = "https://data.kma.go.kr/stcs/grnd/grndTaList.do?pgmNo=70"
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    dropdown = driver.find_element(By.ID, "dataFormCd")
    select_month = Select(dropdown)
    select_month.select_by_index(1)

    dropdown = driver.find_element(By.ID, "dataTypeCd")
    select_normal = Select(dropdown)
    select_normal.select_by_index(0)

    print("다운받고자 하는 기간의 년도를 다음과 같은 형식으로 입력해주세요: 2022-2025")
    years = input()
    start_year, end_year = years.split('-')

    print("다운받고자 하는 기간의 월을 다음과 같은 형식으로 입력해주세요: 1-12")
    months = input()
    start_month, end_month = months.split('-')
    start_month = start_month.zfill(2)
    end_month = end_month.zfill(2)

    dropdown = driver.find_element(By.ID, "startYear")
    select_start_year = Select(dropdown)
    select_start_year.select_by_value(start_year)

    dropdown = driver.find_element(By.ID, "endYear")
    select_start_year = Select(dropdown)
    select_start_year.select_by_value(end_year)    
    
    dropdown = driver.find_element(By.ID, "startMonth")
    select_start_year = Select(dropdown)
    select_start_year.select_by_value(start_month)

    dropdown = driver.find_element(By.ID, "endMonth")
    select_start_year = Select(dropdown)
    select_start_year.select_by_value(end_month)

    print("원하는 지역의 번호를 선택해주세요.")
    print("-> 0. 전국  1. 서울경기  2. 강원영동  3. 강원영서  4. 충북  5. 충남")
    print("   6. 경북  7. 경남  8. 전북  9. 전남  10. 제주")
    area = int(input())+3
    
    popup_button = driver.find_element(By.ID, "btnStn")  
    popup_button.click()
    modal = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "wrap-datapop"))
    )

    region = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="ztree_2_switch"]'))
    )
    region.click()
    select = wait.until(
        EC.element_to_be_clickable((By.XPATH, f'//*[@id="ztree_{area}_a"]'))
    )
    select.click()

    ok_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="sidetreecontrol"]/a'))
    )
    ok_button.click()
    time.sleep(5)

    go_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="schForm"]/div[2]/button'))
    )
    go_button.click()
    time.sleep(3)

    download_csv = wait.until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="wrap_content"]/div[5]/div[1]/div/a[1]'))
    )
    driver.execute_script("arguments[0].click();", download_csv)
    time.sleep(2)
    
    print("다운로드 완료")

finally:
    driver.quit()