#!/usr/bin/env python3
"""Solve NYT expert puzzle + validation rounds."""
import time, random

def ok(g, r, c, n):
    for i in range(9):
        if g[r][i] == n or g[i][c] == n: return False
    br, bc = (r//3)*3, (c//3)*3
    for i in range(br, br+3):
        for j in range(bc, bc+3):
            if g[i][j] == n: return False
    return True

def solve(g):
    best = None; best_n = 10
    for r in range(9):
        for c in range(9):
            if g[r][c] == 0:
                n = sum(1 for v in range(1,10) if ok(g,r,c,v))
                if n < best_n: best_n = n; best = (r,c)
    if not best: return True
    r, c = best
    for v in range(1, 10):
        if ok(g, r, c, v):
            g[r][c] = v
            if solve(g): return True
            g[r][c] = 0
    return False

def count_sols(g, limit=2):
    cnt = [0]
    def bt(g):
        if cnt[0] >= limit: return
        best = None; best_n = 10
        for r in range(9):
            for c in range(9):
                if g[r][c] == 0:
                    n = sum(1 for v in range(1,10) if ok(g,r,c,v))
                    if n < best_n: best_n = n; best = (r,c)
        if not best: cnt[0] += 1; return
        r, c = best
        for v in range(1, 10):
            if ok(g, r, c, v):
                g[r][c] = v; bt(g); g[r][c] = 0
    bt([row[:] for row in g])
    return cnt[0]

def pprint(g, t=""):
    if t: print(f"\n{t}")
    for i, row in enumerate(g):
        if i in [3,6]: print("------+-------+------")
        line = ""
        for j, v in enumerate(row):
            line += f" {v or '.'} " + ("|" if j%3==2 and j<8 else "")
        print(line)

# ============================================================
print("=" * 60)
print("NYT EXPERT PUZZLE — Barron's Screenshot")
print("=" * 60)

# Manual transcription of the BLACK given clues only.
# The blue numbers are user entries that may be wrong.
nyt = [
    [0, 0, 0, 3, 2, 4, 0, 0, 0],
    [0, 0, 9, 7, 4, 5, 0, 0, 0],
    [2, 0, 0, 0, 9, 6, 7, 0, 3],
    [0, 0, 4, 0, 0, 3, 8, 2, 7],
    [0, 1, 0, 0, 0, 7, 0, 4, 9],
    [0, 0, 0, 0, 8, 4, 0, 0, 0],
    [4, 5, 0, 0, 7, 8, 0, 0, 0],
    [7, 0, 6, 4, 0, 9, 0, 8, 5],
    [0, 0, 0, 5, 0, 1, 0, 7, 4],
]

given = sum(1 for r in range(9) for c in range(9) if nyt[r][c] != 0)
print(f"\nGiven clues: {given}")
pprint(nyt, "ORIGINAL GIVENS:")

t0 = time.time()
nyt_sol = [row[:] for row in nyt]
if solve(nyt_sol):
    t1 = time.time()-t0
    pprint(nyt_sol, f"SOLVED ({t1*1000:.0f}ms):")
    n = count_sols(nyt, 2)
    print(f"\nSolutions found: {n} (unique={n==1})")

else:
    print("❌ No solution — transcription may be wrong")

# ============================================================
print("\n" + "=" * 60)
print("VALIDATION ROUND 3 — 10 per difficulty")
print("=" * 60)

random.seed(int(time.time()))

def gen_full():
    grid = [[0]*9 for _ in range(9)]
    for box in range(3):
        nums = list(range(1,10)); random.shuffle(nums); idx = 0
        for r in range(box*3,(box+1)*3):
            for c in range(box*3,(box+1)*3):
                grid[r][c] = nums[idx]; idx += 1
    def fill(g):
        best = None; best_n = 10
        for r in range(9):
            for c in range(9):
                if g[r][c] == 0:
                    n = sum(1 for v in range(1,10) if ok(g,r,c,v))
                    if n < best_n: best_n = n; best = (r,c)
        if not best: return True
        r, c = best
        nums = list(range(1,10)); random.shuffle(nums)
        for v in nums:
            if ok(g,r,c,v):
                g[r][c] = v
                if fill(g): return True
                g[r][c] = 0
        return False
    fill(grid); return grid

def gen_puzzle(diff):
    remap = {'easy':40,'medium':48,'hard':54,'expert':58}
    sol = gen_full(); puz = [row[:] for row in sol]
    cells = [(r,c) for r in range(9) for c in range(9)]
    random.shuffle(cells); removed = 0
    for r, c in cells:
        if removed >= remap.get(diff,40): break
        bak = puz[r][c]; puz[r][c] = 0
        if count_sols(puz,2) != 1: puz[r][c] = bak
        else: removed += 1
    return puz, sol

total_ok = 0
for diff in ['easy','medium','hard','expert']:
    passed = 0
    for _ in range(10):
        puz, sol = gen_puzzle(diff)
        w = [row[:] for row in puz]
        ok_flag = solve(w)
        unique = count_sols(puz,2) == 1 if ok_flag else False
        match = (w == sol) if ok_flag else False
        rules = all(set(w[r])==set(range(1,10)) for r in range(9)) if ok_flag else False
        if ok_flag and unique and match and rules: passed += 1
    total_ok += passed
    print(f"  {diff.upper():8s}: {passed}/10")

print(f"\nRound 3: {total_ok}/40 {'🎉 ALL PASS' if total_ok==40 else '⚠️ FAILURES'}")
