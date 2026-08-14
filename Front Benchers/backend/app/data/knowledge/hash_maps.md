# Hash Maps (Dictionaries)

A hash map (or dictionary in Python) stores key-value pairs and provides O(1) average-case lookup, insertion, and deletion. It is one of the most important data structures in DSA.

## When to Use a Hash Map
- When you need to quickly check if an element exists (membership testing)
- When you need to store and retrieve values by a key
- When you want to count occurrences of elements
- When you need to find complements or pairs (e.g., Two Sum)
- When you need O(1) lookups instead of O(n) linear scans

## Common Patterns
- **Two Sum Pattern**: For each element, check if its complement (target - element) already exists in the hash map. This reduces O(n²) brute force to O(n).
- **Frequency Counting**: Use a hash map to count occurrences of each element. Useful for anagrams, duplicates, and majority element problems.
- **Index Tracking**: Store the index of each element as you iterate, so you can reference it later without re-scanning.

## Python Implementation
```python
seen = {}  # empty hash map
seen[key] = value  # insert O(1)
if key in seen:    # lookup O(1)
value = seen[key]  # access O(1)
```

## Complexity
- Time: O(1) average for insert, lookup, delete
- Space: O(n) where n is the number of stored elements
- Worst case: O(n) per operation due to hash collisions, but this is rare

## Common Mistakes
- Forgetting that hash maps use O(n) extra space
- Using a list scan when a hash map would give O(1) lookup
- Not handling the case where a key doesn't exist (use `.get()` or `in` check)
