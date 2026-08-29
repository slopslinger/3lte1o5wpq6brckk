#!/usr/bin/env python3
"""
Independent Sudoku Solver & Puzzle Validator

This script:
1. Generates puzzles using the game's algorithm (replicated here)
2. Solves each puzzle independently using backtracking
3. Verifies each puzzle has EXACTLY one unique solution
4. Tests all 4 difficulty levels with multiple puzzles each
5. Reports pass/fail for every puzzle

Run from /home/goober/Projects/sudoku-game/
"""

import random
import time


# ============================================================
# Sudoku Generator (replicated from js/main.js)
# ============================================================

def is_valid(grid, row, col, num):
    """Check if placing num at grid[row][col] is valid."""
    # Row check
    for c in range(9):
        if c != col and grid[row][c] == num:
            return False
    # Column check
    for r in range(9):
        if r != row and grid[r][col] == num:
            return False
    # 3x3 box check
    start_row, start_col = (row // 3) * 3, (col // 3) * 3
    for r in range(start_row, start_row + 3):
        for c in range(start_col, start_col + 3):
            if (r != row or c != col) and grid[r][c] == num:
                return False
    return True


def solve_sudoku(grid, max_solutions=2):
    """
    Solve sudoku, returning list of solutions found (up to max_solutions).
    Returns count of solutions without modifying original grid.
    """
    solutions = []

    def backtrack(g):
        if len(solutions) >= max_solutions:
            return
        for r in range(9):
            for c in range(9):
                if g[r][c] == 0:
                    for num in range(1, 10):
                        if is_valid(g, r, c, num):
                            g[r][c] = num
                            backtrack(g)
                            if len(solutions) >= max_solutions:
                                g[r][c] = 0
                                return
                            g[r][c] = 0
                    return  # No valid number found for this cell
        solutions.append([row[:] for row in g])

    # Work on a copy
    work_grid = [row[:] for row in grid]
    backtrack(work_grid)
    return solutions


def generate_full_solution():
    """Generate a complete valid Sudoku solution."""
    grid = [[0] * 9 for _ in range(9)]

    # Fill diagonal boxes first (they don't overlap, so always safe)
    for box in range(3):
        nums = list(range(1, 10))
        random.shuffle(nums)
        idx = 0
        for r in range(box * 3, (box + 1) * 3):
            for c in range(box * 3, (box + 1) * 3):
                grid[r][c] = nums[idx]
                idx += 1

    # Solve the rest
    def fill(grid):
        for r in range(9):
            for c in range(9):
                if grid[r][c] == 0:
                    nums = list(range(1, 10))
                    random.shuffle(nums)
                    for num in nums:
                        if is_valid(grid, r, c, num):
                            grid[r][c] = num
                            if fill(grid):
                                return True
                            grid[r][c] = 0
                    return False
        return True

    fill(grid)
    return grid


def generate_puzzle(difficulty='easy'):
    """Generate a puzzle with the given difficulty. Returns (puzzle, solution)."""
    removals = {
        'easy': 40,
        'medium': 48,
        'hard': 54,
        'expert': 58,
    }

    n_removals = removals.get(difficulty, 45)
    solution = generate_full_solution()
    puzzle = [row[:] for row in solution]

    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)

    removed = 0
    for r, c in cells:
        if removed >= n_removals:
            break
        backup = puzzle[r][c]
        puzzle[r][c] = 0
        # Verify unique solution after removal
        sol_count = solve_sudoku(puzzle, max_solutions=2)
        if len(sol_count) != 1:
            puzzle[r][c] = backup  # Put it back, too many solutions
        else:
            removed += 1

    return puzzle, solution


# ============================================================
# Solver (independent of generator)
# ============================================================

def solve_puzzle(puzzle):
    """Solve a puzzle from scratch. Returns solution or None."""
    grid = [row[:] for row in puzzle]

    def find_empty(g):
        for r in range(9):
            for c in range(9):
                if g[r][c] == 0:
                    return (r, c)
        return None

    def solve(g):
        pos = find_empty(g)
        if not pos:
            return True  # Puzzle solved!
        r, c = pos
        for num in range(1, 10):
            if is_valid(g, r, c, num):
                g[r][c] = num
                if solve(g):
                    return True
                g[r][c] = 0
        return False

    if solve(grid):
        return grid
    return None


def verify_sudoku_rules(solution):
    """Verify a complete solution follows all Sudoku rules."""
    # Check each row has 1-9
    for r in range(9):
        if set(solution[r]) != set(range(1, 10)):
            return False, f"Row {r} missing numbers: {set(range(1,10)) - set(solution[r])}"

    # Check each column has 1-9
    for c in range(9):
        col = [solution[r][c] for r in range(9)]
        if set(col) != set(range(1, 10)):
            return False, f"Column {c} missing numbers: {set(range(1,10)) - set(col)}"

    # Check each 3x3 box has 1-9
    for br in range(3):
        for bc in range(3):
            box = []
            for r in range(br*3, (br+1)*3):
                for c in range(bc*3, (bc+1)*3):
                    box.append(solution[r][c])
            if set(box) != set(range(1, 10)):
                return False, f"Box ({br},{bc}) missing: {set(range(1,10)) - set(box)}"

    return True, "Valid!"


def print_grid(grid, title=""):
    """Pretty-print a Sudoku grid."""
    if title:
        print(f"\n{title}")
    for r, row in enumerate(grid):
        if r in [3, 6]:
            print("------+-------+------")
        line = ""
        for c, val in enumerate(row):
            sym = str(val) if val != 0 else "."
            line += f" {sym} "
            if c % 3 == 2 and c < 8:
                line += "|"
        print(line)


# ============================================================
# Test Suite
# ============================================================

def run_tests(num_puzzles=5):
    """Generate and solve multiple puzzles at each difficulty."""
    difficulties = ['easy', 'medium', 'hard', 'expert']
    results = {}
    total_tests = 0
    total_passed = 0

    print("=" * 60)
    print("SUDOKU PUZZLE VALIDATION SUITE")
    print("=" * 60)
    print(f"Testing {num_puzzles} puzzles per difficulty level")
    print()

    for diff in difficulties:
        print("-" * 50)
        print(f"Difficulty: {diff.upper()}")
        print("-" * 50)

        diff_results = []
        rng_seed = random.randint(1, 999999)
        random.seed(rng_seed)

        for i in range(num_puzzles):
            puzzle_id = f"{diff}_{i+1}"
            total_tests += 1

            # Generate puzzle
            start_t = time.time()
            puzzle, original_solution = generate_puzzle(diff)
            gen_time = time.time() - start_t

            # Count given clues
            given_count = sum(1 for r in range(9) for c in range(9) if puzzle[r][c] != 0)
            empty_count = 81 - given_count

            # Test 1: Solve independently
            solve_start = time.time()
            my_solution = solve_puzzle(puzzle)
            solve_time = time.time() - solve_start

            solved = my_solution is not None

            if solved:
                # Test 2: Verify solution follows Sudoku rules
                valid, reason = verify_sudoku_rules(my_solution)

                # Test 3: Match original generator's solution
                matches_original = (my_solution == original_solution)

                # Test 4: Verify uniqueness (at most 1 solution)
                uniqueness_check = solve_puzzle(puzzle) is not None
                all_solutions = solve_sudoku(puzzle, max_solutions=2)
                unique = len(all_solutions) == 1

                passed = solved and valid and matches_original and unique

                if passed:
                    total_passed += 1
                    status = "✅ PASS"
                else:
                    status = f"❌ FAIL (solved={solved}, valid={valid}, match={matches_original}, unique={unique})"

                # Only print first puzzle in detail
                if i == 0:
                    print(f"\n  Puzzle #{i+1}: {puzzle_id} (seed={rng_seed})")
                    print(f"    Given clues: {given_count} | Empty: {empty_count}")
                    print(f"    Gen time: {gen_time:.3f}s | Solve time: {solve_time:.4f}s")
                    print_grid(puzzle, "  PUZZLE:")
                    print_grid(my_solution, "  SOLUTION (found by independent solver):")
                    print(f"    Rules valid: {reason}")
                    print(f"    Matches generator solution: {matches_original}")
                    print(f"    Unique solution: {unique} ({len(all_solutions)} found)")

                diff_results.append({
                    'id': puzzle_id,
                    'given': given_count,
                    'solved': solved,
                    'valid': valid,
                    'matches': matches_original,
                    'unique': unique,
                    'passed': passed,
                    'gen_time': gen_time,
                    'solve_time': solve_time,
                })

            else:
                status = "❌ UNSOLVABLE"
                if i == 0:
                    print(f"\n  Puzzle #{i+1}: {puzzle_id} — ❌ COULD NOT SOLVE!")
                    print_grid(puzzle, "  Unsolved puzzle:")
                diff_results.append({
                    'id': puzzle_id,
                    'given': given_count,
                    'solved': False,
                    'passed': False,
                })

            if i < 3:  # Show first few results
                print(f"    Puzzle {puzzle_id}: {status}")
            elif not passed and i == 3:
                print(f"    ... ({total_tests - total_passed} failures so far)")

        diff_summary = sum(1 for d in diff_results if d['passed']) / len(diff_results) * 100
        avg_solve = sum(d.get('solve_time', 0) for d in diff_results) / len(diff_results)
        print(f"\n  {diff.upper()} Summary: {sum(1 for d in diff_results if d['passed'])}/{num_puzzles} passed ({diff_summary:.0f}%)")
        print(f"    Avg solve time: {avg_solve:.4f}s | Avg clues: {sum(d['given'] for d in diff_results)//num_puzzles}")

        results[diff] = diff_results

    # Final Report
    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)

    for diff in difficulties:
        r = results[diff]
        passed = sum(1 for x in r if x['passed'])
        total = len(r)
        avg_solve = sum(x.get('solve_time', 0) for x in r) / total
        avg_clues = sum(x['given'] for x in r) // total

        bar = "█" * passed + "░" * (total - passed)
        print(f"  {diff.upper():8s} │{bar}│ {passed}/{total} │ Avg solve: {avg_solve:.4f}s │ Avg clues: {avg_clues}")

    overall_pct = total_passed / total_tests * 100
    print(f"\n  OVERALL: {total_passed}/{total_tests} ({overall_pct:.0f}%)")

    if total_passed == total_tests:
        print("  🎉 ALL PUZZLES VALID AND SOLVABLE!")
    else:
        print(f"  ⚠️ {total_tests - total_passed} puzzles failed validation")

    return results


if __name__ == '__main__':
    random.seed(42)  # Reproducible test run
    run_tests(num_puzzles=10)
