# Sorting Approaches

Sorting arranges elements in a specific order. While sorting is a powerful tool, it is often suboptimal when a hash-based approach exists.

## When Sorting is Appropriate
- When the problem explicitly requires sorted output
- When two pointers on sorted data gives O(n) post-sort
- When checking if two collections are equal (sorted comparison)
- When grouping or clustering elements

## When Sorting is Overkill
- **Anagram detection**: Sorting both strings is O(n log n), but frequency counting is O(n)
- **Finding duplicates**: Sorting then scanning is O(n log n), but a set gives O(n)
- **Two Sum**: Sorting loses original indices; a hash map is O(n)

## Python Sorting
```python
sorted_list = sorted(nums)    # returns new sorted list O(n log n)
nums.sort()                    # sorts in-place O(n log n)
sorted(s)                     # works on strings too (returns list of chars)
```

## Complexity
- Time: O(n log n) for comparison-based sorting
- Space: O(n) for Python's Timsort (merges require extra space)

## Sorting vs Hash Map

| Approach | Time | Space | Preserves Order/Indices |
|----------|------|-------|------------------------|
| Sorting | O(n log n) | O(n) | No |
| Hash Map | O(n) | O(n) | Yes (with index tracking) |
| Set | O(n) | O(n) | No |

## Common Mistakes
- Sorting when a hash-based approach is faster
- Forgetting that sorting doesn't preserve original indices
- Using sorted() on every comparison instead of sorting once
