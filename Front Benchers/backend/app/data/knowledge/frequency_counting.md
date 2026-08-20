# Frequency Counting

Frequency counting is a technique where you count how many times each element appears in a collection. It is fundamental for problems involving anagrams, duplicates, and character distributions.

## When to Use Frequency Counting
- Checking if two strings are anagrams (same character frequencies)
- Finding the most/least frequent element
- Checking if a string has all unique characters
- Grouping elements by their frequency

## Approaches

### Using collections.Counter
```python
from collections import Counter
count = Counter(s)  # counts each character
# Counter({'a': 3, 'b': 2, 'c': 1})
```

### Using a Dictionary
```python
counts = {}
for char in s:
    counts[char] = counts.get(char, 0) + 1
```

### Using a Fixed Array (for lowercase letters)
```python
freq = [0] * 26
for char in s:
    freq[ord(char) - ord('a')] += 1
```

## Anagram Detection
Two strings are anagrams if and only if they have identical character frequency distributions:
- **O(n log n)**: Sort both strings and compare — works but suboptimal
- **O(n)**: Count character frequencies and compare — optimal

## Complexity
- Time: O(n) to count all elements
- Space: O(k) where k is the number of unique elements (bounded by alphabet size for strings)

## Common Mistakes
- Using sorting (O(n log n)) when counting (O(n)) would be faster
- Not checking length equality first — if lengths differ, they can't be anagrams
- Forgetting to handle case sensitivity
