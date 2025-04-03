from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
import time
import os


download_path = os.path.abspath("./environment")

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
    print("환경 데이터를 다운하겠습니다. 잠시만 기다려주세요...")
    url = "https://stat.me.go.kr/portal/stat/easyStatPage.do"
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    print("다운받고자 하는 기간의 시점을 다음과 같은 형식으로 입력해주세요: 2024-03")
    start_date = input()
    print("다운받고자 하는 기간의 종점을 다음과 같은 형식으로 입력해주세요: 2024-05")
    end_date = input()
    start_year, start_month = start_date.split("-")
    end_year, end_month = end_date.split("-")
    start_month = start_month.zfill(2)
    end_month = end_month.zfill(2)

    atmospheric_environment = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="treeStatData"]/ul/li[1]/ul/li[4]/span/span[1]')
        )
    )
    atmospheric_environment.click()
    air_pollution_status = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                '//*[@id="treeStatData"]/ul/li[1]/ul/li[4]/ul/li[1]/span/span[1]',
            )
        )
    )
    air_pollution_status.click()
    month = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                '//*[@id="treeStatData"]/ul/li[1]/ul/li[4]/ul/li[1]/ul/li[2]/span/span[1]',
            )
        )
    )
    month.click()

    for i in range(1, 7):
        env = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    f'//*[@id="treeStatData"]/ul/li[1]/ul/li[4]/ul/li[1]/ul/li[2]/ul/li[{i}]',
                )
            )
        )
        env.click()

        time.sleep(1)
        dropdown = driver.find_element(By.ID, "wrttimeStartYear")
        select_start_year = Select(dropdown)
        select_start_year.select_by_value(start_year)

        time.sleep(1)
        dropdown = driver.find_element(By.ID, "wrttimeStartQt")
        select_start_month = Select(dropdown)
        select_start_month.select_by_value(start_month)

        time.sleep(1)
        dropdown = driver.find_element(By.ID, "wrttimeEndYear")
        select_end_year = Select(dropdown)
        select_end_year.select_by_value(end_year)

        time.sleep(1)
        dropdown = driver.find_element(By.ID, "wrttimeEndQt")
        select_end_month = Select(dropdown)
        select_end_month.select_by_value(end_month)

        time.sleep(1)

        check = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="addStatTab"]'))
        )
        check.click()

        time.sleep(3)

        try:
            popup = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "layerpopup-stat-area"))
            )
            if popup.is_displayed():
                download_id = '//*[@id="confDown"]'
            else:
                download_id = '//*[@id="easySheet"]/div[2]/form/div[1]/div/div[3]/div[3]/div[3]/div/div[1]/div/div[3]/div/span/button[2]'
        except:
            download_id = '//*[@id="easySheet"]/div[2]/form/div[1]/div/div[3]/div[3]/div[3]/div/div[1]/div/div[3]/div/span/button[2]'

        download_csv = wait.until(EC.element_to_be_clickable((By.XPATH, download_id)))
        download_csv.click()

        before_files = set(os.listdir(download_path))
        driver.execute_script("arguments[0].click();", download_csv)
        while True:
            after_files = set(os.listdir(download_path))
            new_files = after_files - before_files
            if new_files:
                break
            time.sleep(1)

        print(f"{i}번째 항목 다운로드 완료")
        rollback = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="tabs-main"]/span'))
        )
        rollback.click()
        time.sleep(2)

    print("모든 항목 다운로드 완료하였습니다!")


finally:
    driver.quit()
