import os
import time
import glob
import boto3
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


DOWNLOAD_DIR = os.path.abspath("./dieases")
CHROMEDRIVER_PATH = "./chromedriver/chromedriver"
TARGET_URL = (
    "https://opendata.hira.or.kr/op/opc/olapMfrnIntrsIlnsInfoTab5.do?moveFlag=Y"
)
S3_BUCKET_NAME = "favicon-dataset"


def configure_driver(download_dir):
    chrome_options = Options()
    chrome_options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
        },
    )
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    service = Service(CHROMEDRIVER_PATH)
    return webdriver.Chrome(service=service, options=chrome_options)


def set_date_range(driver, start_date, end_date):
    driver.execute_script(
        """
        let startInput = document.getElementById('sYm');
        let endInput = document.getElementById('eYm');
        startInput.value = arguments[0];
        endInput.value = arguments[1];
        startInput.classList.add('active');
        endInput.classList.add('active');
        startInput.dispatchEvent(new Event('change', { bubbles: true }));
        endInput.dispatchEvent(new Event('change', { bubbles: true }));
    """,
        start_date,
        end_date,
    )


def download_file(driver, wait, index):
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="searchDate"]/div/div/span[2]/label')
        )
    ).click()
    time.sleep(1)

    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="searchBtn2"]'))).click()
    time.sleep(5)

    download_button = wait.until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="exlBtn"]'))
    )
    driver.execute_script("arguments[0].click();", download_button)
    print(f"{index+1}번째 항목 다운로드 완료")
    time.sleep(2)


def upload_and_cleanup_tempfile(download_dir, bucket_name, s3_key):
    files = glob.glob(os.path.join(download_dir, "*.xlsx"))
    if not files:
        print("업로드할 파일을 찾을 수 없습니다.")
        return
    latest_file = max(files, key=os.path.getctime)

    s3 = boto3.client("s3")
    s3.upload_file(latest_file, bucket_name, s3_key)
    print(f"S3 업로드 완료: {s3_key}")

    os.remove(latest_file)


def main():
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    driver = configure_driver(DOWNLOAD_DIR)
    wait = WebDriverWait(driver, 10)

    try:
        print("질병 데이터를 다운하겠습니다. 잠시만 기다려주세요...")
        driver.get(TARGET_URL)

        wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="btnSearch"]'))
        ).click()
        time.sleep(2)

        items = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//table/tbody/tr/td[2]/a"))
        )
        print(f"총 {len(items)}개의 항목을 찾았습니다.")

        start_date = input("시작 시점 (예: 2024-03): ").strip()
        end_date = input("종료 시점 (예: 2024-05): ").strip()
        set_date_range(driver, start_date, end_date)

        for index in range(len(items)):
            print(f"{index+1}번째 항목 처리 중...")
            items[index].click()
            time.sleep(2)

            download_file(driver, wait, index)

            s3_filename = f"origin/dieases/item_{index+1}_{start_date}_{end_date}.xlsx"
            upload_and_cleanup_tempfile(DOWNLOAD_DIR, S3_BUCKET_NAME, s3_filename)

            # 목록 다시 불러오기
            wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="btnSearch"]'))
            ).click()
            time.sleep(2)
            items = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//table/tbody/tr/td[2]/a")
                )
            )

        print("모든 항목 다운로드 및 업로드 완료!")

    finally:
        driver.quit()
        shutil.rmtree(DOWNLOAD_DIR, ignore_errors=True)


if __name__ == "__main__":
    main()
