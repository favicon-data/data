import os
import time
import glob
import boto3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


DOWNLOAD_DIR = os.path.abspath("./.climate")
CHROMEDRIVER_PATH = "./chromedriver/chromedriver"
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


def get_user_input():
    print("날씨 데이터를 다운하겠습니다.")
    data_type = int(input("1. 기온  2. 기상현상일수\n번호 입력: ")) - 1
    years = input("년도를 입력해주세요 (예: 2022-2025): ")
    months = input("월을 입력해주세요 (예: 1-12): ")
    print("지역번호")
    print("-> 1. 서울  2. 인천  3. 대전  4. 대구  5. 부산")
    print("-> 6. 광주  7. 울산  8. 세종  9. 경기 10. 강원")
    print("-> 11. 충북 12. 충남 13. 전북 14. 전남 15. 경북")
    print("-> 16. 경남 17. 제주")
    area = int(input("지역 번호 선택 (1~17): "))
    return data_type, years, months, area


def get_url_and_menu_length(driver, data_type):
    if data_type == 0:
        url = "https://data.kma.go.kr/stcs/grnd/grndTaList.do?pgmNo=70"
        driver.get(url)
        return WebDriverWait(driver, 10), 1
    else:
        url = "https://data.kma.go.kr/stcs/grnd/grndRnDay.do?pgmNo=156"
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        menu_links = driver.find_elements(
            By.XPATH, '//*[@id="snb"]/nav/ul/li[3]/ul/li/a'
        )
        return wait, len(menu_links)


def select_search_options(
    driver, wait, data_type, index, start_year, end_year, start_month, end_month
):
    if data_type == 0:
        Select(driver.find_element(By.ID, "dataFormCd")).select_by_index(1)
    elif index not in [3, 4]:
        Select(driver.find_element(By.ID, "dataFormCd")).select_by_index(0)

        Select(driver.find_element(By.ID, "startMonth")).select_by_value(start_month)
        Select(driver.find_element(By.ID, "endMonth")).select_by_value(end_month)

    Select(driver.find_element(By.ID, "startYear")).select_by_value(start_year)
    Select(driver.find_element(By.ID, "endYear")).select_by_value(end_year)


def select_region(wait, driver, data_type, area_input, i):
    region_map_temp = {
        1: (14, 16),
        2: (17, 18),
        3: (20, 21),
        4: (23, 26),
        5: (27, 28),
        6: (29, 30),
        7: (31, 32),
        8: (33, 35),
        9: (39, 40),
        10: (55, 56),
        11: (62, 63),
        12: (69, 70),
        13: (80, 81),
        14: (97, 98),
        15: (134, 135),
        16: (112, 122),
        17: (127, 133),
    }

    region_map_day = {
        1: (2, 4),
        2: (11, 14),
        3: (17, 18),
        4: (8, 9),
        5: (5, 6),
        6: (15, 16),
        7: (19, 20),
        8: (122, 123),
        9: (21, 23),
        10: (27, 28),
        11: (23, 47),
        12: (50, 55),
        13: (57, 63),
        14: (68, 84),
        15: (85, 86),
        16: (100, 110),
        17: (115, 121),
    }

    # 선택한 데이터 종류에 따라 매핑 선택
    region_map = region_map_temp if data_type == 0 else region_map_day
    switch, area = region_map[area_input]

    if i not in [0, 3, 4]:
        if 5 < switch < 50:
            switch -= 1
            area -= 1
        elif 50 <= switch:
            switch -= 2
            area -= 2

    time.sleep(1)
    wait.until(EC.element_to_be_clickable((By.ID, f"ztree_{switch}_switch"))).click()
    wait.until(EC.element_to_be_clickable((By.ID, f"ztree_{area}_a"))).click()


def run_search(driver, wait, data_type):
    time.sleep(1)
    wait.until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="sidetreecontrol"]/a'))
    ).click()
    time.sleep(2)
    go_xpath = (
        '//*[@id="schForm"]/div[2]/button'
        if data_type == 0
        else '//*[@id="schForm"]/div[3]/button'
    )
    wait.until(EC.element_to_be_clickable((By.XPATH, go_xpath))).click()
    time.sleep(3)


def download_file(driver, wait, index):
    time.sleep(1)
    if index in [0, 3, 4]:
        download_path = '//*[@id="wrap_content"]/div[5]/div[1]/div/a[1]'
    else:
        download_path = f'//*[@id="wrap_content"]/div[4]/div[1]/div/a[1]'
    download_btn = wait.until(EC.presence_of_element_located((By.XPATH, download_path)))
    driver.execute_script("arguments[0].click();", download_btn)
    time.sleep(2)


def upload_and_cleanup_tempfile(download_dir, bucket_name, s3_key):
    files = glob.glob(os.path.join(download_dir, "*.csv"))
    if not files:
        print("업로드할 파일을 찾을 수 없습니다.")
        return
    latest_file = max(files, key=os.path.getctime)

    s3 = boto3.client("s3")
    s3.upload_file(latest_file, bucket_name, s3_key)
    print(f"S3 업로드 완료: {s3_key}")

    os.remove(latest_file)


def main():
    driver = configure_driver(DOWNLOAD_DIR)
    try:
        data_type, years, months, area_input = get_user_input()
        start_year, end_year = years.split("-")
        start_month, end_month = months.split("-")
        start_month = start_month.zfill(2)
        end_month = end_month.zfill(2)

        wait, length = get_url_and_menu_length(driver, data_type)

        region = {
            1: "서울",
            2: "인천",
            3: "대전",
            4: "대구",
            5: "부산",
            6: "광주",
            7: "울산",
            8: "세종",
            9: "경기",
            10: "강원",
            11: "충북",
            12: "충남",
            13: "전북",
            14: "전남",
            15: "경북",
            16: "경남",
            17: "제주",
        }
        area = region[area_input]
        year = f"{start_year}-{end_year}"
        month = f"{start_month}-{end_month}"

        for index in range(length):
            time.sleep(2)
            if data_type == 1 and index != 0:
                driver.find_elements(By.XPATH, '//*[@id="snb"]/nav/ul/li[3]/ul/li/a')[
                    index
                ].click()
                time.sleep(3)

            select_search_options(
                driver,
                wait,
                data_type,
                index,
                start_year,
                end_year,
                start_month,
                end_month,
            )
            time.sleep(4)
            region_id = "btnStn" if index != 3 else "sltArea"
            driver.find_element(By.ID, region_id).click()
            wait.until(EC.visibility_of_element_located((By.ID, "wrap-datapop")))
            select_region(wait, driver, data_type, area_input, index)
            run_search(driver, wait, data_type)
            time.sleep(4)
            download_file(driver, wait, index)

            if data_type == 0:
                s3_filename = f"origin/climate/weather_{area}_{year}_{month}.csv"
            else:
                type_name = {
                    0: "강수일수",
                    1: "눈일수",
                    2: "황사일수",
                    3: "폭염일수",
                    4: "열대야일수",
                    5: "안개일수",
                    6: "서리일수",
                    7: "결빙일수",
                    8: "우박일수",
                    9: "폭풍일수",
                    10: "뇌전일수",
                    11: "한파일수",
                }
                if index in [3, 4]:
                    s3_filename = f"origin/climate/{type_name[index]}_{area}_{year}.csv"
                else:
                    s3_filename = (
                        f"origin/climate/{type_name[index]}_{area}_{year}_{month}.csv"
                    )

            upload_and_cleanup_tempfile(DOWNLOAD_DIR, S3_BUCKET_NAME, s3_filename)

        print("다운로드 완료되었습니다.")
    except Exception as e:
        print("오류 발생:", e)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
