# Sets

A set is an unordered collection of unique elements. In Python, sets provide O(1) average-case membership testing, making them ideal for duplicate detection and fast lookups.

## When to Use a Set
- When you need to check if an element has been seen before
- When you need to remove duplicates from a collection
- When you need fast membership testing without storing values
- When you don't need key-value pairs (use a hash map for that)

## Common Patterns
- **Duplicate Detection**: Add elements to a set as you iterate. If an element is already in the set, it's a duplicate. This is O(n) vs O(n²) for nested loops.
- **Two Sum with Boolean Return**: If you only need to know whether a pair exists (not indices), use a set to store seen numbers and check for complements.
- **Intersection/Union**: Sets support mathematical operations like intersection (`&`), union (`|`), and difference (`-`).

## Python Implementation
```python
seen = set()       # empty set
seen.add(element)  # add O(1)
if element in seen: # check O(1)
seen.remove(element) # remove O(1)
```

## Complexity
- Time: O(1) average for add, check, remove
- Space: O(n) where n is the number of stored elements

## Set vs Hash Map
- Use a **set** when you only need to check existence (no values needed)
- Use a **hash map** when you need to associate values with keys (e.g., storing indices)

## Common Mistakes
- Using `len(nums) != len(set(nums))` works for Contains Duplicate but creates the entire set upfront. An early-exit loop with a set is more efficient for large inputs.
- Confusing sets with lists — sets are unordered and don't support indexing.
