from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
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
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

service = Service("./chromedriver/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    print("환경 데이터를 다운하겠습니다. 잠시만 기다려주세요...")