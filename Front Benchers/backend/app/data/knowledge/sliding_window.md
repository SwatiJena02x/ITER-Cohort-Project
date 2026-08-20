# Sliding Window Technique

The sliding window technique maintains a "window" (subarray or substring) that expands or contracts as you iterate. It converts problems that seem to require checking all subarrays (O(n²)) into a single-pass O(n) solution.

## When to Use Sliding Window
- Finding the maximum/minimum sum subarray of size k
- Finding the longest substring with at most k distinct characters
- Finding the smallest subarray with sum >= target
- Any problem involving contiguous subarrays or substrings

## Types of Sliding Window

### Fixed-Size Window
The window size is constant (e.g., subarray of size k):
```python
window_sum = sum(nums[:k])
max_sum = window_sum
for i in range(k, len(nums)):
    window_sum += nums[i] - nums[i - k]  # slide: add new, remove old
    max_sum = max(max_sum, window_sum)
```

### Variable-Size Window
The window expands and contracts based on a condition:
```python
left = 0
for right in range(len(nums)):
    # expand window by including nums[right]
    while window_is_invalid():
        # contract window from left
        left += 1
```

## Complexity
- Time: O(n) — each element is added and removed from the window at most once
- Space: O(1) for sum-based problems, O(k) if tracking window contents

## Related, But Not True Sliding Window: Stock Problems
- Best Time to Buy and Sell Stock is often grouped near sliding window because both replace nested loops with a single O(n) pass — but it isn't a true sliding window, since there's no expanding/contracting window boundary, just one pointer moving forward while tracking the minimum price seen so far.
- If this problem's coach hints call it "single pass tracking min price" rather than "sliding window," that's the more precise name — use it when discussing this problem specifically.
- No need for nested loops to compare every buy/sell pair either way — the underlying insight is the same "remember what you've seen" idea as sliding window, just without an actual window.

## Common Mistakes
- Recalculating the entire window from scratch instead of incrementally updating
- Forgetting to handle the initial window setup
- Not contracting the window when it becomes invalid
