#!/usr/bin/env python3
"""Debug guide engine on a true Easy puzzle."""
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

try:
    driver.get('http://localhost:9091/index.html')
    time.sleep(3)

    # Ensure Easy is selected and start fresh
    driver.execute_script("""
        document.getElementById('difficulty').value = 'easy';
        document.getElementById('new-game-btn').click();
    """)
    time.sleep(2)

    # Read board state
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
    print(f'Easy puzzle — Clues: {clues}, Empty: {81 - clues}')

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

    naked = []
    cand_dist = {}
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                cands = [n for n in range(1,10) if is_valid(board, r, c, n)]
                d = len(cands)
                cand_dist[d] = cand_dist.get(d, 0) + 1
                if d == 1:
                    naked.append((r+1, c+1, cands[0]))

    print(f'Naked singles: {len(naked)}')
    for ns in naked[:10]:
        print(f'  Cell ({ns[0]},{ns[1]}) = {ns[2]}')
    print(f'Candidate dist: {cand_dist}')

    # Hidden singles (row, col, box)
    hidden_count = 0
    for unit_type in ['row', 'col', 'box']:
        if unit_type == 'row':
            for r in range(9):
                for n in range(1, 10):
                    pos = [c for c in range(9) if board[r][c] == 0 and is_valid(board, r, c, n)]
                    hidden_count += (1 if len(pos) == 1 else 0)
        elif unit_type == 'col':
            for c in range(9):
                for n in range(1, 10):
                    pos = [r for r in range(9) if board[r][c] == 0 and is_valid(board, r, c, n)]
                    hidden_count += (1 if len(pos) == 1 else 0)
        else:
            for br in range(0, 9, 3):
                for bc in range(0, 9, 3):
                    for n in range(1, 10):
                        pos = [(r,c) for r in range(br,br+3) for c in range(bc,bc+3)
                               if board[r][c] == 0 and is_valid(board, r, c, n)]
                        hidden_count += (1 if len(pos) == 1 else 0)
    print(f'Total hidden singles: {hidden_count}')

    # Now test naked pairs
    pairs = 0
    for r in range(9):
        for c in range(9):
            if board[r][c] != 0: continue
            c1 = set(n for n in range(1,10) if is_valid(board, r, c, n))
            if len(c1) != 2: continue
            # Check row peers
            for cc in range(9):
                if cc == c or board[r][cc] != 0: continue
                c2 = set(n for n in range(1,10) if is_valid(board, r, cc, n))
                if c1 == c2: pairs += 1

    print(f'Naked pairs (row only): {pairs}')

finally:
    driver.quit()
