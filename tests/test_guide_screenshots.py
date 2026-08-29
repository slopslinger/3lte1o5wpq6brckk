#!/usr/bin/env python3
"""Selenium screenshots of the Sudoku Strategy Guide mode."""
import os, time, sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

out_dir = '/home/goober/.openclaw/workspace/screenshots'
os.makedirs(out_dir, exist_ok=True)

opts = Options()
opts.add_argument('--headless')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--window-size=1280,1024')

driver = webdriver.Chrome(options=opts)

try:
    driver.get('http://localhost:9091/index.html')
    wait = WebDriverWait(driver, 5)

    # Wait for grid to render
    cells = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'cell')))
    time.sleep(1)

    # Screenshot 1: Game start (dark theme default)
    driver.save_screenshot(f'{out_dir}/guide_01_start.png')
    print('✅ 1/5 — Start screen captured')

    # Make a couple moves so guide has something to work with
    number_pad = driver.find_elements(By.CSS_SELECTOR, '.number-pad button')
    # grid_cells not used below, skipping

    # Actually let's use JavaScript clicks on specific cells and numbers
    time.sleep(1)

    # Click cell (0,4) - first row, middle-ish
    for cell in driver.find_elements(By.CSS_SELECTOR, '#sudoku-grid .cell'):
        if cell.get_attribute('data-row') == '0' and cell.get_attribute('data-col') == '4':
            driver.execute_script('arguments[0].click()', cell)
            break
    time.sleep(0.3)

    # Click number 5 on pad
    for btn in driver.find_elements(By.CSS_SELECTOR, '.number-pad button'):
        if btn.get_attribute('data-num') == '5':
            driver.execute_script('arguments[0].click()', btn)
            break
    time.sleep(0.5)

    # Click another cell
    for cell in driver.find_elements(By.CSS_SELECTOR, '#sudoku-grid .cell'):
        if cell.get_attribute('data-row') == '1' and cell.get_attribute('data-col') == '2':
            driver.execute_script('arguments[0].click()', cell)
            break
    time.sleep(0.3)

    # Click number 7 on pad
    for btn in driver.find_elements(By.CSS_SELECTOR, '.number-pad button'):
        if btn.get_attribute('data-num') == '7':
            driver.execute_script('arguments[0].click()', btn)
            break
    time.sleep(0.5)

    # Screenshot 2: After making a few moves
    driver.save_screenshot(f'{out_dir}/guide_02_after_moves.png')
    print('✅ 2/5 — After moves captured')

    # Click the Guide button
    try:
        guide_btn = wait.until(EC.element_to_be_clickable((By.ID, 'guide-btn')))
        driver.execute_script('arguments[0].click()', guide_btn)
        time.sleep(1.5)

        # Screenshot 3: Guide panel open with first hint
        driver.save_screenshot(f'{out_dir}/guide_03_guide_panel_open.png')
        print('✅ 3/5 — Guide panel open captured')

        # Check what the guide says
        try:
            explanation = driver.find_element(By.ID, 'guide-explanation')
            print(f'   Guide says: {explanation.text[:200]}')
        except:
            print('   (could not read guide explanation)')

        # Screenshot 4: Next hint
        try:
            next_btn = driver.find_element(By.ID, 'guide-next-btn')
            if next_btn:
                driver.execute_script('arguments[0].click()', next_btn)
                time.sleep(1)
                driver.save_screenshot(f'{out_dir}/guide_04_next_hint.png')
                print('✅ 4/5 — Next hint captured')
        except Exception as e:
            print(f'   ⚠️ Could not click next: {e}')

    except Exception as e:
        print(f'⚠️ Guide button issue: {e}')

    # Screenshot 5: Switch to Ocean theme
    try:
        close_btn = driver.find_element(By.ID, 'guide-close-btn')
        if close_btn:
            driver.execute_script('arguments[0].click()', close_btn)
            time.sleep(0.5)
    except:
        pass

    # Change theme to ocean
    driver.execute_script("""
      var sel = document.getElementById('theme-select');
      if(sel) { sel.value='ocean'; sel.dispatchEvent(new Event('change')); }
    """)
    time.sleep(1)
    driver.save_screenshot(f'{out_dir}/guide_05_ocean_theme.png')
    print('✅ 5/5 — Ocean theme captured')

    # Switch to Hard difficulty and show guide on harder puzzle
    driver.execute_script("""
      document.getElementById('difficulty').value='hard';
      document.getElementById('new-game-btn').click();
    """)
    time.sleep(2)
    driver.execute_script("document.getElementById('guide-btn').click();")
    time.sleep(1.5)
    driver.save_screenshot(f'{out_dir}/guide_06_hard_guide.png')
    print('✅ 6/5 — Hard puzzle guide captured')

    print('\nDone! Screenshots saved.')

except Exception as e:
    print(f'Error: {e}')
    import traceback; traceback.print_exc()
finally:
    driver.quit()
