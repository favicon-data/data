from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# 다운로드 경로 설정
download_path = os.path.abspath("./diseases")

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

service = Service("./chromedriver/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    print("질병데이터를 다운하겠습니다. 잠시만 기다려주세요...")
    url = "https://opendata.hira.or.kr/op/opc/olapMfrnIntrsIlnsInfoTab5.do?moveFlag=Y"
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    # 항목 조회
    search_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="btnSearch"]'))
    )
    search_button.click()
    time.sleep(2)

    item_links = wait.until(
        EC.presence_of_all_elements_located((By.XPATH, "//table/tbody/tr/td[2]/a"))
    )
    length = len(item_links)
    print(f"총 {length}개의 항목을 찾았습니다.")

    # 기간 설정
    print("다운받고자 하는 기간의 시점을 다음과 같은 형식으로 입력해주세요: 2024-03")
    start_date = input()
    print("다운받고자 하는 기간의 종점을 다음과 같은 형식으로 입력해주세요: 2024-05")
    end_date = input()

    driver.execute_script(
        """
        let startInput = document.getElementById('sYm');
        let endInput = document.getElementById('eYm');
        
        startInput.value = arguments[0];
        startInput.classList.add('active'); 
        startInput.dispatchEvent(new Event('change', { bubbles: true }));
        
        endInput.value = arguments[1];
        endInput.classList.add('active'); 
        endInput.dispatchEvent(new Event('change', { bubbles: true }));
    """,
        start_date,
        end_date,
    )

    for index in range(length):
        print(f"{index+1}번째 항목 선택 중...")

        # 연번에 따라서 하나씩 선택
        item_links[index].click()
        time.sleep(2)

        # 기간구분 - 진료년월 선택
        label_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="searchDate"]/div/div/span[2]/label')
            )
        )
        label_button.click()
        time.sleep(1)

        # 검색 버튼 클릭
        go_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="searchBtn2"]'))
        )
        go_button.click()
        time.sleep(5)

        # 엑셀 다운로드
        download_button = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="exlBtn"]'))
        )
        driver.execute_script("arguments[0].click();", download_button)

        time.sleep(2)

        print(f"{index+1}번째 항목 다운로드 완료")

        # 항목 조회
        search_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="btnSearch"]'))
        )
        search_button.click()
        time.sleep(2)

        item_links = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//table/tbody/tr/td[2]/a"))
        )

    print("모든 항목 다운로드 완료")


finally:
    driver.quit()
