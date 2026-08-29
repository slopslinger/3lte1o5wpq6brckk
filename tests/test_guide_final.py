#!/usr/bin/env python3
"""Full guide mode test on port 9095."""
import time, json, os
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
driver.execute_cdp_cmd('Network.setCacheDisabled', {'cacheDisabled': True})

try:
    driver.get('http://localhost:9095/index.html')
    time.sleep(3)

    def get_board():
        return json.loads(driver.execute_script("""
        var cells = document.querySelectorAll('#sudoku-grid .cell');
        var b = [];
        for (var r = 0; r < 9; r++) {
            b[r] = [];
            for (var c = 0; c < 9; c++) {
                var cell = cells[r*9+c];
                if (cell.classList.contains('given') || cell.classList.contains('user-input'))
                    b[r][c] = parseInt(cell.textContent.trim());
                else b[r][c] = 0;
            }
        }
        return JSON.stringify(b);
        """))

    def check_naked_hidden(board):
        def valid(b,r,c,n):
            for x in range(9):
                if x!=c and b[r][x]==n: return False
                if x!=r and b[x][c]==n: return False
            sr,sc=(r//3)*3,(c//3)*3
            for rr in range(sr,sr+3):
                for cc in range(sc,sc+3):
                    if (rr!=r or cc!=c) and b[rr][cc]==n: return False
            return True

        naked=[]; hidden_row=[]; hidden_col=[]; hidden_box=[]
        for r in range(9):
            for c in range(9):
                if board[r][c]==0:
                    cands=[n for n in range(1,10) if valid(board,r,c,n)]
                    if len(cands)==1: naked.append((r+1,c+1,cands[0]))
        for r in range(9):
            for n in range(1,10):
                pos=[c for c in range(9) if board[r][c]==0 and valid(board,r,c,n)]
                if len(pos)==1: hidden_row.append((r+1,pos[0]+1,n))
        for c in range(9):
            for n in range(1,10):
                pos=[r for r in range(9) if board[r][c]==0 and valid(board,r,c,n)]
                if len(pos)==1: hidden_col.append((pos[0]+1,c+1,n))

        return naked, hidden_row+hidden_col

    # Test all difficulties
    for diff in ['easy','medium','hard','expert']:
        driver.execute_script(f"""
            document.getElementById('difficulty').value = '{diff}';
            document.getElementById('new-game-btn').click();
        """)
        time.sleep(1 if diff!='expert' else 3)

        board = get_board()
        clues = sum(1 for r in range(9) for c in range(9) if board[r][c]!=0)
        naked, hidden = check_naked_hidden(board)
        print(f'{diff.upper():8s}: clues={clues:2d}, empty={81-clues:2d}, naked={len(naked):2d}, hidden={len(hidden):2d}')

    # Screenshot 1: Easy start
    driver.execute_script("""document.getElementById('difficulty').value='easy';document.getElementById('new-game-btn').click();""")
    time.sleep(1)
    driver.save_screenshot(f'{out}/guide_final_01_easy_start.png')
    print('\n✅ Screenshot 1: Easy start')

    # Open guide on fresh Easy
    driver.execute_script("document.getElementById('guide-btn').click();")
    time.sleep(2)
    driver.save_screenshot(f'{out}/guide_final_02_guide_open.png')
    txt = driver.find_element(By.ID, 'guide-explanation').text[:300]
    print(f'   Guide: {txt}')

    # Navigate to next hint
    driver.execute_script("document.getElementById('guide-next-btn').click();")
    time.sleep(1)
    driver.save_screenshot(f'{out}/guide_final_03_first_hint.png')
    txt = driver.find_element(By.ID, 'guide-explanation').text[:300]
    print(f'   First hint: {txt}')

    # Navigate again
    driver.execute_script("document.getElementById('guide-next-btn').click();")
    time.sleep(1)
    driver.save_screenshot(f'{out}/guide_final_04_second_hint.png')
    txt = driver.find_element(By.ID, 'guide-explanation').text[:300]
    print(f'   Second hint: {txt}')

finally:
    driver.quit()
    print('\nDone!')
