#!/usr/bin/env python3
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

opts = Options()
opts.add_argument('--headless')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--window-size=1280,1024')

driver = webdriver.Chrome(options=opts)

try:
    driver.get('http://localhost:9091/index.html')
    time.sleep(3)

    # Check for JS errors via browser console logs
    logs = driver.get_log('browser')
    if logs:
        print(f'Browser console ({len(logs)} entries):')
        for entry in logs[:20]:
            print(f'  [{entry["level"]}] {entry["message"][:200]}')

    # Simple check: how many cells?
    count = driver.execute_script("return document.querySelectorAll('#sudoku-grid .cell').length;")
    print(f'\nGrid cells found: {count}')

    # Check if guide button exists
    hasGuide = driver.execute_script("return !!document.getElementById('guide-btn');")
    print(f'Guide button exists: {hasGuide}')

    # Check theme select
    hasTheme = driver.execute_script("return !!document.getElementById('theme-select');")
    print(f'Theme selector exists: {hasTheme}')

finally:
    driver.quit()
