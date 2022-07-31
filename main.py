# -*- coding: utf-8 -*-
import json
import os
import re
import shutil
import time
import traceback

import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

TTS_URL = 'https://ttsmp3.com/'
CONFIG_PATH = os.path.abspath("./config.json")
DATA_PATH = os.path.abspath("data.json")


def read_json_file(config_path):
    with open(config_path, 'r') as f:
        return json.loads(f.read())


if __name__ == '__main__':
    assert os.path.exists(CONFIG_PATH), f"Not found config file. config file path: {CONFIG_PATH}"
    config = read_json_file(CONFIG_PATH)

    assert os.path.exists(DATA_PATH), f"Not found data file. data file path: {DATA_PATH}"
    data = read_json_file(DATA_PATH)

    chrome_download_path = os.path.abspath("./")
    assert os.path.exists(chrome_download_path), f"Not found chrome download path. {chrome_download_path}"

    download_dir_path = os.path.join(chrome_download_path, 'tts')
    if os.path.exists(download_dir_path):
        shutil.rmtree(download_dir_path)

    chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
    driver_path = os.path.abspath(f'./{chrome_ver}/chromedriver')

    if not os.path.exists(driver_path):
        print("Install driver...")
        chromedriver_autoinstaller.install(True)

    try:
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(driver_path, options=options)

        # set word
        driver.get(TTS_URL)

        words = data['words']
        words_len = len(words)
        for idx, word in enumerate(words):

            voiceText = driver.find_element(By.ID, 'voicetext')
            voiceText.send_keys(word)

            # download
            downloadButton = driver.find_element(By.ID, 'downloadenbutton')
            downloadButton.click()

            if not os.path.exists(download_dir_path):
                os.mkdir(download_dir_path)

            # file renaming
            while True:
                time.sleep(0.5)
                find_file = False
                files = os.listdir(chrome_download_path)
                target_file_path = ''
                for file in files:
                    full_path = os.path.join(chrome_download_path, file)
                    ext = full_path.split('.')[-1]
                    target_file_path = f'{os.path.join(download_dir_path, word)}.{ext}'

                    if not find_file and re.match(r'.+/ttsMP3\.com.+', full_path) and 'crdownload' not in full_path:
                        shutil.move(full_path, target_file_path)
                        find_file = True
                        time.sleep(0.5)
                        break

                if find_file and target_file_path != '' and os.path.exists(target_file_path):
                    print(f'[{idx + 1}/{words_len}]Download success. {word} (path: {target_file_path})')
                    break

            voiceText.clear()
            time.sleep(0.1)

    except Exception:
        print(traceback.format_exc())
    finally:
        driver.close()
