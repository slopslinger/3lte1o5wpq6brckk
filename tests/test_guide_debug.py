#!/usr/bin/env python3
"""Debug guide engine by injecting console logs."""
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

    # Use Selenium logs to capture console output
    debug_js = """
    (function() {
        // We need to peek inside the IIFE's scope.
        // The game is wrapped in (function(){...})(); so we can't access internals directly.
        // Instead, let's manually replicate the candidate logic on the visible grid.

        var cells = document.querySelectorAll('#sudoku-grid .cell');
        var board = [];
        for (var r = 0; r < 9; r++) {
            board[r] = [];
            for (var c = 0; c < 9; c++) {
                var idx = r * 9 + c;
                var val = cells[idx].textContent;
                board[r][c] = val ? parseInt(val) : 0;
            }
        }

        // Count candidates for each empty cell
        function isValid(b, row, col, num) {
            for (var c = 0; c < 9; c++) if (c !== col && b[row][c] === num) return false;
            for (var r = 0; r < 9; r++) if (r !== row && b[r][col] === num) return false;
            var sr = Math.floor(row/3)*3, sc = Math.floor(col/3)*3;
            for (var rr = sr; rr < sr+3; rr++)
                for (var cc = sc; cc < sc+3; cc++)
                    if ((rr !== row || cc !== col) && b[rr][cc] === num) return false;
            return true;
        }

        var nakedSingles = [];
        var hiddenSingles = [];
        var totalEmpty = 0;
        var minCandidates = 9;
        var candidateDist = {};

        for (var r = 0; r < 9; r++) {
            for (var c = 0; c < 9; c++) {
                if (board[r][c] === 0) {
                    totalEmpty++;
                    var cands = [];
                    for (var n = 1; n <= 9; n++) {
                        if (isValid(board, r, c, n)) cands.push(n);
                    }
                    candidateDist[cands.length] = (candidateDist[cands.length]||0) + 1;
                    if (cands.length < minCandidates) minCandidates = cands.length;
                    if (cands.length === 1) {
                        nakedSingles.push({r:r+1, c:c+1, v:cands[0]});
                    }
                }
            }
        }

        // Check hidden singles too
        for (var r = 0; r < 9; r++) {
            for (var n = 1; n <= 9; n++) {
                var positions = [];
                for (var c = 0; c < 9; c++) {
                    if (board[r][c] === 0) {
                        var cands2 = [];
                        for (var nn = 1; nn <= 9; nn++)
                            if (isValid(board, r, c, nn)) cands2.push(nn);
                        if (cands2.includes(n)) positions.push(c+1);
                    }
                }
                if (positions.length === 1) {
                    hiddenSingles.push({row:r+1, col:positions[0], val:n});
                }
            }
        }

        console.log('=== GUIDE ENGINE DEBUG ===');
        console.log('Empty cells:', totalEmpty);
        console.log('Min candidates:', minCandidates);
        console.log('Candidate distribution:', JSON.stringify(candidateDist));
        console.log('Naked singles found:', nakedSingles.length);
        if (nakedSingles.length > 0) console.log('Naked singles:', JSON.stringify(nakedSingles.slice(0,5)));
        console.log('Hidden singles found:', hiddenSingles.length);
        if (hiddenSingles.length > 0) console.log('Hidden singles (first 5):', JSON.stringify(hiddenSingles.slice(0,5)));
        console.log('=== END DEBUG ===');

        // Return a summary for Selenium to capture
        return JSON.stringify({
            empty: totalEmpty,
            minCands: minCandidates,
            candDist: candidateDist,
            nakedSingles: nakedSingles.length,
            hiddenSingles: hiddenSingles.length,
            firstNaked: nakedSingles.slice(0,3),
            firstHidden: hiddenSingles.slice(0,3)
        });
    })()
    """

    result = driver.execute_script(debug_js)
    print(f'\nDebug result: {result}')

finally:
    driver.quit()
