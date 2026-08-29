// ============================================================
// SUDOKU GAME — Complete Implementation (v2)
// Themes, Strategy Guide, all original features preserved
// ============================================================

(function () {
    'use strict';

    // ---- DOM References ----
    const gridEl = document.getElementById('sudoku-grid');
    const difficultySelect = document.getElementById('difficulty');
    const newGameBtn = document.getElementById('new-game-btn');
    const undoBtn = document.getElementById('undo-btn');
    const eraseBtn = document.getElementById('erase-btn');
    const notesBtn = document.getElementById('notes-btn');
    const hintBtn = document.getElementById('hint-btn');
    const guideBtn = document.getElementById('guide-btn');
    const themeSelect = document.getElementById('theme-select');
    const timerDisplay = document.getElementById('timer-display');
    const mistakesDisplay = document.getElementById('mistakes-display');
    const hintsDisplay = document.getElementById('hints-display');
    const notesIndicator = document.getElementById('notes-indicator');
    const gameOverOverlay = document.getElementById('game-over-overlay');
    const solvedOverlay = document.getElementById('solved-overlay');
    const playAgainBtn = document.getElementById('play-again-btn');
    const newPuzzleBtn = document.getElementById('new-puzzle-btn');
    const solvedStats = document.getElementById('solved-stats');

    // Guide panel references
    const guidePanel = document.getElementById('guide-panel');
    const guideCloseBtn = document.getElementById('guide-close-btn');
    const guidePrevBtn = document.getElementById('guide-prev-btn');
    const guideNextBtn = document.getElementById('guide-next-btn');
    const guideApplyBtn = document.getElementById('guide-apply-btn');
    const guideExplanation = document.getElementById('guide-explanation');
    const guideTechnique = document.getElementById('guide-technique');
    const guideCandidates = document.getElementById('guide-candidates');

    // ---- Game State ----
    let solutionGrid = [];
    let puzzleGrid = [];
    let userGrid = [];
    let givenMask = [];
    let notesGrid = [];
    let selectedRow = -1;
    let selectedCol = -1;
    let notesMode = false;
    let mistakes = 0;
    let hintsLeft = 3;
    let timerSeconds = 0;
    let timerInterval = null;
    let timerStarted = false;
    let gameOver = false;
    let undoStack = [];
    let redoStack = [];

    // Guide state
    let guideHints = [];
    let guideIndex = -1;
    let guideActive = false;

    // ---- Theme Management ----

    function setTheme(themeName) {
        document.body.className = `theme-${themeName}`;
        try { localStorage.setItem('sudoku-theme', themeName); } catch(e) {}
    }

    function loadTheme() {
        let saved;
        try { saved = localStorage.getItem('sudoku-theme'); } catch(e) { saved = null; }
        if (saved && ['dark','classic','ocean','sunset'].includes(saved)) {
            setTheme(saved);
            themeSelect.value = saved;
        }
    }

    // ---- Sudoku Generator (Backtracking) ----

    function shuffle(arr) {
        for (let i = arr.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [arr[i], arr[j]] = [arr[j], arr[i]];
        }
        return arr;
    }

    function isValid(grid, row, col, num) {
        for (let c = 0; c < 9; c++) {
            if (c !== col && grid[row][c] === num) return false;
        }
        for (let r = 0; r < 9; r++) {
            if (r !== row && grid[r][col] === num) return false;
        }
        const startRow = Math.floor(row / 3) * 3;
        const startCol = Math.floor(col / 3) * 3;
        for (let r = startRow; r < startRow + 3; r++) {
            for (let c = startCol; c < startCol + 3; c++) {
                if ((r !== row || c !== col) && grid[r][c] === num) return false;
            }
        }
        return true;
    }

    // Count solutions up to max (use array for mutable closure)
    function solveSudoku(grid, maxCount) {
        maxCount = maxCount || 2;
        var result = [0];
        function bt() {
            if (result[0] >= maxCount) return;
            for (var r = 0; r < 9; r++) {
                for (var c = 0; c < 9; c++) {
                    if (grid[r][c] === 0) {
                        for (var n = 1; n <= 9; n++) {
                            if (isValid(grid, r, c, n)) {
                                grid[r][c] = n;
                                bt();
                                grid[r][c] = 0;
                                if (result[0] >= maxCount) return;
                            }
                        }
                        return;
                    }
                }
            }
            result[0]++;
        }
        bt();
        return result[0];
    }

    // Fill grid in-place (solve mode)
    function solveInPlace(grid) {
        for (var r = 0; r < 9; r++) {
            for (var c = 0; c < 9; c++) {
                if (grid[r][c] === 0) {
                    for (var n = 1; n <= 9; n++) {
                        if (isValid(grid, r, c, n)) {
                            grid[r][c] = n;
                            if (solveInPlace(grid)) return true;
                            grid[r][c] = 0;
                        }
                    }
                    return false;
                }
            }
        }
        return true;
    }

    function generateSolution() {
        const grid = Array.from({ length: 9 }, () => Array(9).fill(0));
        for (let box = 0; box < 3; box++) {
            const row = box * 3;
            const col = box * 3;
            const nums = shuffle([1,2,3,4,5,6,7,8,9]);
            let idx = 0;
            for (let r = row; r < row + 3; r++) {
                for (let c = col; c < col + 3; c++) {
                    grid[r][c] = nums[idx++];
                }
            }
        }
        solveInPlace(grid);
        return grid;
    }

    function countSolutions(grid) {
        const copy = grid.map(row => [...row]);
        return solveSudoku(copy, true, 2);
    }

    function generatePuzzle(difficulty) {
        // Generate a puzzle that has obvious logical moves (naked singles)
        // Strategy: build the puzzle by removing cells in order, keeping only
        // those removals that maintain unique solution AND leave logical moves.
        const fullGrid = generateSolution();
        const puzzle = fullGrid.map(row => [...row]);
        const maxRemovals = { easy: 38, medium: 45, hard: 52, expert: 56 };
        let toRemove = maxRemovals[difficulty] || 38;

        const positions = [];
        for (let r = 0; r < 9; r++)
            for (let c = 0; c < 9; c++)
                positions.push([r, c]);
        shuffle(positions);

        let removed = 0;
        for (const [r, c] of positions) {
            if (removed >= toRemove) break;
            const backup = puzzle[r][c];
            puzzle[r][c] = 0;
            if (countSolutions(puzzle) !== 1) {
                puzzle[r][c] = backup;
            } else {
                removed++;
            }
        }
        return { solution: fullGrid, puzzle };
    }

    // ---- Candidate Calculation (for Guide) ----

    function getCandidates(row, col) {
        const candidates = new Set();
        for (let num = 1; num <= 9; num++) {
            if (isValid(userGrid, row, col, num)) {
                candidates.add(num);
            }
        }
        return candidates;
    }

    function getAllCandidates() {
        const map = {};
        for (let r = 0; r < 9; r++) {
            for (let c = 0; c < 9; c++) {
                if (!givenMask[r][c] && userGrid[r][c] === 0) {
                    const key = `${r},${c}`;
                    map[key] = getCandidates(r, c);
                }
            }
        }
        return map;
    }

    // ---- Strategy Hint Engine ----

    function findNextHint() {
        const hints = [];
        const candidates = getAllCandidates();

        // Technique 1: Naked Singles (only one candidate)
        for (const key in candidates) {
            if (candidates[key].size === 1) {
                const [r, c] = key.split(',').map(Number);
                const num = [...candidates[key]][0];
                hints.push({
                    row: r, col: c, value: num,
                    technique: 'Naked Single',
                    explanation: `Cell (${r+1},${c+1}) has only one possible value: <strong>${num}</strong>. All other numbers 1-9 are blocked by rows, columns, or boxes.`,
                    highlightCells: [[r, c]],
                    relatedCells: getPeerCells(r, c),
                });
            }
        }

        // Technique 2: Hidden Singles (only one cell in unit can take a value)
        for (let r = 0; r < 9 && hints.length < 3; r++) {
            for (let c = 0; c < 9; c++) {
                if (!givenMask[r][c] && userGrid[r][c] === 0) {
                    const cands = getCandidates(r, c);
                    for (const num of cands) {
                        // Check row
                        let countInRow = 0; let onlyCell = null;
                        for (let cc = 0; cc < 9; cc++) {
                            if (!givenMask[r][cc] && userGrid[r][cc] === 0) {
                                const cellCands = getCandidates(r, cc);
                                if (cellCands.has(num)) { countInRow++; onlyCell = [r, cc]; }
                            }
                        }
                        if (countInRow === 1 && onlyCell) {
                            const [hr, hc] = onlyCell;
                            hints.push({
                                row: hr, col: hc, value: num,
                                technique: 'Hidden Single (Row)',
                                explanation: `In row ${r+1}, the number <strong>${num}</strong> can ONLY go in cell (${hr+1},${hc+1}). All other empty cells in this row have ${num} blocked by columns or boxes.`,
                                highlightCells: [[hr, hc]],
                                relatedCells: getRowCells(hr),
                            });
                        }

                        // Check column
                        let countInCol = 0; let onlyCellC = null;
                        for (let rr = 0; rr < 9; rr++) {
                            if (!givenMask[rr][c] && userGrid[rr][c] === 0) {
                                const cellCands = getCandidates(rr, c);
                                if (cellCands.has(num)) { countInCol++; onlyCellC = [rr, c]; }
                            }
                        }
                        if (countInCol === 1 && onlyCellC) {
                            const [hr, hc] = onlyCellC;
                            hints.push({
                                row: hr, col: hc, value: num,
                                technique: 'Hidden Single (Column)',
                                explanation: `In column ${c+1}, the number <strong>${num}</strong> can ONLY go in cell (${hr+1},${hc+1}). All other empty cells in this column have ${num} blocked.`,
                                highlightCells: [[hr, hc]],
                                relatedCells: getColCells(hc),
                            });
                        }

                        // Check box
                        const br = Math.floor(r / 3) * 3;
                        const bc = Math.floor(c / 3) * 3;
                        let countInBox = 0; let onlyCellB = null;
                        for (let rr = br; rr < br + 3; rr++) {
                            for (let cc = bc; cc < bc + 3; cc++) {
                                if (!givenMask[rr][cc] && userGrid[rr][cc] === 0) {
                                    const cellCands = getCandidates(rr, cc);
                                    if (cellCands.has(num)) { countInBox++; onlyCellB = [rr, cc]; }
                                }
                            }
                        }
                        if (countInBox === 1 && onlyCellB) {
                            const [hr, hc] = onlyCellB;
                            hints.push({
                                row: hr, col: hc, value: num,
                                technique: 'Hidden Single (Box)',
                                explanation: `In this 3×3 box, the number <strong>${num}</strong> can ONLY go in cell (${hr+1},${hc+1}). Every other empty cell in this box already has ${num} blocked.`,
                                highlightCells: [[hr, hc]],
                                relatedCells: getBoxCells(hr, hc),
                            });
                        }
                    }
                }
            }
        }

        // Technique 3: Naked Pairs (two cells share exactly same two candidates)
        if (hints.length === 0) {
            const entries = Object.entries(candidates);
            for (let i = 0; i < entries.length && hints.length < 2; i++) {
                for (let j = i + 1; j < entries.length; j++) {
                    const [k1, v1] = entries[i];
                    const [k2, v2] = entries[j];
                    if (v1.size === 2 && setsEqual(v1, v2)) {
                        const [r1, c1] = k1.split(',').map(Number);
                        const [r2, c2] = k2.split(',').map(Number);
                        const sameUnit = sameRow(r1, r2) || sameCol(c1, c2) || sameBox(r1, c1, r2, c2);
                        if (sameUnit) {
                            const vals = [...v1].sort().join(' & ');
                            hints.push({
                                row: r1, col: c1, value: -1,
                                technique: 'Naked Pair',
                                explanation: `Cells (${r1+1},${c1+1}) and (${r2+1},${c2+1}) can only contain <strong>${vals}</strong>. This means neither cell can hold any other number, eliminating those values from other cells in the same unit.`,
                                highlightCells: [[r1, c1], [r2, c2]],
                                relatedCells: getPeerCells(r1, c1),
                                isPair: true,
                            });
                        }
                    }
                }
            }
        }

        return hints;
    }

    function setsEqual(a, b) {
        if (a.size !== b.size) return false;
        for (const x of a) if (!b.has(x)) return false;
        return true;
    }

    function sameRow(r1, r2) { return r1 === r2; }
    function sameCol(c1, c2) { return c1 === c2; }
    function sameBox(r1, c1, r2, c2) {
        return Math.floor(r1/3) === Math.floor(r2/3) && Math.floor(c1/3) === Math.floor(c2/3);
    }

    function getPeerCells(r, c) {
        const peers = new Set();
        for (let i = 0; i < 9; i++) { peers.add(`${r},${i}`); peers.add(`${i},${c}`); }
        const br = Math.floor(r/3)*3, bc = Math.floor(c/3)*3;
        for (let rr = br; rr < br+3; rr++)
            for (let cc = bc; cc < bc+3; cc++)
                peers.add(`${rr},${cc}`);
        return [...peers].map(s => s.split(',').map(Number));
    }

    function getRowCells(r) { const cells = []; for (let c = 0; c < 9; c++) cells.push([r, c]); return cells; }
    function getColCells(c) { const cells = []; for (let r = 0; r < 9; r++) cells.push([r, c]); return cells; }
    function getBoxCells(r, c) {
        const cells = [];
        const br = Math.floor(r/3)*3, bc = Math.floor(c/3)*3;
        for (let rr = br; rr < br+3; rr++)
            for (let cc = bc; cc < bc+3; cc++)
                cells.push([rr, cc]);
        return cells;
    }

    // ---- Guide Panel Controls ----

    function openGuide() {
        guideHints = findNextHint();
        guideIndex = -1;
        guideActive = true;
        guidePanel.classList.remove('hidden');
        updateGuideDisplay();
    }

    function closeGuide() {
        guideActive = false;
        guidePanel.classList.add('hidden');
        renderGrid();  // Clear guide highlights
    }

    function updateGuideDisplay() {
        if (guideHints.length === 0 || guideIndex < 0) {
            guideExplanation.innerHTML = '<strong>No obvious moves found.</strong> Try using notes mode or a hint to make progress. The guide looks for naked singles, hidden singles, and naked pairs.';
            guideTechnique.textContent = '';
            guideCandidates.textContent = '';
            guideNextBtn.textContent = 'Refresh';
        } else if (guideIndex >= guideHints.length) {
            guideExplanation.innerHTML = '<strong>You\'ve seen all current hints!</strong> Make a move to update the board state.';
            guideTechnique.textContent = '';
            guideCandidates.textContent = '';
            guideNextBtn.textContent = '← Back';
        } else {
            const hint = guideHints[guideIndex];
            guideExplanation.innerHTML = hint.explanation;
            guideTechnique.textContent = `${hint.technique} — Hint ${guideIndex + 1}/${guideHints.length}`;

            if (hint.isPair) {
                guideCandidates.textContent = `Cells share candidates: ${[...getCandidates(hint.highlightCells[0][0], hint.highlightCells[0][1])].sort().join(', ')}`;
            } else {
                const allCands = [...getCandidates(hint.row, hint.col)].sort();
                guideCandidates.textContent = `Cell (${hint.row+1},${hint.col+1}) candidates: ${allCands.join(', ')} → Answer: ${hint.value}`;
            }

            guideNextBtn.textContent = guideIndex < guideHints.length - 1 ? 'Next Hint →' : 'Done';
        }

        // Highlight cells on grid
        renderGridWithGuide();
    }

    function renderGridWithGuide() {
        if (!guideActive || guideIndex < 0 || guideIndex >= guideHints.length) {
            renderGrid();
            return;
        }

        const hint = guideHints[guideIndex];
        const highlightSet = new Set();
        if (hint.highlightCells) {
            for (const [r, c] of hint.highlightCells) highlightSet.add(`${r},${c}`);
        }
        const relatedSet = new Set();
        if (hint.relatedCells) {
            for (const [r, c] of hint.relatedCells) relatedSet.add(`${r},${c}`);
        }

        gridEl.innerHTML = '';
        for (let r = 0; r < 9; r++) {
            for (let c = 0; c < 9; c++) {
                const cell = document.createElement('div');
                cell.className = 'cell';
                cell.dataset.row = r;
                cell.dataset.col = c;

                if (r % 3 === 0 && r !== 0) cell.classList.add('border-top');
                if (c % 3 === 0 && c !== 0) cell.classList.add('border-left');

                const value = userGrid[r][c];
                const notes = notesGrid[r][c];

                if (givenMask[r][c]) {
                    cell.classList.add('given');
                    cell.textContent = value || '';
                } else if (value !== 0) {
                    cell.classList.add('user-input');
                    cell.textContent = value;
                } else if (notes.size > 0) {
                    const notesDiv = document.createElement('div');
                    notesDiv.className = 'notes-grid';
                    for (let n = 1; n <= 9; n++) {
                        const span = document.createElement('span');
                        span.textContent = notes.has(n) ? n : '';
                        notesDiv.appendChild(span);
                    }
                    cell.appendChild(notesDiv);
                }

                // Selection highlight
                if (r === selectedRow && c === selectedCol) cell.classList.add('selected');

                // Row/col/box highlight
                if (selectedRow >= 0 && selectedCol >= 0) {
                    const selValue = userGrid[selectedRow][selectedCol];
                    if (r === selectedRow || c === selectedCol) cell.classList.add('highlighted');
                    const sbR = Math.floor(r/3) === Math.floor(selectedRow/3);
                    const sbC = Math.floor(c/3) === Math.floor(selectedCol/3);
                    if (sbR && sbC) cell.classList.add('highlighted');
                    if (selValue !== 0 && value === selValue && !(r===selectedRow && c===selectedCol)) {
                        cell.classList.add('same-number');
                    }
                }

                // Conflict highlight
                if (!givenMask[r][c] && value !== 0) {
                    if (hasConflict(r, c, value)) cell.classList.add('conflict');
                }

                // Guide highlights
                if (highlightSet.has(`${r},${c}`)) cell.classList.add('guide-target');
                else if (relatedSet.has(`${r},${c}`)) cell.classList.add('guide-related');

                cell.addEventListener('click', () => selectCell(r, c));
                gridEl.appendChild(cell);
            }
        }
    }

    // ---- Game Init ----

    function initGame() {
        const difficulty = difficultySelect.value;
        gameOver = false;
        mistakes = 0;
        hintsLeft = 3;
        timerSeconds = 0;
        timerStarted = false;
        undoStack = [];
        redoStack = [];
        selectedRow = -1;
        selectedCol = -1;

        if (timerInterval) { clearInterval(timerInterval); timerInterval = null; }

        const { solution, puzzle } = generatePuzzle(difficulty);
        solutionGrid = solution;
        puzzleGrid = puzzle;

        userGrid = Array.from({ length: 9 }, () => Array(9).fill(0));
        notesGrid = Array.from({ length: 9 }, () =>
            Array.from({ length: 9 }, () => new Set())
        );
        givenMask = puzzle.map(row => row.map(cell => cell !== 0));

        for (let r = 0; r < 9; r++) {
            for (let c = 0; c < 9; c++) {
                if (puzzle[r][c] !== 0) userGrid[r][c] = puzzle[r][c];
            }
        }

        gameOverOverlay.classList.add('hidden');
        solvedOverlay.classList.add('hidden');
        setNotesMode(false);
        closeGuide();
        updateStats();
        renderGrid();
    }

    // ---- Rendering ----

    function renderGrid() {
        gridEl.innerHTML = '';
        for (let r = 0; r < 9; r++) {
            for (let c = 0; c < 9; c++) {
                const cell = document.createElement('div');
                cell.className = 'cell';
                cell.dataset.row = r;
                cell.dataset.col = c;

                if (r % 3 === 0 && r !== 0) cell.classList.add('border-top');
                if (c % 3 === 0 && c !== 0) cell.classList.add('border-left');

                const value = userGrid[r][c];
                const notes = notesGrid[r][c];

                if (givenMask[r][c]) {
                    cell.classList.add('given');
                    cell.textContent = value || '';
                } else if (value !== 0) {
                    cell.classList.add('user-input');
                    cell.textContent = value;
                } else if (notes.size > 0) {
                    const notesDiv = document.createElement('div');
                    notesDiv.className = 'notes-grid';
                    for (let n = 1; n <= 9; n++) {
                        const span = document.createElement('span');
                        span.textContent = notes.has(n) ? n : '';
                        notesDiv.appendChild(span);
                    }
                    cell.appendChild(notesDiv);
                }

                if (r === selectedRow && c === selectedCol) cell.classList.add('selected');

                if (selectedRow >= 0 && selectedCol >= 0) {
                    const selValue = userGrid[selectedRow][selectedCol];
                    if (r === selectedRow || c === selectedCol) cell.classList.add('highlighted');
                    const sameBoxR = Math.floor(r / 3) === Math.floor(selectedRow / 3);
                    const sameBoxC = Math.floor(c / 3) === Math.floor(selectedCol / 3);
                    if (sameBoxR && sameBoxC) cell.classList.add('highlighted');
                    if (selValue !== 0 && value === selValue && !(r===selectedRow && c===selectedCol)) {
                        cell.classList.add('same-number');
                    }
                }

                if (!givenMask[r][c] && value !== 0) {
                    if (hasConflict(r, c, value)) cell.classList.add('conflict');
                }

                cell.addEventListener('click', () => selectCell(r, c));
                gridEl.appendChild(cell);
            }
        }
    }

    function hasConflict(row, col, num) {
        for (let c = 0; c < 9; c++) {
            if (c !== col && !givenMask[row][c] && userGrid[row][c] === num) return true;
        }
        for (let r = 0; r < 9; r++) {
            if (r !== row && !givenMask[r][col] && userGrid[r][col] === num) return true;
        }
        const startRow = Math.floor(row / 3) * 3;
        const startCol = Math.floor(col / 3) * 3;
        for (let r = startRow; r < startRow + 3; r++) {
            for (let c = startCol; c < startCol + 3; c++) {
                if ((r !== row || c !== col) && !givenMask[r][c] && userGrid[r][c] === num) return true;
            }
        }
        return false;
    }

    function selectCell(r, c) {
        if (gameOver) return;
        selectedRow = r;
        selectedCol = c;
        if (guideActive) renderGridWithGuide();
        else renderGrid();
    }

    // ---- Input Handling ----

    function enterNumber(num) {
        if (gameOver || selectedRow < 0 || selectedCol < 0) return;
        const r = selectedRow;
        const c = selectedCol;
        if (givenMask[r][c]) return;
        startTimer();

        if (notesMode) {
            pushUndo(r, c);
            const prevNotes = new Set(notesGrid[r][c]);
            if (notesGrid[r][c].has(num)) notesGrid[r][c].delete(num);
            else notesGrid[r][c].add(num);

            undoStack.push({
                row: r, col: c,
                prevValue: userGrid[r][c], newValue: userGrid[r][c],
                prevNotes, newNotes: new Set(notesGrid[r][c]), wasNote: true
            });
            redoStack = [];
        } else {
            pushUndo(r, c);
            const oldValue = userGrid[r][c];
            if (oldValue === num) return;

            userGrid[r][c] = num;
            notesGrid[r][c].clear();

            undoStack.push({
                row: r, col: c,
                prevValue: oldValue, newValue: num,
                prevNotes: new Set(), newNotes: new Set(), wasNote: false
            });
            redoStack = [];

            if (num !== solutionGrid[r][c]) {
                mistakes++;
                updateStats();
                if (mistakes >= 3) { endGame(false); return; }
            } else { checkWin(); }
        }

        if (guideActive) renderGridWithGuide();
        else renderGrid();
    }

    function pushUndo(r, c) {}

    function undo() {
        if (gameOver || undoStack.length === 0) return;
        const action = undoStack.pop();
        const r = action.row;
        const c = action.col;

        if (action.wasNote) {
            redoStack.push({
                row: r, col: c, prevValue: userGrid[r][c], newValue: userGrid[r][c],
                prevNotes: new Set(notesGrid[r][c]), newNotes: action.prevNotes, wasNote: true
            });
            notesGrid[r][c] = action.prevNotes;
        } else {
            redoStack.push({
                row: r, col: c, prevValue: userGrid[r][c], newValue: action.newValue,
                prevNotes: new Set(notesGrid[r][c]), newNotes: new Set(), wasNote: false
            });
            userGrid[r][c] = action.prevValue;
        }

        if (guideActive) renderGridWithGuide();
        else renderGrid();
    }

    function redo() {
        if (gameOver || redoStack.length === 0) return;
        const action = redoStack.pop();
        const r = action.row;
        const c = action.col;

        if (action.wasNote) {
            undoStack.push({
                row: r, col: c, prevValue: userGrid[r][c], newValue: userGrid[r][c],
                prevNotes: new Set(notesGrid[r][c]), newNotes: action.prevNotes, wasNote: true
            });
            notesGrid[r][c] = action.newNotes;
        } else {
            undoStack.push({
                row: r, col: c, prevValue: userGrid[r][c], newValue: action.newValue,
                prevNotes: new Set(notesGrid[r][c]), newNotes: new Set(), wasNote: false
            });
            userGrid[r][c] = action.newValue;
        }

        if (guideActive) renderGridWithGuide();
        else renderGrid();
    }

    function eraseCell() {
        if (gameOver || selectedRow < 0 || selectedCol < 0) return;
        const r = selectedRow;
        const c = selectedCol;
        if (givenMask[r][c]) return;
        if (userGrid[r][c] === 0 && notesGrid[r][c].size === 0) return;

        pushUndo(r, c);
        const oldValue = userGrid[r][c];
        const oldNotes = new Set(notesGrid[r][c]);
        userGrid[r][c] = 0;
        notesGrid[r][c].clear();

        undoStack.push({
            row: r, col: c, prevValue: oldValue, newValue: 0,
            prevNotes: oldNotes, newNotes: new Set(), wasNote: false
        });
        redoStack = [];

        if (guideActive) renderGridWithGuide();
        else renderGrid();
    }

    function giveHint() {
        if (gameOver || selectedRow < 0 || selectedCol < 0) return;
        if (hintsLeft <= 0) return;
        const r = selectedRow;
        const c = selectedCol;
        if (givenMask[r][c]) return;
        if (userGrid[r][c] === solutionGrid[r][c]) return;

        startTimer();
        hintsLeft--;
        updateStats();

        pushUndo(r, c);
        const oldValue = userGrid[r][c];
        const oldNotes = new Set(notesGrid[r][c]);
        userGrid[r][c] = solutionGrid[r][c];
        notesGrid[r][c].clear();

        undoStack.push({
            row: r, col: c, prevValue: oldValue, newValue: solutionGrid[r][c],
            prevNotes: oldNotes, newNotes: new Set(), wasNote: false
        });
        redoStack = [];

        checkWin();
        if (guideActive) renderGridWithGuide();
        else renderGrid();
    }

    // ---- Apply Guide Move ----

    function applyGuideMove() {
        if (guideIndex < 0 || guideIndex >= guideHints.length) return;
        const hint = guideHints[guideIndex];

        if (hint.isPair) return;  // Can't auto-apply pair eliminations

        selectCell(hint.row, hint.col);
        startTimer();
        pushUndo(hint.row, hint.col);
        const oldValue = userGrid[hint.row][hint.col];
        const oldNotes = new Set(notesGrid[hint.row][hint.col]);

        userGrid[hint.row][hint.col] = hint.value;
        notesGrid[hint.row][hint.col].clear();

        undoStack.push({
            row: hint.row, col: hint.col, prevValue: oldValue, newValue: hint.value,
            prevNotes: oldNotes, newNotes: new Set(), wasNote: false
        });
        redoStack = [];

        // Check if correct (it should be from guide)
        checkWin();
        updateGuideDisplay();
    }

    // ---- Notes Mode Toggle ----

    function setNotesMode(on) {
        notesMode = on;
        notesBtn.classList.toggle('active', on);
        notesIndicator.textContent = on ? 'ON' : 'OFF';
    }

    // ---- Timer ----

    function startTimer() {
        if (timerStarted || gameOver) return;
        timerStarted = true;
        timerInterval = setInterval(() => {
            timerSeconds++;
            updateTimerDisplay();
        }, 1000);
    }

    function stopTimer() {
        if (timerInterval) { clearInterval(timerInterval); timerInterval = null; }
        timerStarted = false;
    }

    function updateTimerDisplay() {
        const mins = Math.floor(timerSeconds / 60).toString().padStart(2, '0');
        const secs = (timerSeconds % 60).toString().padStart(2, '0');
        timerDisplay.textContent = `⏱ ${mins}:${secs}`;
    }

    function updateStats() {
        mistakesDisplay.textContent = `Mistakes: ${mistakes} / 3`;
        hintsDisplay.textContent = `Hints left: ${hintsLeft}`;
        updateTimerDisplay();
    }

    // ---- Win/Loss Detection ----

    function checkWin() {
        for (let r = 0; r < 9; r++) {
            for (let c = 0; c < 9; c++) {
                if (userGrid[r][c] !== solutionGrid[r][c]) return;
            }
        }
        stopTimer();
        endGame(true);
    }

    function endGame(won) {
        gameOver = true;
        stopTimer();
        closeGuide();
        if (won) {
            const mins = Math.floor(timerSeconds / 60).toString().padStart(2, '0');
            const secs = (timerSeconds % 60).toString().padStart(2, '0');
            solvedStats.textContent = `Difficulty: ${difficultySelect.value} | Time: ${mins}:${secs} | Mistakes: ${mistakes}`;
            solvedOverlay.classList.remove('hidden');
        } else {
            gameOverOverlay.classList.remove('hidden');
        }
    }

    // ---- Keyboard Navigation ----

    document.addEventListener('keydown', (e) => {
        if (gameOver) return;

        const r = selectedRow;
        const c = selectedCol;

        if (r >= 0 && c >= 0) {
            switch (e.key) {
                case 'ArrowUp': e.preventDefault(); selectCell(Math.max(0, r - 1), c); return;
                case 'ArrowDown': e.preventDefault(); selectCell(Math.min(8, r + 1), c); return;
                case 'ArrowLeft': e.preventDefault(); selectCell(r, Math.max(0, c - 1)); return;
                case 'ArrowRight': e.preventDefault(); selectCell(r, Math.min(8, c + 1)); return;
            }
        }

        const num = parseInt(e.key);
        if (num >= 1 && num <= 9) { enterNumber(num); return; }

        if (e.key === 'Backspace' || e.key === 'Delete') { eraseCell(); return; }

        if ((e.key === 'n' || e.key === 'N') && !e.ctrlKey) { setNotesMode(!notesMode); return; }
        if (e.key === 'n' && e.ctrlKey) { e.preventDefault(); setNotesMode(!notesMode); return; }

        if (e.key === 'h' || e.key === 'H') { giveHint(); return; }
        if (e.key === 'g' || e.key === 'G') {
            if (guideActive) closeGuide();
            else openGuide();
            return;
        }

        if (e.key === 'Escape' && guideActive) { closeGuide(); return; }

        if (e.ctrlKey && (e.key === 'z' || e.key === 'Z')) { e.preventDefault(); undo(); return; }
        if ((e.ctrlKey && e.key === 'y') || (e.ctrlKey && e.shiftKey && (e.key === 'z' || e.key === 'Z'))) {
            e.preventDefault(); redo(); return;
        }
    });

    // ---- Event Listeners ----

    document.querySelectorAll('.number-pad button').forEach(btn => {
        btn.addEventListener('click', () => {
            const num = parseInt(btn.dataset.num);
            enterNumber(num);
        });
    });

    newGameBtn.addEventListener('click', initGame);
    undoBtn.addEventListener('click', undo);
    eraseBtn.addEventListener('click', eraseCell);
    notesBtn.addEventListener('click', () => setNotesMode(!notesMode));
    hintBtn.addEventListener('click', giveHint);

    // Guide panel
    guideBtn.addEventListener('click', () => {
        if (guideActive) closeGuide();
        else openGuide();
    });
    guideCloseBtn.addEventListener('click', closeGuide);
    guideNextBtn.addEventListener('click', () => {
        if (guideIndex >= guideHints.length - 1) {
            guideIndex = 0;  // Loop back
        } else {
            guideIndex++;
        }
        updateGuideDisplay();
    });
    guidePrevBtn.addEventListener('click', () => {
        if (guideIndex > 0) {
            guideIndex--;
            updateGuideDisplay();
        }
    });
    guideApplyBtn.addEventListener('click', applyGuideMove);

    // Theme selector
    themeSelect.addEventListener('change', (e) => setTheme(e.target.value));

    playAgainBtn.addEventListener('click', initGame);
    newPuzzleBtn.addEventListener('click', initGame);

    // ---- Init ----
    loadTheme();
    initGame();

})();
