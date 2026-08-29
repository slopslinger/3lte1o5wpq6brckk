#!/usr/bin/env python3
"""Guide test: fill cells CORRECTLY via hints, then check guide."""
import time, os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

out = '/home/goober/.openclaw/workspace/screenshots'
opts = Options()
opts.add_argument('--headless')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--window-size=1280,1024')

driver = webdriver.Chrome(options=opts)

try:
    driver.get('http://localhost:9091/index.html')
    WebDriverWait(driver, 5).until(
        lambda d: d.execute_script("return document.getElementById('sudoku-grid').children.length") == 81
    )
    time.sleep(1)

    # Use hints to fill in cells correctly (hints always give right answer)
    # Each hint fills one cell, so after several hints we should have naked singles
    for i in range(6):
        # Click a random empty cell, then use hint button
        driver.execute_script("""
          var cells = document.querySelectorAll('#sudoku-grid .cell');
          for (var c of cells) {
            if (!c.textContent || c.classList.contains('user-input')) continue;
            // Find first non-given empty cell
            if (!c.classList.contains('given') && !c.textContent) {
              c.click();
              break;
            }
          }
        """)
        time.sleep(0.3)

        # Click hint button
        hint_btn = driver.find_element(By.ID, 'hint-btn')
        if hint_btn:
            driver.execute_script('arguments[0].click()', hint_btn)
            time.sleep(0.5)
            print(f'  Hint {i+1} used')

    # Now open guide
    driver.execute_script("document.getElementById('guide-btn').click();")
    time.sleep(2)
    driver.save_screenshot(f'{out}/guide_08_after_hints.png')
    print('✅ Captured guide after 6 hints')

    try:
        txt = driver.find_element(By.ID, 'guide-explanation').text[:300]
        print(f'   Guide says: {txt}')
    except Exception as e:
        print(f'   Could not read: {e}')

finally:
    driver.quit()
