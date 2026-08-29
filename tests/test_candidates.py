#!/usr/bin/env python3
"""Debug guide engine candidates on a fresh puzzle."""
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

    # Read board from DOM cells - given cells have class "given" and textContent
    # Empty cells may contain notes-grid children, so read carefully
    result = driver.execute_script("""
    var cells = document.querySelectorAll('#sudoku-grid .cell');
    var board = [];
    for (var r = 0; r < 9; r++) {
        board[r] = [];
        for (var c = 0; c < 9; c++) {
            var cell = cells[r * 9 + c];
            // Given cells have the value as direct text, empty cells might have notes-grid child
            var given = cell.classList.contains('given');
            var userInp = cell.classList.contains('user-input');
            if (given || userInp) {
                board[r][c] = parseInt(cell.textContent.trim());
            } else {
                board[r][c] = 0;
            }
        }
    }
    return JSON.stringify(board);
    """)

    import json
    board = json.loads(result)

    # Count clues
    clues = sum(1 for r in range(9) for c in range(9) if board[r][c] != 0)
    print(f'Clues: {clues}, Empty: {81 - clues}')

    # Check naked singles and hidden singles using same logic as the guide
    def is_valid(b, row, col, num):
        for cc in range(9):
            if cc != col and b[row][cc] == num:
                return False
        for rr in range(9):
            if rr != row and b[rr][col] == num:
                return False
        sr, sc = (row // 3) * 3, (col // 3) * 3
        for rr in range(sr, sr+3):
            for cc in range(sc, sc+3):
                if (rr != row or cc != col) and b[rr][cc] == num:
                    return False
        return True

    naked = []
    cand_dist = {}
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                cands = [n for n in range(1, 10) if is_valid(board, r, c, n)]
                dist = len(cands)
                cand_dist[dist] = cand_dist.get(dist, 0) + 1
                if len(cands) == 1:
                    naked.append((r+1, c+1, cands[0]))

    print(f'Naked singles: {len(naked)}')
    for ns in naked[:5]:
        print(f'  Cell ({ns[0]},{ns[1]}) = {ns[2]}')
    print(f'Candidate distribution: {cand_dist}')

    # Hidden singles check
    hidden = []
    for r in range(9):
        for n in range(1, 10):
            positions = []
            for c in range(9):
                if board[r][c] == 0:
                    if is_valid(board, r, c, n):
                        positions.append(c+1)
            if len(positions) == 1:
                hidden.append((r+1, positions[0], n))

    print(f'Hidden singles (rows): {len(hidden)}')
    for h in hidden[:5]:
        print(f'  Row {h[0]}, col {h[1]} = {h[2]}')

finally:
    driver.quit()
