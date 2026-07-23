# Coding / DSA Prep

> Some tier-1s (Google, Amazon, Atlassian) run a DSA round even for DevOps/SRE. Others do **scripting + troubleshooting** instead. Prepare both, weighted to the companies on your list.

---

## WHAT TO EXPECT BY COMPANY TYPE
- **FAANG-tier (Google, Amazon, Meta):** real DSA — arrays, strings, hashmaps, trees, graphs, sometimes DP. LeetCode Easy→Medium.
- **Salesforce-tier / product cos:** lighter DSA or practical scripting.
- **SRE-specific:** scripting (parse logs, process data), Linux debugging, sometimes "code a rate limiter / LRU cache."
- **Startups/unicorns (Razorpay, CRED, PhonePe):** practical coding + system design; less pure DSA.

Since you're strong in **Python**, use it for coding rounds.

---

## PYTHON PATTERNS TO KNOW COLD
```python
# Hashmap counting
from collections import Counter, defaultdict
c = Counter(items)

# Two pointers
l, r = 0, len(a)-1
while l < r: ...

# Sliding window
window = 0
for r in range(len(a)):
    window += a[r]
    while invalid: window -= a[l]; l += 1

# BFS (queue)
from collections import deque
q = deque([start]); seen = {start}
while q:
    node = q.popleft()
    for nb in graph[node]:
        if nb not in seen: seen.add(nb); q.append(nb)

# DFS (recursion or stack)
def dfs(node, seen):
    seen.add(node)
    for nb in graph[node]:
        if nb not in seen: dfs(nb, seen)

# Sort with key
items.sort(key=lambda x: (x[1], -x[0]))

# Heap
import heapq
heapq.heappush(h, x); heapq.heappop(h)  # min-heap
```

## TOP TOPICS (priority order for DevOps/SRE)
1. **Hashmaps / sets** — counting, dedup, lookups (most common)
2. **Strings** — parsing, manipulation (log-processing flavored)
3. **Arrays / two-pointer / sliding window**
4. **Stacks / queues** — incl. valid-parentheses, LRU cache
5. **Trees** — traversal, BFS/DFS
6. **Graphs** — BFS/DFS, dependency resolution (topological sort — very DevOps-relevant)
7. **Heaps** — top-K, scheduling
8. (Lighter) Binary search, basic DP

## SRE / SCRIPTING-STYLE PROBLEMS (high-yield for you)
- Parse a log file, count errors per hour / find top-N IPs by request count.
- Implement an **LRU cache** (dict + doubly-linked list, or `OrderedDict`).
- Implement a **rate limiter** (token bucket / sliding window).
- **Topological sort** of service dependencies (detect cycles).
- Merge/monitor intervals (uptime windows).
- Parse config/JSON and validate/transform.
- Find files > X size / dedup by hash (mirror your stale-VM/cleanup work).

## PRACTICE PLAN
- **~40–60 LeetCode** problems (mostly Easy + Medium) across the topics above. Blind 75 is a good curated list.
- Do **1–2/day**, timed (25–35 min). Review the optimal solution even if you solve it.
- Practice **talking while coding** — narrate approach, complexity, edge cases.
- Always state **time & space complexity** at the end.

## INTERVIEW TECHNIQUE
1. Restate the problem + ask clarifying questions (input size, edge cases, constraints).
2. State a brute-force approach, then optimize.
3. Talk through the approach BEFORE coding — get buy-in.
4. Code cleanly; handle edge cases (empty, nulls, duplicates).
5. Test with an example, trace through.
6. State complexity.

## COMPLEXITY QUICK REF
- Hashmap lookup: O(1) avg · Sort: O(n log n) · BFS/DFS: O(V+E) · Heap ops: O(log n) · Binary search: O(log n)
