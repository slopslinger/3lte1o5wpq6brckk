#!/usr/bin/env python3
"""Debug: read actual board state from DOM."""
import time, json
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

    result = driver.execute_script("""
    (function() {
        var cells = document.querySelectorAll('#sudoku-grid .cell');
        var board = [];
        var notesCount = 0;
        for (var r = 0; r < 9; r++) {
            board[r] = [];
            for (var c = 0; c < 9; c++) {
                var cell = cells[r * 9 + c];
                var val = cell.textContent.trim();
                var hasNotes = cell.querySelector('.notes-grid') !== null;
                if (hasNotes) notesCount++;
                board[r][c] = val ? parseInt(val) : 0;
            }
        }

        // Print board as text
        var lines = [];
        for (var r = 0; r < 9; r++) {
            var line = '';
            for (var c = 0; c < 9; c++) {
                line += board[r][c] === 0 ? '. ' : board[r][c] + ' ';
            }
            lines.push(line);
            if (r % 3 === 2 && r !== 8) lines.push('---');
        }

        // Validate: count clues
        var clues = 0;
        for (var r = 0; r < 9; r++)
            for (var c = 0; c < 9; c++)
                if (board[r][c] !== 0) clues++;

        return JSON.stringify({
            board: lines.join('\\n'),
            clues: clues,
            empty: 81 - clues,
            notesCells: notesCount
        });
    })()
    """)

    data = json.loads(result)
    print(f'Clues: {data["clues"]}, Empty: {data["empty"]}')
    print(data['board'])

finally:
    driver.quit()
