#!/usr/bin/env python3
"""Test guide mode after solving some cells so naked singles appear."""
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

    # Make several moves using the keyboard to get closer to naked singles
    # Just type numbers — some will be right, some wrong, but guide should fire
    for _ in range(5):
        driver.execute_script("""
          // Fill in first 3 empty cells with guesses
          var cells = document.querySelectorAll('#sudoku-grid .cell');
          let filled = 0;
          for (var i = 0; i < cells.length && filled < 3; i++) {
            if (!cells[i].textContent) {
              cells[i].click();
              var btn = Array.from(document.querySelectorAll('.number-pad button')).find(b => b.dataset.num === '1');
              if (btn) btn.click();
              filled++;
            }
          }
        """)
        time.sleep(0.5)

    # Now open guide
    driver.execute_script("""
      var g = document.getElementById('guide-btn');
      if(g) g.click();
    """)
    time.sleep(2)
    driver.save_screenshot(f'{out}/guide_07_after_progress.png')
    print('✅ Captured guide after making moves')

    # Read what the guide says
    try:
        txt = driver.find_element(By.ID, 'guide-explanation').text[:300]
        print(f'   Guide text: {txt}')
    except Exception as e:
        print(f'   Could not read: {e}')

finally:
    driver.quit()
