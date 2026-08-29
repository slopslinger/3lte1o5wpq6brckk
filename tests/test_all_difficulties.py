#!/usr/bin/env python3
"""Full test of fixed guide on port 9094."""
import time, json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

opts = Options()
opts.add_argument('--headless')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--window-size=1280,1024')

driver = webdriver.Chrome(options=opts)
driver.execute_cdp_cmd('Network.setCacheDisabled', {'cacheDisabled': True})

try:
    driver.get('http://localhost:9094/index.html')
    time.sleep(3)

    # Test Easy
    for diff in ['easy','medium','hard']:
        driver.execute_script(f"""
            document.getElementById('difficulty').value = '{diff}';
            document.getElementById('new-game-btn').click();
        """)
        time.sleep(1.5 if diff == 'expert' else 0.5)

        result = driver.execute_script("""
        var cells = document.querySelectorAll('#sudoku-grid .cell');
        var board = [];
        for (var r = 0; r < 9; r++) {
            board[r] = [];
            for (var c = 0; c < 9; c++) {
                var cell = cells[r * 9 + c];
                if (cell.classList.contains('given') || cell.classList.contains('user-input')) {
                    board[r][c] = parseInt(cell.textContent.trim());
                } else {
                    board[r][c] = 0;
                }
            }
        }
        return JSON.stringify(board);
        """)

        board = json.loads(result)
        clues = sum(1 for r in range(9) for c in range(9) if board[r][c] != 0)

        # Count naked singles
        def is_valid(b, row, col, num):
            for cc in range(9):
                if cc != col and b[row][cc] == num: return False
            for rr in range(9):
                if rr != row and b[rr][col] == num: return False
            sr, sc = (row // 3) * 3, (col // 3) * 3
            for rr in range(sr, sr+3):
                for cc in range(sc, sc+3):
                    if (rr != row or cc != col) and b[rr][cc] == num: return False
            return True

        naked = 0
        hidden = 0
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    cands = [n for n in range(1,10) if is_valid(board, r, c, n)]
                    if len(cands) == 1: naked += 1
        for r in range(9):
            for n in range(1, 10):
                pos = [c for c in range(9) if board[r][c] == 0 and is_valid(board, r, c, n)]
                if len(pos) == 1: hidden += 1

        print(f'{diff.upper()}: clues={clues}, empty={81-clues}, naked_singles={naked}, hidden_singles={hidden}')

    # Now test guide on Easy
    driver.execute_script("""
        document.getElementById('difficulty').value = 'easy';
        document.getElementById('new-game-btn').click();
    """)
    time.sleep(1)

    driver.execute_script("document.getElementById('guide-btn').click();")
    time.sleep(2)
    driver.save_screenshot('/home/goober/.openclaw/workspace/screenshots/guide_09_easy_fixed.png')

    txt = driver.find_element(By.ID, 'guide-explanation').text[:300]
    print(f'\nGuide says: {txt}')

finally:
    driver.quit()
