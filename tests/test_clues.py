#!/usr/bin/env python3
"""Quick clue count test."""
import time, json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

opts = Options()
opts.add_argument('--headless')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=opts)
driver.execute_cdp_cmd('Network.setCacheDisabled', {'cacheDisabled': True})

try:
    driver.get('http://localhost:9098/index.html')
    time.sleep(2)

    for diff in ['easy','medium','hard']:
        driver.execute_script(f"""document.getElementById('difficulty').value='{diff}';document.getElementById('new-game-btn').click();""")
        time.sleep(3)  # Give generation time

        n = driver.execute_script("""
        var c=0;
        document.querySelectorAll('#sudoku-grid .cell').forEach(function(cell){if(cell.classList.contains('given'))c++;});
        return c;
        """)
        dv = driver.execute_script("return document.getElementById('difficulty').value;")
        print(f'{diff.upper():8s}: clues={n} (dropdown={dv})')

    # Also check: does the JS actually have maxRemovals?
    src = driver.execute_script("return document.querySelector('script[src]').src;")
    print(f'\nLoaded script: {src}')

finally:
    driver.quit()
