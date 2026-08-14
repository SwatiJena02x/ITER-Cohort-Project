# Two Pointer Technique

The two pointer technique uses two pointers (indices) to traverse a data structure, typically from opposite ends or at different speeds. It reduces nested loops to a single pass.

## When to Use Two Pointers
- When working with sorted arrays or linked lists
- When looking for pairs that satisfy a condition
- When you need to compare elements from both ends
- When removing duplicates in-place

## Common Patterns

### Opposite Direction (Converging)
Start one pointer at the beginning and one at the end, move them toward each other:
```python
left, right = 0, len(nums) - 1
while left < right:
    # process nums[left] and nums[right]
    # move left forward or right backward
```
Used for: Two Sum II – Input Array Is Sorted, Container With Most Water, Valid Palindrome

### Same Direction (Fast/Slow)
Both pointers start at the beginning, one moves faster:
```python
slow, fast = 0, 0
while fast < len(nums):
    # fast explores, slow tracks position
```
Used for: Remove Duplicates, Linked List Cycle Detection

## Complexity
- Time: O(n) — each pointer traverses the array at most once
- Space: O(1) — no extra data structures needed

## Two Pointers vs Hash Map
- Two pointers: O(n) time, O(1) space — but requires sorted input
- Hash map: O(n) time, O(n) space — works on unsorted input
- If the array is already sorted, two pointers is preferred (no extra space)
- This does NOT apply to the standard/unsorted 'Two Sum' problem (LeetCode #1) — that requires a hash map since the input isn't sorted. Two pointers only applies when you're explicitly given a sorted array.

## Common Mistakes
- Using two pointers on unsorted arrays where ordering matters
- Not handling the case where both pointers point to the same element
- Off-by-one errors in the while condition (use `<` not `<=` to avoid using same element twice)
- Confusing this with the unsorted Two Sum problem, where a hash map is the correct optimal approach instead.
